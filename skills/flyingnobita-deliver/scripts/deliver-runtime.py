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
import uuid
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


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
        require(harness in ('codex', 'claude', 'agy'), 'unsupported harness')
        require(isinstance(model, str) and model and not model.startswith('-'), 'invalid model')
        require(not profile.get('provider') and not profile.get('features'),
                'provider/features require a verified native mapping; cannot drop settings')
        if harness == 'claude':
            require(effort in ('low', 'medium', 'high', 'xhigh', 'max'), 'unsupported Claude effort')
            require(mode in ('plan', 'auto', 'manual', 'dontAsk', 'acceptEdits', 'bypassPermissions'),
                    'unsupported Claude permission mode')
            argv = ['--model', model, '--effort', effort, '--permission-mode', mode]
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
              'tasks': {}, 'evidence': [], 'concurrency': limit, 'purpose': purpose}
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
    require(resource['session'] == record['host']['session'], 'resource host mismatch')
    worktree = Path(resource['worktree']).resolve()
    require(worktree != Path(record['repo']), 'worker must use isolated worktree')
    require(git(worktree, 'rev-parse', '--path-format=absolute', '--git-common-dir') == record['common_dir'],
            'worktree belongs to another repository')
    require(git(worktree, 'symbolic-ref', '--short', 'HEAD') == resource['branch'], 'branch mismatch')
    return git(worktree, 'rev-parse', 'HEAD')


def update_task(command, data, record, directory):
    task = record['tasks'][data['task']]
    if command == 'attempt':
        require(not task['verified'], 'task already verified')
        authorize_role(record, task['role'])
        require(all(record['tasks'][d]['verified'] for d in task['dependencies']), 'dependencies incomplete')
        require(not task['attempts'] or task['attempts'][-1]['status'] == 'recovered',
                'existing attempt requires reconciliation')
        active = sum(bool(t['attempts']) and not t['verified'] and
                     t['attempts'][-1]['status'] != 'recovered' for t in record['tasks'].values())
        require(active < record['concurrency'], 'concurrency limit reached')
        resource = data['resource']
        commit = check_resource(record, resource)
        require(commit == record['baseline'] or data.get('approved_base') == commit,
                'worker base differs from approved baseline')
        for other in record['tasks'].values():
            if other['verified']:
                continue
            for previous in other['attempts']:
                require(all(previous['resource'][key] != resource[key]
                            for key in ('worktree', 'pane', 'agent', 'workspace', 'branch')),
                        'resource collision with recorded attempt')
        attempt_id = uuid.uuid4().hex
        task['attempts'].append({'id': attempt_id, 'resource': resource, 'base': commit,
                                 'status': 'ready', 'report_path': str(directory / 'reports' /
                                 (data['task'] + '-' + attempt_id + '.json'))})
        return
    require(task['attempts'], 'no task attempt')
    attempt = task['attempts'][-1]
    if command != 'recover':
        require(data['attempt'] == attempt['id'], 'stale attempt')
    if command == 'prompt':
        require(record['host']['host'] == 'herdr', 'native prompt requires Herdr')
        require(attempt['status'] == 'ready', 'prompt already intended; inspect before retry')
        require(data.get('worker_session'), 'recognized worker harness session required')
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
                                       '--wait', '--timeout', str(timeout)], text=True,
                                      capture_output=True, timeout=timeout / 1000 + 5, check=False)
            attempt['dispatch_response'] = {'returncode': response.returncode,
                                            'stdout': response.stdout, 'stderr': response.stderr}
            if response.returncode == 0:
                attempt['status'] = 'observed'
        except (subprocess.TimeoutExpired, OSError) as error:
            attempt['dispatch_response'] = {'error': str(error)}
        # Even success is only an observation. A matching report and verification are separate gates.
    elif command == 'dispatch-intent':
        require(attempt['status'] == 'ready', 'prompt already intended; inspect before retry')
        require(isinstance(data['prompt'], str) and data['prompt'], 'empty prompt')
        attempt['prompt_sha256'] = hashlib.sha256(data['prompt'].encode()).hexdigest()
        attempt['status'] = 'dispatch-uncertain'
    elif command == 'followup':
        require(attempt['status'] == 'reported' and not task['verified'] and data.get('evidence'),
                'followup requires unverified report and recorded answer/decision')
        head = check_resource(record, attempt['resource'])
        require(head == json.loads(Path(attempt['report_path']).read_text())['commit'],
                'work changed since report; inspect before followup')
        attempt['status'] = 'continued'
        attempt['followup_evidence'] = data['evidence']
        attempt_id = uuid.uuid4().hex
        task['attempts'].append({'id': attempt_id, 'resource': dict(attempt['resource']),
                                 'base': head, 'status': 'ready', 'previous_attempt': attempt['id'],
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
        path = Path(attempt['report_path'])
        if path.exists():
            require(json.loads(path.read_text()) == report, 'report is immutable')
        else:
            atomic(path, report)
        attempt['status'] = 'reported'
    elif command == 'verify':
        require(attempt['status'] == 'reported', 'matching report required')
        report = json.loads(Path(attempt['report_path']).read_text())
        require(not report['questions'], 'unresolved worker questions')
        require(data.get('host') == record['host']['session'], 'revalidate host before verification')
        require(data.get('evidence') and data['commit'] == report['commit'] ==
                check_resource(record, attempt['resource']), 'independent verification/commit mismatch')
        task['verified'] = True
        attempt['status'] = 'verified'
        record['evidence'].append({'task': data['task'], 'attempt': attempt['id'],
                                   'commit': data['commit'], 'verification': data['evidence']})
    else:
        raise ValueError('unsupported task operation')


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
            require(all(host.get(k) == record['host'][k] for k in ('host', 'session')) and
                    host.get('pane') and data.get('evidence') and data.get('stage'),
                    'revalidated same host/session, stage and evidence required')
            require(Path(git(record['repo'], 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
                    == Path(record['common_dir']), 'canonical repository changed')
            record['evidence'].append({'previous_host': record['host'], 'host': host,
                                       'stage': data['stage'], 'verification': data['evidence']})
            record['host'] = host
            record['stage'] = data['stage']
        elif command == 'operation-intent':
            operations = record.setdefault('operations', {})
            operation_id = identifier(data['operation_id'])
            require(operation_id not in operations, 'operation already intended; inspect before retry')
            require(data['operation'] in ('worktree-create', 'agent-start', 'worktree-remove', 'workspace-close',
                                         'run-create', 'task-create', 'worker-release'),
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
    standalone = {'select': select, 'select-host': select_hosts, 'profiles': profiles,
                  'create': create, 'migrate-orca': migrate_orca, 'orca-task': orca_task}
    result = standalone[command](data) if command in standalone else run_command(command, data)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, IndexError, TypeError, subprocess.SubprocessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
