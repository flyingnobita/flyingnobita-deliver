#!/usr/bin/env python3
"""Delivery's deterministic JSON boundary. Host evidence is supplied by the caller."""
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone


def require(condition, message):
    if not condition:
        raise ValueError(message)


def observed_at():
    return datetime.now(timezone.utc).isoformat()


def select_hosts(data):
    hosts = ('herdr', 'paseo', 'orca')
    require(all(data.get(h) in ('confirmed', 'absent') for h in hosts),
            'broken or ambiguous host identity; inspect failed check')
    present = [h for h in hosts if data[h] == 'confirmed']
    require(present, 'no confirmed host')
    if len(present) > 1:
        require(data.get('choice') in present, 'multiple hosts confirmed; choose a confirmed host')
        return {'host': data['choice']}
    require(data.get('choice', present[0]) == present[0], 'chosen host is absent')
    return {'host': present[0]}


def select(data):
    # Retain the original two-host CLI for already-deployed adapter callers.
    # Updated callers use select-host, which requires explicit Orca evidence.
    return select_hosts({'orca': 'absent', **data})


def concurrency(value):
    require(type(value) is int and value > 0, 'concurrency must be a positive integer')
    return value


PURPOSES = {
    'delivery': (('brief', 'plan', 'seams'), ('planner', 'implementer', 'reviewer', 'qa')),
    'setup': (('setup',), ('smoke',)),
    'review-only': (('review',), ('reviewer',)),
    'review-repair': (('review', 'seams'), ('reviewer', 'implementer')),
}


def authorize_role(record, role):
    purpose = record.get('purpose', 'delivery')
    fields, roles = PURPOSES[purpose]
    require(role in roles, 'role is outside run purpose')
    if purpose == 'delivery' and role == 'planner':
        return
    require(all(record['approved'].get(k) for k in fields),
            'approved plan and seams or purpose-specific authorization required')


def migrate_orca(data):
    """Preview only: retain every legacy value and require decisions for changed semantics."""
    legacy = data['legacy']
    require(isinstance(legacy, dict), 'legacy config must be an object')
    legacy_roles = legacy.get('roles', {})
    require(isinstance(legacy_roles, dict), 'legacy roles must be a table')
    roles = {}
    for role in ('implementer', 'reviewer'):
        old = legacy_roles.get(role)
        require(old is None or isinstance(old, dict), 'legacy role must be a table')
        if old:
            require(isinstance(old.get('agent'), str) and old['agent'], 'legacy role needs agent')
            roles[role] = {'harness': old['agent']}
            roles[role].update({k: old[k] for k in ('model', 'effort') if k in old})
    setup = legacy.get('worktree_setup', 'run')
    require(setup in ('run', 'skip', 'inherit'), 'invalid worktree setup policy')
    return {'config': {'delivery': {'max_workers': concurrency(legacy.get('max_workers', 4)),
                                    'human_schedule': 'normal', 'landing': 'leave'},
                       'hosts': {'orca': {'worktree_setup': setup, 'roles': roles}}},
            'legacy': legacy,
            'missing_roles': [role for role in ('planner', 'implementer', 'reviewer', 'qa') if role not in roles],
            'decisions': [
                'Choose planner and QA profiles; validate all effective Orca launch settings.',
                'Keep the initiating orchestrator; old orchestrator/fixer profiles remain in legacy only.',
                'Landing stays leave until explicitly chosen; legacy local merge is not PR merge authority.',
                'Use the default branch unless a different base is explicitly approved for this run.',
                'Questions unresolved by the approved plan block; timeouts never authorize assumptions.',
                'Review legacy sandbox/network/unknown fields; do not modify host permissions automatically.'
            ]}


def profiles(data):
    layers = [data.get(key, {}) for key in ('defaults', 'project', 'run')]
    result = {}
    sessions = data.get('opencode_sessions', {})
    require(isinstance(sessions, dict), 'OpenCode session bindings must be an object')
    roles = {'planner', 'implementer', 'reviewer', 'qa'}
    require(all(isinstance(layer, dict) and set(layer) <= roles for layer in layers),
            'unknown delivery role')
    for role in set().union(*layers):
        profile = {}
        for layer in layers:
            profile.update(layer.get(role, {}))
        require(set(profile) <= {'harness', 'model', 'effort', 'mode', 'provider', 'features'},
                'unsupported profile field')
        harness, model, effort, mode = (profile[k] for k in ('harness', 'model', 'effort', 'mode'))
        require(harness in ('codex', 'claude', 'agy', 'pi', 'omp', 'opencode'), 'unsupported harness')
        require(isinstance(model, str) and model and not model.startswith('-'), 'invalid model')
        require(not profile.get('provider') and not profile.get('features'),
                'provider/features require a verified native mapping; cannot drop settings')
        if harness == 'claude':
            require(effort in ('low', 'medium', 'high', 'xhigh', 'max'), 'unsupported Claude effort')
            require(mode in ('plan', 'auto', 'manual', 'dontAsk', 'acceptEdits', 'bypassPermissions'),
                    'unsupported Claude permission mode')
            argv = ['--model', model, '--effort', effort, '--permission-mode', mode]
        elif harness == 'pi':
            require(effort in ('off', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'),
                    'unsupported Pi thinking level')
            require(mode == 'default', 'unsupported Pi mode; use default')
            argv = ['--model', model, '--thinking', effort]
        elif harness == 'omp':
            require(effort in ('off', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'auto'),
                    'unsupported omp thinking level')
            require(mode in ('default', 'always-ask', 'always-ask-cached', 'write', 'yolo'),
                    'unsupported omp approval mode')
            argv = ['--model', model, '--thinking', effort]
            if mode != 'default':
                argv += ['--approval-mode', mode]
        elif harness == 'opencode':
            require(re.fullmatch(r'[^\s#/]+/[^\s#]+', model),
                    'OpenCode model must be provider/model without a variant suffix')
            require(effort in ('minimal', 'low', 'medium', 'high', 'xhigh', 'max'),
                    'unsupported OpenCode model variant')
            require(mode == 'default',
                    'unsupported OpenCode mode; preserve native approvals with default')
            # V2 Mini has no Herdr reporter. Bind a native session before full-TUI startup.
            argv = None
            provider, model_id = model.split('/', 1)
            session_request = {'model': {'providerID': provider, 'id': model_id, 'variant': effort}}
            if role in sessions:
                binding = sessions[role]
                require(isinstance(binding, dict) and set(binding) == {'directory', 'session'},
                        'OpenCode binding requires expected directory and native session')
                directory = binding['directory']
                require(isinstance(directory, str) and Path(directory).is_absolute()
                        and Path(directory).is_dir(), 'OpenCode worktree directory must exist and be absolute')
                session = binding['session']
                require(isinstance(session, dict) and
                        session.get('model') == session_request['model'],
                        'OpenCode session model/variant differs from requested profile')
                require(isinstance(session.get('location'), dict), 'OpenCode native session location required')
                location = session['location'].get('directory')
                require(isinstance(location, str) and Path(location).is_absolute()
                        and Path(location).resolve() == Path(directory).resolve(),
                        'OpenCode session belongs to another directory')
                session_id = session.get('id')
                require(isinstance(session_id, str) and re.fullmatch(r'ses_[A-Za-z0-9]+', session_id),
                        'invalid OpenCode native session ID')
                argv = ['--session', session_id]
        elif harness == 'agy':
            require(effort in ('low', 'medium', 'high', 'xhigh', 'max'), 'unsupported agy effort')
            require(mode in ('plan', 'auto', 'accept-edits', 'dangerously-skip-permissions'),
                    'unsupported agy permission mode')
            argv = ['--model', model, '--effort', effort]
            argv += (['--dangerously-skip-permissions'] if mode == 'dangerously-skip-permissions'
                     else ['--mode', mode])
        else:
            require(effort in ('low', 'medium', 'high', 'xhigh'), 'unsupported Codex effort')
            require(mode in ('full-access', 'auto', 'read-only'), 'unsupported Codex permission mode')
            argv = ['--model', model, '-c', 'model_reasoning_effort=' + json.dumps(effort)]
            if mode == 'full-access':
                argv += ['--dangerously-bypass-approvals-and-sandbox']
            else:
                argv += ['--sandbox', 'read-only' if mode == 'read-only' else 'workspace-write',
                         '--ask-for-approval', 'on-request']
        result[role] = {'profile': profile, 'argv': argv, 'availability_verified': False}
        if harness == 'opencode':
            result[role]['session_request'] = session_request
    require(all(role in result and result[role]['profile']['harness'] == 'opencode' for role in sessions),
            'OpenCode session binding has no matching OpenCode role')
    return result


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', value),
            'invalid identifier')
    return value


def orca_task(data):
    packet = data['packet']
    require(isinstance(packet, dict), 'structured task packet required')
    fields = ('target', 'change', 'constraints', 'ownership', 'acceptance')
    for field in fields:
        value = packet.get(field)
        require(isinstance(value, str) and value.strip() and
                not re.fullmatch(r'<[^>]+>', value.strip()), 'complete task field required: ' + field)
    profile = packet.get('profile')
    require(isinstance(profile, dict) and set(profile) <= {'harness', 'model', 'effort'}
            and isinstance(profile.get('harness'), str) and profile['harness'].strip(),
            'selected native profile required')
    for field in ('model', 'effort'):
        require(field not in profile or isinstance(profile[field], str) and profile[field].strip(),
                'invalid native profile field')
    require(not profile.get('effort') or profile.get('model'), 'effort requires explicit model')
    path = packet.get('report_path')
    require(isinstance(path, str) and Path(path).is_absolute(), 'absolute report path required')
    commands = packet.get('verification_commands')
    require(isinstance(commands, list) and commands and all(
        isinstance(argv, list) and argv and all(isinstance(arg, str) and arg for arg in argv)
        for argv in commands), 'explicit verification command argv required')
    require(packet.get('axis') in (None, 'standards', 'spec'), 'unknown review axis')
    lines = [field.capitalize() + ': ' + packet[field].strip() for field in fields]
    lines += ['Profile: ' + json.dumps(profile, sort_keys=True), 'Report: ' + path,
              'Independent verification commands: ' + json.dumps(commands)]
    if packet.get('axis'):
        lines.append('Review axis: ' + packet['axis'])
    spec = '\n\n'.join(lines)
    return {'spec': spec, 'sha256': hashlib.sha256(spec.encode()).hexdigest()}


def orca_artifact(path, directory, nonempty=True):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink() and path.is_file(),
            'durable regular artifact required')
    resolved = path.resolve()
    require(resolved.is_relative_to(directory.resolve()) and path.stat().st_uid == os.getuid(),
            'artifact must be owned and inside this private run directory')
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            size += len(block)
            digest.update(block)
    require(not nonempty or size, 'report artifact is empty')
    return {'path': str(resolved), 'sha256': digest.hexdigest(), 'bytes': size}


def orca_verification(data, record, job, directory):
    require(orca_artifact(job['report']['artifact']['path'], directory) == job['report']['artifact'],
            'settled report artifact changed')
    proof = data.get('verification')
    require(isinstance(proof, dict) and proof.get('stage') == job['role'],
            'explicit stage-specific independent verification required')
    checks = proof.get('checks')
    require(isinstance(checks, list) and len(checks) == len(job['packet']['verification_commands']),
            'every planned independent check required')
    captured = []
    for expected, check in zip(job['packet']['verification_commands'], checks):
        require(isinstance(check, dict) and check.get('argv') == expected
                and type(check.get('exit_code')) is int and check['exit_code'] == 0
                and check.get('commit') == data['commit'], 'independent check failed or mismatched')
        artifact = orca_artifact(check['output_path'], directory, nonempty=False)
        require(artifact['path'] != job['report']['artifact']['path'],
                'worker report is not independent check output')
        captured.append({**check, 'output': artifact})
    if job['role'] == 'reviewer':
        require(proof.get('verdict') == 'clean' and type(proof.get('must_fix')) is int
                and proof['must_fix'] == 0, 'clean review verdict with zero must-fix required')
    return {**proof, 'checks': captured}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True,
                                   stderr=subprocess.PIPE).strip()


def state_root(data):
    default = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'flyingnobita-deliver'
    root = Path(data.get('state_root', default)).expanduser().resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(root.stat().st_uid == os.getuid() and root.stat().st_mode & 0o077 == 0,
            'state root must be private and owned by current user')
    return root


def atomic(path, value):
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def create(data):
    repo = Path(git(data['repo'], 'rev-parse', '--show-toplevel')).resolve()
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    root = state_root(data)
    require(not root.is_relative_to(repo), 'state must be outside project checkout')
    require(data['host'].get('host') in ('herdr', 'paseo', 'orca') and data['host'].get('session')
            and data['host'].get('pane'), 'host/session/pane binding required')
    require(isinstance(data.get('approved', {}), dict), 'approved decisions must be an object')
    baseline = git(repo, 'rev-parse', '--verify', data['base'] + '^{commit}')
    git(repo, 'check-ref-format', '--branch', data['branch'])
    branch_ref = 'refs/heads/' + data['branch']
    exists = subprocess.run(['git', '-C', str(repo), 'show-ref', '--verify', '--quiet', branch_ref],
                            check=False).returncode
    require(exists in (0, 1), 'cannot inspect integration branch')
    if exists == 0:
        require(baseline == git(repo, 'rev-parse', branch_ref + '^{commit}'),
                'integration branch does not match approved base')
    limit = concurrency(data.get('concurrency', 3))
    purpose = data.get('purpose', 'delivery')
    require(purpose in PURPOSES, 'unknown run purpose')
    run_id = uuid.uuid4().hex
    directory = root / run_id
    directory.mkdir(mode=0o700)
    (directory / 'reports').mkdir(mode=0o700)
    record = {'schema': 1, 'run_id': run_id, 'repo': str(repo), 'common_dir': str(common),
              'baseline': baseline, 'base': data['base'], 'branch': data['branch'], 'stage': 'setup',
              'host': data['host'], 'approved': data.get('approved', {}), 'profiles': data['profiles'],
              'tasks': {}, 'evidence': [], 'concurrency': limit, 'purpose': purpose,
              'test_contract': 1, 'profile_contract': 1}
    if data['host']['host'] == 'orca':
        contract = data.get('orca_contract', 2)
        require(type(contract) is int and contract in (1, 2), 'unsupported Orca contract')
        record['orca_contract'] = contract
    atomic(directory / 'run.json', record)
    return record


def orca_head(record, job):
    worktree = Path(job['worktree']).resolve()
    require(worktree != Path(record['repo']), 'worker must use isolated worktree')
    require(git(worktree, 'rev-parse', '--path-format=absolute', '--git-common-dir') == record['common_dir'],
            'worktree belongs to another repository')
    require(git(worktree, 'symbolic-ref', '--short', 'HEAD') == job['branch'], 'branch mismatch')
    return git(worktree, 'rev-parse', 'HEAD')


def orca_evidence(command, data, record, directory):
    """Journal native identities; Orca alone decides lifecycle, retries and settlement."""
    require(record['host']['host'] == 'orca', 'Orca host required')
    jobs = record.setdefault('orca_jobs', {})
    key = identifier(data['job'])
    if command == 'orca-intent':
        require(key not in jobs, 'dispatch already intended; reconcile native request before retry')
        role = data['role']
        authorize_role(record, role)
        require(sum('report' not in j and 'rejection' not in j for j in jobs.values()) < record['concurrency'],
                'concurrency limit reached')
        for field in ('request_id', 'native_run', 'native_task'):
            identifier(data[field])
        require(all(j['request_id'] != data['request_id'] for j in jobs.values()), 'request already recorded')
        require(record.get('orca_run', data['native_run']) == data['native_run'], 'native run mismatch')
        job = {k: data[k] for k in ('request_id', 'native_run', 'native_task', 'role', 'worktree', 'branch', 'base')}
        job['worktree'] = str(Path(job['worktree']).resolve())
        require(orca_head(record, job) == data['base'], 'base changed before dispatch')
        for old in jobs.values():
            if 'report' not in old and 'rejection' not in old:
                require(old['worktree'] != job['worktree'] and old['branch'] != job['branch'],
                        'workspace already has a pending dispatch')
        if record.get('orca_contract', 1) >= 2:
            packet = data.get('packet')
            compiled = orca_task({'packet': packet})
            require(packet['profile'] == record['profiles'].get(role), 'task profile differs from selected role')
            report_path = Path(packet['report_path']).resolve()
            require(report_path.is_relative_to(directory.resolve()) and
                    not report_path.is_relative_to(Path(job['worktree'])),
                    'task report must be inside private run directory, outside worktree')
            job['packet'], job['compiled_task'] = packet, compiled
        job['verified'] = False
        jobs[key] = job
        record['orca_run'] = data['native_run']
        return
    job = jobs[key]
    require('rejection' not in job, 'rejected intent is immutable')
    if command == 'orca-receipt':
        require('dispatch' not in job and data.get('evidence'), 'receipt already recorded or missing evidence')
        require(all(data.get(k) == job[k] for k in ('native_run', 'native_task', 'request_id')),
                'native receipt identity mismatch')
        dispatch = identifier(data['dispatch'])
        require(all(j.get('dispatch') != dispatch for j in jobs.values()), 'dispatch already bound')
        job['dispatch'] = dispatch
        job['receipt'] = data['evidence']
    elif command == 'orca-report':
        require(job.get('dispatch') and all(data.get(k) == job[k] for k in ('native_run', 'native_task', 'dispatch')),
                'native completion identity mismatch')
        require('report' not in job, 'report is immutable')
        require(data.get('outcome') in ('succeeded', 'failed') and data.get('checks')
                and isinstance(data.get('questions'), list) and data.get('evidence'), 'incomplete completion report')
        require(data['commit'] == orca_head(record, job), 'report commit mismatch')
        report = {k: data[k] for k in ('native_run', 'native_task', 'dispatch', 'outcome', 'commit',
                                      'checks', 'questions', 'evidence')}
        if record.get('orca_contract', 1) >= 2:
            require(data.get('artifact_path') == job['packet']['report_path'],
                    'matching packet report artifact required')
            report['artifact'] = orca_artifact(data['artifact_path'], directory)
        path = directory / 'reports' / (key + '-orca.json')
        if path.exists():
            require(json.loads(path.read_text()) == report, 'report is immutable')
        else:
            atomic(path, report)
        job['report'] = report
        job['report_path'] = str(path)
    elif command == 'orca-rejected':
        require('dispatch' not in job and 'report' not in job, 'dispatch exists; use native settlement')
        require(all(data.get(k) == job[k] for k in ('native_run', 'native_task', 'request_id')),
                'native rejection identity mismatch')
        recorded = data.get('request_state') == 'completed' and data.get('task_state') in ('ready', 'failed')
        # Orca rejects blocked Tasks before its request journal starts. A missing
        # receipt alone remains uncertain; retain the exact matching direct refusal.
        refusal = data.get('preflight_rejection')
        error = refusal.get('error', {}) if isinstance(refusal, dict) else {}
        error_data = error.get('data', {}) if isinstance(error, dict) else {}
        direct = (data.get('request_state') == 'absent' and data.get('task_state') == 'pending'
                  and isinstance(refusal, dict) and refusal.get('ok') is False
                  and isinstance(error, dict) and error.get('code') == 'task_not_startable'
                  and isinstance(error_data, dict) and error_data.get('status') == 'pending'
                  and error_data.get('taskId') == job['native_task']
                  and error_data.get('orchestrationRequestId') == job['request_id'])
        require((recorded or direct) and data.get('dispatch_absent') is True and data.get('evidence'),
                'recorded rejection or matching direct preflight refusal and inspected absence of dispatch required')
        require(orca_head(record, job) == job['base'] and
                not git(job['worktree'], 'status', '--porcelain', '--untracked-files=all'),
                'work changed; preserve and inspect')
        job['rejection'] = {k: data[k] for k in ('request_state', 'task_state', 'dispatch_absent', 'evidence')}
        if direct:
            job['rejection']['preflight_rejection'] = refusal
    elif command == 'orca-verify':
        report = job.get('report', {})
        require(report.get('outcome') == 'succeeded' and not report.get('questions'),
                'successful report without pending questions required')
        require(data.get('dispatch') == job['dispatch'] and data.get('host') == record['host']['session'],
                'dispatch/host mismatch')
        require(data.get('evidence') and data['commit'] == report['commit'] == orca_head(record, job),
                'independent verification/commit mismatch')
        require(not git(job['worktree'], 'status', '--porcelain', '--untracked-files=all'),
                'uncommitted work; verify committed result')
        proof = orca_verification(data, record, job, directory) if record.get('orca_contract', 1) >= 2 else None
        job['verified'] = True
        record['evidence'].append({'job': key, 'dispatch': job['dispatch'], 'commit': data['commit'],
                                   'verification': proof or data['evidence']})
    else:
        raise ValueError('unsupported Orca evidence operation')


def check_resource(record, resource):
    require(all(resource.get(k) for k in ('worktree', 'branch', 'workspace', 'pane', 'agent', 'session')),
            'complete resource binding required')
    require(resource['session'] in (record['host']['session'], *record.get('previous_sessions', [])),
            'resource host mismatch')
    worktree = Path(resource['worktree']).resolve()
    require(worktree != Path(record['repo']), 'worker must use isolated worktree')
    require(git(worktree, 'rev-parse', '--path-format=absolute', '--git-common-dir') == record['common_dir'],
            'worktree belongs to another repository')
    require(git(worktree, 'symbolic-ref', '--short', 'HEAD') == resource['branch'], 'branch mismatch')
    return git(worktree, 'rev-parse', 'HEAD')


def test_commit(repo, value):
    require(isinstance(value, str) and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', value),
            'test provenance requires full commit hashes')
    require(git(repo, 'rev-parse', '--verify', value + '^{commit}') == value,
            'test provenance commit mismatch')


def test_report(record, task, attempt, report):
    # Legacy runs remain resumable; opting into proof always validates it.
    required = task['role'] == 'implementer' and record.get('test_contract') == 1
    if not required and 'test_scope' not in report and 'test_evidence' not in report:
        return []
    scope, groups = report.get('test_scope'), report.get('test_evidence')
    require(scope in ('changed', 'none', 'docs-only') and isinstance(groups, list),
            'test_scope and test_evidence required for implementer reports')
    changed = git(record['repo'], 'diff', '--name-only', '--diff-filter=ACMRT',
                  attempt['base'], report['commit']).splitlines()
    # Catch omission of conventional test files; custom seams still need review.
    changed_tests = {p for p in changed if
                     set(Path(p).parts[:-1]) & {'test', 'tests', '__tests__', 'spec', 'specs'}
                     or Path(p).name.startswith('test_')
                     or re.search(r'(?:_test\.[^.]+|\.(?:test|spec)\.[^.]+|\.bats)$', p)}
    if scope != 'changed':
        require(not groups and isinstance(report.get('test_reason'), str) and report['test_reason'].strip(),
                'no-test exemption requires a reason and empty test_evidence')
        require(not changed_tests, 'changed test files cannot use a no-test exemption')
        if scope == 'docs-only':
            paths = git(record['repo'], 'diff', '--name-only', attempt['base'], report['commit']).splitlines()
            require(all(Path(p).suffix.lower() in ('.md', '.rst', '.txt', '.adoc') for p in paths),
                    'docs-only exemption contains non-document changes')
        return []
    require(groups, 'changed tests require provenance groups')
    ids = set()
    covered = set()
    for group in groups:
        require(isinstance(group, dict) and isinstance(group.get('id'), str) and group['id']
                and group['id'] not in ids, 'test provenance needs unique group ids')
        ids.add(group['id'])
        kind = group.get('kind')
        require(kind in ('behavioral', 'guard', 'bootstrap'), 'unknown test provenance kind')
        for field in ('subject_commit', 'test_commit'):
            test_commit(record['repo'], group.get(field))
        require(kind != 'behavioral' or group['subject_commit'] != report['commit'],
                'behavioral red subject is the final green commit')
        require(kind == 'behavioral' or (isinstance(group.get('reason'), str) and group['reason'].strip()),
                'guard/bootstrap classification requires its plan-backed reason')
        tests = group.get('tests')
        require(isinstance(tests, list) and tests, 'test paths and content hashes required')
        paths = set()
        for test in tests:
            require(isinstance(test, dict), 'test path/hash entry must be an object')
            path = test.get('path')
            require(isinstance(path, str) and path and not Path(path).is_absolute()
                    and '..' not in Path(path).parts and path not in paths,
                    'test paths must be unique checkout-relative files')
            paths.add(path)
            covered.add(path)
            blob = subprocess.check_output(['git', '-C', record['repo'], 'cat-file', 'blob',
                                            group['test_commit'] + ':' + path], stderr=subprocess.PIPE)
            require(test.get('sha256') == hashlib.sha256(blob).hexdigest(),
                    'test content hash differs from cited test commit')
    require(changed_tests <= covered, 'changed test paths missing from provenance groups')
    return groups


def test_results(record, task, attempt, report, data):
    groups = test_report(record, task, attempt, report)
    results = data.get('test_results', [])
    require(isinstance(results, list) and len(results) == len(groups),
            'independent before/after receipts required for every test group')
    require(all(isinstance(row, dict) and isinstance(row.get('id'), str) for row in results),
            'test results require group ids')
    indexed = {row['id']: row for row in results}
    require(set(indexed) == {group['id'] for group in groups}, 'test receipt group mismatch')
    proof = []
    for group in groups:
        for phase in ('before', 'after'):
            reference = indexed[group['id']][phase]
            path = Path(reference['path'])
            require(path.is_absolute() and path.is_file() and not path.is_symlink()
                    and not path.resolve().is_relative_to(Path(attempt['resource']['worktree']).resolve()),
                    'independent receipt must be a regular file outside the worker checkout')
            content = path.read_bytes()
            require(reference.get('sha256') == hashlib.sha256(content).hexdigest(),
                    'independent receipt hash mismatch')
            receipt = json.loads(content)
            require(isinstance(receipt, dict), 'independent receipt must be an object')
            expected = {'run_id': record['run_id'], 'task': data['task'], 'attempt': attempt['id'],
                        'phase': phase, 'test_commit': group['test_commit'], 'tests': group['tests'],
                        'subject_commit': group['subject_commit'] if phase == 'before' else report['commit']}
            require(all(receipt.get(k) == v for k, v in expected.items()),
                    'independent receipt identity, commit or test content mismatch')
            command = receipt.get('command')
            require(isinstance(command, list) and command and all(isinstance(arg, str) for arg in command),
                    'independent receipt command argv required')
            rc = receipt.get('returncode')
            require(type(rc) is int, 'receipt returncode must be an integer')
            failure = phase == 'before' and group['kind'] in ('behavioral', 'bootstrap')
            expected_class = ('assertion-failure' if group['kind'] == 'behavioral' else 'bootstrap-absence') if failure else 'passed'
            require((0 < rc <= 255 if failure else rc == 0)
                    and receipt.get('classification') == expected_class,
                    'receipt is not the required assertion failure, bootstrap absence or pass')
            proof.append({'group': group['id'], **reference, 'receipt': receipt})
    return proof


def canonical_profile(role, value):
    require(isinstance(value, dict), 'complete profile object required')
    compiled = profiles({'defaults': {role if role in ('planner', 'implementer', 'reviewer', 'qa') else 'qa': value}})
    profile = next(iter(compiled.values()))['profile']
    return {key: profile[key] for key in ('harness', 'model', 'effort', 'mode')}


def requested_profile(record, task, data, previous=None):
    current = (previous or {}).get('requested_profile')
    if current is None:
        row = record['profiles'].get(task['role'], {})
        current = row.get('profile', row) or None
    if current is not None:
        current = canonical_profile(task['role'], current)
    chosen = data.get('requested_profile', current)
    if chosen is not None:
        chosen = canonical_profile(task['role'], chosen)
    if chosen != current:
        require(isinstance(data.get('profile_authorization'), str) and data['profile_authorization'].strip(),
                'profile selection/change requires recorded user authorization')
    return chosen


def update_task(command, data, record, directory):
    task = record['tasks'][data['task']]
    require(not task.get('abandoned'), 'task abandoned')
    if command == 'abandon':
        require(not task['verified'] and data.get('evidence') and data.get('user_decision'),
                'abandoning an unverified task requires evidence and the user decision')
        if task['attempts'] and task['attempts'][-1]['status'] != 'recovered':
            task['attempts'][-1]['status'] = 'abandoned'
        task['abandoned'] = {'evidence': data['evidence'], 'user_decision': data['user_decision'],
                             'at': observed_at()}
        return
    if command == 'attempt':
        require(not task['verified'], 'task already verified')
        authorize_role(record, task['role'])
        require(all(record['tasks'][d]['verified'] for d in task['dependencies']), 'dependencies incomplete')
        require(not task['attempts'] or task['attempts'][-1]['status'] == 'recovered',
                'existing attempt requires reconciliation')
        active = sum(bool(t['attempts']) and not t['verified'] and not t.get('abandoned') and
                     t['attempts'][-1]['status'] != 'recovered' for t in record['tasks'].values())
        require(active < record['concurrency'], 'concurrency limit reached')
        resource = data['resource']
        require(resource.get('session') == record['host']['session'], 'resource host mismatch')
        commit = check_resource(record, resource)
        require(commit == record['baseline'] or data.get('approved_base') == commit,
                'worker base differs from approved baseline')
        for other in record['tasks'].values():
            if other['verified'] or other.get('abandoned'):
                continue
            for previous in other['attempts']:
                require(all(previous['resource'][key] != resource[key]
                            for key in ('worktree', 'pane', 'agent', 'workspace', 'branch')),
                        'resource collision with recorded attempt')
        attempt_id = uuid.uuid4().hex
        task['attempts'].append({'id': attempt_id, 'resource': resource, 'base': commit,
                                 'created_at': observed_at(),
                                 'requested_profile': requested_profile(record, task, data),
                                 'profile_authorization': data.get('profile_authorization'),
                                 'status': 'ready', 'report_path': str(directory / 'reports' /
                                 (data['task'] + '-' + attempt_id + '.json'))})
        return
    require(task['attempts'], 'no task attempt')
    attempt = task['attempts'][-1]
    if command != 'recover':
        require(data['attempt'] == attempt['id'], 'stale attempt')
    if command == 'profile-bind':
        require('profile_proof' not in attempt and attempt['status'] not in ('continued', 'verified', 'recovered'),
                'profile proof is immutable; use a followup attempt for a replacement')
        chosen = requested_profile(record, task, data, attempt)
        actual = canonical_profile(task['role'], data.get('observed_profile'))
        require(chosen is not None and actual == chosen, 'observed profile differs from authorized request')
        require(data.get('worker_session') and data.get('evidence') and data.get('availability_verified') is True,
                'startup evidence, availability verification and harness session required')
        require(attempt.get('worker_session', data['worker_session']) == data['worker_session'],
                'profile proof harness session mismatch')
        attempt['requested_profile'] = chosen
        attempt['profile_authorization'] = data.get('profile_authorization', attempt.get('profile_authorization'))
        attempt['worker_session'] = data['worker_session']
        attempt['profile_proof'] = {'requested_profile': chosen, 'observed_profile': actual,
                                    'worker_session': data['worker_session'], 'availability_verified': True,
                                    'evidence': data['evidence'], 'bound_at': observed_at()}
    elif command == 'prompt':
        require(record['host']['host'] == 'herdr', 'native prompt requires Herdr')
        require(attempt['status'] == 'ready', 'prompt already intended; inspect before retry')
        require(data.get('worker_session'), 'recognized worker harness session required')
        require(not attempt.get('profile_proof')
                or attempt['profile_proof']['worker_session'] == data['worker_session'],
                'dispatch differs from the bound profile session; use a followup')
        timeout = data.get('timeout_ms', 30000)
        require(isinstance(timeout, int) and 1 <= timeout <= 60000, 'wait must be bounded to 60 seconds')
        binary = data.get('herdr_bin', 'herdr')
        target = attempt['resource']['pane']
        agent = json.loads(subprocess.check_output([binary, 'agent', 'get', target],
                           text=True, timeout=10))['result']['agent']
        require(agent.get('pane_id') == target and
                agent.get('workspace_id') == attempt['resource']['workspace'] and
                agent.get('agent_session', {}).get('value') == data['worker_session'] and
                agent.get('agent_status') in ('idle', 'done'), 'worker identity/readiness mismatch')
        update_task('dispatch-intent', data, record, directory)
        attempt['worker_session'] = data['worker_session']
        attempt['completion_baseline'] = agent.get('completion_seq')
        atomic(directory / 'run.json', record)
        try:
            response = subprocess.run([binary, 'agent', 'prompt', target, data['prompt'],
                                       '--wait', '--until', 'working', '--until', 'blocked',
                                       '--timeout', str(timeout)], text=True,
                                      capture_output=True, timeout=timeout / 1000 + 5, check=False)
            attempt['dispatch_response'] = {'returncode': response.returncode,
                                            'stdout': response.stdout, 'stderr': response.stderr}
            if response.returncode == 0:
                attempt['status'] = 'observed'
                attempt['acknowledged_at'] = observed_at()
        except (subprocess.TimeoutExpired, OSError) as error:
            attempt['dispatch_response'] = {'error': str(error)}
        # Even success is only an observation. A matching report and verification are separate gates.
    elif command == 'dispatch-intent':
        require(attempt['status'] == 'ready', 'prompt already intended; inspect before retry')
        require(isinstance(data['prompt'], str) and data['prompt'], 'empty prompt')
        attempt['prompt_sha256'] = hashlib.sha256(data['prompt'].encode()).hexdigest()
        attempt['status'] = 'dispatch-uncertain'
        attempt['dispatched_at'] = observed_at()
    elif command == 'followup':
        require(attempt['status'] == 'reported' and not task['verified'] and data.get('evidence'),
                'followup requires unverified report and recorded answer/decision')
        head = check_resource(record, attempt['resource'])
        require(head == json.loads(Path(attempt['report_path']).read_text())['commit'],
                'work changed since report; inspect before followup')
        chosen = requested_profile(record, task, data, attempt)
        attempt['status'] = 'continued'
        attempt['followup_evidence'] = data['evidence']
        attempt_id = uuid.uuid4().hex
        task['attempts'].append({'id': attempt_id, 'resource': dict(attempt['resource']),
                                 'created_at': observed_at(), 'requested_profile': chosen,
                                 'profile_authorization': data.get('profile_authorization', attempt.get('profile_authorization')),
                                 'base': head, 'status': 'ready', 'previous_attempt': attempt['id'],
                                 'report_path': str(directory / 'reports' /
                                 (data['task'] + '-' + attempt_id + '.json'))})
    elif command == 'handoff':
        require(attempt['status'] in ('ready', 'dispatch-uncertain', 'observed'),
                'handoff requires an unreported attempt; after a report use followup')
        require(not Path(attempt['report_path']).exists(), 'report exists; record it and use followup')
        require(data.get('evidence'), 'handoff evidence required')
        observation = attempt.get('reconciliation', {})
        head = check_resource(record, attempt['resource'])
        clean = not git(attempt['resource']['worktree'], 'status', '--porcelain', '--untracked-files=all')
        require(observation.get('commit') == head and observation.get('clean') == clean,
                'reconcile the live worker before handoff; work changed since reconciliation')
        worker = data.get('worker') or {}
        resource = {**attempt['resource'], **{k: worker[k] for k in ('workspace', 'pane', 'agent') if worker.get(k)},
                    'session': record['host']['session']}
        check_resource(record, resource)
        for other_id, other in record['tasks'].items():
            if other_id == data['task'] or other['verified'] or other.get('abandoned'):
                continue
            for previous in other['attempts']:
                require(all(previous['resource'][key] != resource[key] for key in ('pane', 'agent')),
                        'resource collision with recorded attempt')
        chosen = requested_profile(record, task, data, attempt)
        attempt['status'] = 'handed-off'
        attempt['handoff'] = {'evidence': data['evidence'], 'commit': head, 'clean': clean, 'at': observed_at()}
        attempt_id = uuid.uuid4().hex
        task['attempts'].append({'id': attempt_id, 'resource': resource, 'base': head,
                                 'created_at': observed_at(), 'requested_profile': chosen,
                                 'profile_authorization': data.get('profile_authorization', attempt.get('profile_authorization')),
                                 'status': 'ready', 'previous_attempt': attempt['id'],
                                 'report_path': str(directory / 'reports' /
                                 (data['task'] + '-' + attempt_id + '.json'))})
    elif command == 'cleanup-check':
        require(task['verified'] and data.get('observation') == attempt['resource'],
                'verified task and current ownership required')
        head = check_resource(record, attempt['resource'])
        require(not git(attempt['resource']['worktree'], 'status', '--porcelain', '--untracked-files=all'),
                'dirty worktree; preserve')
        landed = git(record['repo'], 'rev-parse', '--verify', data['landed'] + '^{commit}')
        ancestor = subprocess.run(['git', '-C', record['repo'], 'merge-base', '--is-ancestor', head, landed],
                                  capture_output=True, check=False).returncode == 0
        same_tree = git(record['repo'], 'rev-parse', head + '^{tree}') == git(record['repo'], 'rev-parse', landed + '^{tree}')
        require(ancestor or same_tree, 'landing not verified by ancestry or identical tree')
        attempt['cleanup_checked'] = {'head': head, 'landed': landed, 'ownership': data['observation']}
    elif command == 'reconcile':
        observation = data['observation']
        require(observation.get('session') == record['host']['session'] and
                observation.get('resource') == attempt['resource'], 'live ownership/session mismatch')
        head = check_resource(record, attempt['resource'])
        require(observation.get('commit') == head, 'live Git observation mismatch')
        require(observation.get('agent_state') in ('idle', 'done', 'working', 'blocked', 'unknown', 'exited'),
                'invalid live agent state')
        clean = not git(attempt['resource']['worktree'], 'status', '--porcelain', '--untracked-files=all')
        attempt['reconciliation'] = {**observation, 'clean': clean}
    elif command == 'recover':
        observation = attempt.get('reconciliation', {})
        require(task['recoveries'] < 2, 'automatic recovery limit exhausted')
        require(attempt['status'] in ('ready', 'dispatch-uncertain', 'observed'),
                'preserve reported or recovered work')
        require(observation.get('agent_state') == 'exited' and
                observation.get('dispatch') == 'not-submitted' and observation.get('clean') and
                observation.get('commit') == attempt['base'], 'ambiguous outcome; preserve and inspect')
        require(check_resource(record, attempt['resource']) == attempt['base'] and
                not git(attempt['resource']['worktree'], 'status', '--porcelain', '--untracked-files=all') and
                not Path(attempt['report_path']).exists(), 'work changed since reconciliation')
        attempt['status'] = 'recovered'
        task['recoveries'] += 1
    elif command == 'report':
        report = data['report']
        require(attempt['status'] in ('dispatch-uncertain', 'observed'), 'attempt not dispatched')
        require(all(report.get(k) == v for k, v in
                    [('run_id', record['run_id']), ('task', data['task']), ('attempt', attempt['id'])]),
                'report identity mismatch')
        require(report.get('checks') and isinstance(report.get('questions'), list), 'incomplete report')
        require(report.get('commit') == check_resource(record, attempt['resource']), 'report commit mismatch')
        test_report(record, task, attempt, report)
        path = Path(attempt['report_path'])
        if path.exists():
            require(json.loads(path.read_text()) == report, 'report is immutable')
        else:
            atomic(path, report)
        attempt['status'] = 'reported'
        attempt['reported_at'] = observed_at()
    elif command == 'verify':
        require(attempt['status'] == 'reported', 'matching report required')
        report = json.loads(Path(attempt['report_path']).read_text())
        require(not report['questions'], 'unresolved worker questions')
        require(data.get('host') == record['host']['session'], 'revalidate host before verification')
        require(data.get('evidence') and data['commit'] == report['commit'] ==
                check_resource(record, attempt['resource']), 'independent verification/commit mismatch')
        proof = test_results(record, task, attempt, report, data)
        profile = attempt.get('profile_proof')
        if record.get('profile_contract') == 1 or profile is not None:
            require(profile and profile.get('availability_verified') is True
                    and profile['observed_profile'] == attempt['requested_profile']
                    and profile['worker_session'] == attempt.get('worker_session'),
                    'matching effective profile proof required before verification')
        task['verified'] = True
        attempt['status'] = 'verified'
        attempt['verified_at'] = observed_at()
        record['evidence'].append({'task': data['task'], 'attempt': attempt['id'],
                                   'commit': data['commit'], 'verification': data['evidence'],
                                   'test_results': proof, 'profile_proof': profile})
    else:
        raise ValueError('unsupported task operation')


def ancestors():
    pids, pid = set(), os.getpid()
    while pid > 1 and pid not in pids:
        pids.add(pid)
        try:
            pid = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            break
    return pids


def darwin_busy_processes(worktree, pattern):
    """macOS has no procfs; inspect same-user candidates with native ps/lsof."""
    output = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,uid=,args='], text=True, timeout=10)
    processes = {}
    for line in output.splitlines():
        fields = line.strip().split(None, 3)
        if len(fields) == 4 and all(value.isdigit() for value in fields[:3]):
            pid, parent, uid = map(int, fields[:3])
            processes[pid] = (parent, uid, fields[3])
    own, pid = set(), os.getpid()
    while pid > 1 and pid not in own:
        own.add(pid)
        pid = processes.get(pid, (0,))[0]
    found = []
    for pid, (_, uid, command) in processes.items():
        if pid in own or uid != os.getuid() or not re.search(pattern, command):
            continue
        result = subprocess.run(['lsof', '-a', '-p', str(pid), '-d', 'cwd', '-Fpn0'],
                                capture_output=True, timeout=10, check=False)
        if result.returncode:
            # A candidate can exit between ps and lsof. A still-live unreadable
            # process is unknown, not evidence that background work has settled.
            exists = subprocess.run(['ps', '-p', str(pid), '-o', 'pid='],
                                    capture_output=True, timeout=10, check=False)
            require(exists.returncode == 1 and not exists.stdout.strip(),
                    'cannot inspect live background process cwd')
            continue
        paths = [Path(os.fsdecode(field[1:])) for field in result.stdout.split(b'\0')
                 if field.startswith(b'n')]
        require(paths, 'background process cwd missing from lsof output')
        if any(cwd == worktree or worktree in cwd.parents for cwd in paths):
            found.append({'pid': pid, 'command': command})
    return sorted(found, key=lambda process: process['pid'])


def busy_processes(worktree, pattern):
    """Processes running in the worktree whose command line matches pattern, never this waiter."""
    if sys.platform == 'darwin':
        return darwin_busy_processes(worktree, pattern)
    own, found = ancestors(), []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit() or int(entry.name) in own:
            continue
        try:
            cwd = Path(os.readlink(entry / 'cwd'))
            command = (entry / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip()
        except OSError:
            continue
        if (cwd == worktree or worktree in cwd.parents) and re.search(pattern, command):
            found.append({'pid': int(entry.name), 'command': command})
    return sorted(found, key=lambda process: process['pid'])


def wait(data):
    """Read-only, bounded wait on one attempt: report, blocked prompt, background work or silence."""
    directory = state_root(data) / identifier(data['run_id'])
    require(directory.is_dir() and not directory.is_symlink(), 'run missing or symlinked')
    record = json.loads((directory / 'run.json').read_text())
    attempt = record['tasks'][data['task']]['attempts'][-1]
    require(data['attempt'] == attempt['id'], 'stale attempt')
    timeout, poll = data.get('timeout_s', 300), data.get('poll_s', 5)
    require(isinstance(timeout, (int, float)) and 0 < timeout <= 600 and
            isinstance(poll, (int, float)) and 0 < poll <= timeout, 'wait must be bounded to 600 seconds')
    pattern = data.get('busy_pattern', r'\b(test|pytest|vitest|jest)\b')
    worktree = Path(attempt['resource']['worktree']).resolve()
    deadline = time.monotonic() + timeout
    while True:
        status, busy = 'unknown', []
        if Path(attempt['report_path']).exists():
            state = 'reported'
        else:
            try:
                status = json.loads(subprocess.check_output(
                    [data.get('herdr_bin', 'herdr'), 'agent', 'get', attempt['resource']['pane']],
                    text=True, timeout=10))['result']['agent'].get('agent_status', 'unknown')
            except (subprocess.SubprocessError, OSError, ValueError, KeyError):
                pass
            busy = busy_processes(worktree, pattern) if status in ('idle', 'done') else []
            state = {'blocked': 'blocked', 'exited': 'exited'}.get(status)
            if status in ('idle', 'done'):
                state = 'background-running' if busy else 'settled-no-report'
        if state not in (None, 'background-running') or time.monotonic() >= deadline:
            return {'state': state or 'timeout', 'agent_status': status, 'busy': busy,
                    'report_path': attempt['report_path']}
        time.sleep(poll)


def run_command(command, data):
    directory = state_root(data) / identifier(data['run_id'])
    require(directory.is_dir() and not directory.is_symlink(), 'run missing or symlinked')
    with (directory / 'writer.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another orchestrator is mutating this run') from None
        record = json.loads((directory / 'run.json').read_text())
        require(record['schema'] == 1, 'unsupported state schema')
        if command == 'show':
            return record
        if command == 'approve':
            approved = data['approved']
            require(isinstance(approved, dict) and
                    all(approved.get(k) for k in PURPOSES[record.get('purpose', 'delivery')][0])
                    and data.get('evidence'), 'purpose-specific user authorization plus evidence required')
            record['evidence'].append({'previous_approved': record['approved'],
                                       'approved': approved, 'user_approval': data['evidence']})
            record['approved'] = approved
        elif command == 'checkpoint':
            host = data['host']
            change = data.get('session_change') or {}
            moved = host.get('session') != record['host']['session']
            require(host.get('host') == record['host']['host'] and host.get('session') and
                    host.get('pane') and data.get('evidence') and data.get('stage') and
                    (not moved or (change.get('caller_evidence') and change.get('user_confirmation'))),
                    'revalidated same host, stage and evidence required; a session change needs '
                    'caller evidence and user confirmation')
            require(Path(git(record['repo'], 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
                    == Path(record['common_dir']), 'canonical repository changed')
            record['evidence'].append({'previous_host': record['host'], 'host': host,
                                       'stage': data['stage'], 'verification': data['evidence'],
                                       **({'session_change': change} if moved else {})})
            if moved:
                record.setdefault('previous_sessions', []).append(record['host']['session'])
            record['host'] = host
            record['stage'] = data['stage']
        elif command == 'operation-intent':
            operations = record.setdefault('operations', {})
            operation_id = identifier(data['operation_id'])
            require(operation_id not in operations, 'operation already intended; inspect before retry')
            require(data['operation'] in ('worktree-create', 'agent-start', 'worktree-remove', 'workspace-close',
                                         'run-create', 'task-create', 'worker-release', 'opencode-session-create'),
                    'unsupported resource operation')
            require(isinstance(data['target'], dict) and data['target'], 'exact target required')
            operations[operation_id] = {'operation': data['operation'], 'target': data['target'], 'status': 'uncertain'}
        elif command == 'operation-result':
            operation = record['operations'][identifier(data['operation_id'])]
            require(operation['status'] == 'uncertain' and data.get('result'), 'operation already reconciled or no result')
            operation['result'] = data['result']
            operation['status'] = 'observed'
        elif command == 'task':
            task_id = identifier(data['task'])
            require(task_id not in record['tasks'], 'task already exists')
            dependencies = data.get('dependencies', [])
            require(len(set(dependencies)) == len(dependencies) and
                    all(d in record['tasks'] for d in dependencies), 'invalid dependencies')
            record['tasks'][task_id] = {'dependencies': dependencies, 'recoveries': 0,
                                        'attempts': [], 'verified': False, 'role': data.get('role', 'implementer')}
        elif command.startswith('orca-'):
            orca_evidence(command, data, record, directory)
        else:
            update_task(command, data, record, directory)
        atomic(directory / 'run.json', record)
        return record


def main():
    data = json.load(sys.stdin)
    command = sys.argv[1]
    if command == 'orca-settle':
        command = 'orca-report'
    standalone = {'select': select, 'select-host': select_hosts, 'profiles': profiles, 'wait': wait,
                  'create': create, 'migrate-orca': migrate_orca, 'orca-task': orca_task}
    result = standalone[command](data) if command in standalone else run_command(command, data)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, IndexError, TypeError, subprocess.SubprocessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
