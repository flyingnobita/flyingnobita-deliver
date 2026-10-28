#!/usr/bin/env python3
"""Behavior tests through deliver-runtime's JSON CLI."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[1] / 'skills/flyingnobita-deliver/scripts'
          / 'deliver-runtime.py')


class RuntimeTests(unittest.TestCase):
    def call(self, command, payload, ok=True):
        result = subprocess.run(['python3', str(SCRIPT), command], input=json.dumps(payload),
                                text=True, capture_output=True, check=False, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return json.loads(result.stdout) if ok else result.stderr

    def test_host_selection_never_falls_back_from_broken_context(self):
        for herdr, paseo, expected in [('confirmed', 'absent', 'herdr'),
                                        ('absent', 'confirmed', 'paseo')]:
            self.assertEqual(self.call('select', {'herdr': herdr, 'paseo': paseo})['host'], expected)
        for pair in [('broken', 'confirmed'), ('confirmed', 'broken'),
                     ('absent', 'absent'), ('confirmed', 'confirmed')]:
            self.call('select', {**dict(zip(('herdr', 'paseo'), pair)), 'orca': 'absent'}, ok=False)
        self.assertEqual(self.call('select', {'herdr': 'confirmed', 'paseo': 'confirmed',
                                             'choice': 'herdr', 'orca': 'absent'})['host'], 'herdr')

    def test_three_host_selection_requires_all_evidence_and_present_choice(self):
        import itertools
        for states in itertools.product(('absent', 'confirmed'), repeat=3):
            data = dict(zip(('herdr', 'paseo', 'orca'), states))
            present = [h for h, state in data.items() if state == 'confirmed']
            self.call('select-host', data, ok=len(present) == 1)
            for host in ('herdr', 'paseo', 'orca'):
                result = self.call('select-host', {**data, 'choice': host}, ok=host in present)
                if host in present:
                    self.assertEqual(result['host'], host)
        self.call('select-host', {'herdr': 'absent', 'paseo': 'absent'}, ok=False)
        self.call('select-host', {'herdr': 'absent', 'paseo': 'confirmed', 'orca': 'broken'}, ok=False)

    def test_migration_is_a_preview_and_never_increases_authority(self):
        legacy = {'max_workers': 4, 'land_policy': 'merge', 'base_branch': 'release',
                  'question_policy': 'assume-and-record', 'future': {'keep': True},
                  'roles': {'implementer': {'agent': 'codex', 'model': 'chosen'},
                            'reviewer': {'agent': 'claude'}, 'orchestrator': {'model': 'old'},
                            'fixer': {'agent': 'codex', 'effort': 'high'}}}
        result = self.call('migrate-orca', {'legacy': legacy})
        self.assertEqual(result['legacy'], legacy)
        self.assertEqual(result['config']['delivery']['landing'], 'leave')
        self.assertEqual(result['config']['delivery']['max_workers'], 4)
        roles = result['config']['hosts']['orca']['roles']
        self.assertEqual(roles['implementer'], {'harness': 'codex', 'model': 'chosen'})
        self.assertNotIn('orchestrator', roles)
        self.assertNotIn('fixer', roles)
        self.assertEqual(result['missing_roles'], ['planner', 'qa'])
        self.assertTrue(result['decisions'])
        self.assertEqual(result, self.call('migrate-orca', {'legacy': legacy}))
        for value in (0, -1, True, '4'):
            self.call('migrate-orca', {'legacy': {'max_workers': value}}, ok=False)
        self.assertEqual(self.call('migrate-orca', {'legacy': {}})['missing_roles'],
                         ['planner', 'implementer', 'reviewer', 'qa'])
        for invalid in ({'roles': 'wrong'}, {'roles': {'implementer': 'wrong'}}):
            self.assertNotIn('Traceback', self.call('migrate-orca', {'legacy': invalid}, ok=False))

    def test_orca_journal_rejects_duplicate_dispatch_and_stale_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, old = self.setup_run(root)
            original = self.call('show', old)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'}, 'orca_contract': 1,
                'approved': original['approved'], 'profiles': {}, 'base': 'main',
                'branch': 'integration', 'concurrency': 1})
            run = {**old, 'run_id': record['run_id']}
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'build', str(worktree), 'main')
            intent = {**run, 'job': 'build', 'request_id': 'request1', 'native_run': 'run1',
                      'native_task': 'task1', 'role': 'implementer', 'worktree': str(worktree),
                      'branch': 'build', 'base': record['baseline']}
            self.call('orca-intent', intent)
            self.call('orca-intent', intent, ok=False)
            self.call('orca-intent', {**intent, 'job': 'another', 'request_id': 'request2'}, ok=False)
            receipt = {**run, 'job': 'build', 'native_run': 'run1', 'native_task': 'task1',
                       'dispatch': 'dispatch1', 'request_id': 'request1', 'evidence': 'native receipt'}
            self.call('orca-receipt', {**receipt, 'native_task': 'wrong'}, ok=False)
            self.call('orca-receipt', receipt)
            report = {**run, 'job': 'build', 'dispatch': 'dispatch1', 'native_run': 'run1',
                      'native_task': 'task1', 'outcome': 'succeeded', 'commit': record['baseline'],
                      'checks': ['tests passed'], 'questions': [], 'evidence': 'accepted worker_done'}
            self.call('orca-report', {**report, 'dispatch': 'stale'}, ok=False)
            self.call('orca-report', report)
            self.call('orca-report', {**report, 'outcome': 'failed'}, ok=False)
            verify = {**run, 'job': 'build', 'dispatch': 'dispatch1', 'commit': record['baseline'],
                      'host': 'runtime', 'evidence': 'independent suite and red check'}
            self.call('orca-verify', {**verify, 'host': 'other'}, ok=False)
            self.git(worktree, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                     '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', 'changed')
            self.call('orca-verify', verify, ok=False)
            self.assertFalse(self.call('show', run)['orca_jobs']['build']['verified'])

    def test_orca_gate_requires_success_and_no_open_questions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'work', str(worktree), 'main')
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'}, 'orca_contract': 1,
                'profiles': {}, 'base': 'main', 'branch': 'new'})
            run = {**prior, 'run_id': record['run_id']}
            for index, (outcome, questions, passes) in enumerate((
                ('failed', [], False), ('succeeded', ['unanswered'], False), ('succeeded', [], True)
            )):
                job, request, task, dispatch = (f'{prefix}{index}' for prefix in ('job', 'req', 'task', 'dispatch'))
                identity = {**run, 'job': job, 'request_id': request, 'native_run': 'native', 'native_task': task}
                self.call('orca-intent', {**identity, 'role': 'planner', 'worktree': str(worktree),
                                        'branch': 'work', 'base': record['baseline']})
                self.call('orca-receipt', {**identity, 'dispatch': dispatch, 'evidence': 'native receipt'})
                self.call('orca-report', {**identity, 'dispatch': dispatch, 'outcome': outcome,
                          'commit': record['baseline'], 'checks': ['saved plan'], 'questions': questions,
                          'evidence': 'native settlement'})
                verification = {**run, 'job': job, 'dispatch': dispatch, 'commit': record['baseline'],
                                'host': 'runtime', 'evidence': 'independently read plan and inspected code'}
                self.call('orca-verify', verification, ok=passes)
                self.assertEqual(self.call('show', run)['orca_jobs'][job]['verified'], passes)

    def test_run_purposes_authorize_only_their_roles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'work', str(worktree), 'main')
            for purpose, approved, allowed in (
                ('setup', {'setup': 'user requested no-edit profile validation'}, ['smoke']),
                ('review-only', {'review': 'review target against fixed point'}, ['reviewer']),
                ('review-repair', {'review': 'repair standards/spec findings', 'seams': ['CLI']},
                 ['reviewer', 'implementer']),
            ):
                for role in ('smoke', 'planner', 'implementer', 'reviewer', 'qa'):
                    record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                        'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'}, 'orca_contract': 1,
                        'purpose': purpose, 'profiles': {}, 'base': 'main', 'branch': 'new'})
                    run = {**prior, 'run_id': record['run_id']}
                    intent = {**run, 'job': 'job', 'request_id': 'req', 'native_run': 'native',
                              'native_task': 'task', 'role': role, 'worktree': str(worktree),
                              'branch': 'work', 'base': record['baseline']}
                    self.call('orca-intent', intent, ok=False)
                    self.call('approve', {**run, 'approved': approved, 'evidence': 'user request'})
                    self.call('orca-intent', intent, ok=role in allowed)

    def test_proven_pre_dispatch_rejection_releases_capacity_without_fabricated_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'}, 'orca_contract': 1,
                'profiles': {}, 'base': 'main', 'branch': 'new', 'concurrency': 1})
            run = {**prior, 'run_id': record['run_id']}
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'work', str(worktree), 'main')
            intent = {**run, 'job': 'plan', 'request_id': 'req', 'native_run': 'native',
                      'native_task': 'task', 'role': 'planner', 'worktree': str(worktree),
                      'branch': 'work', 'base': record['baseline']}
            self.call('orca-intent', intent)
            reject = {**run, 'job': 'plan', 'request_id': 'req', 'native_run': 'native',
                      'native_task': 'task', 'request_state': 'completed', 'task_state': 'ready',
                      'dispatch_absent': True, 'evidence': 'completed native rejection; no dispatch/resources'}
            for bad in ({'request_state': 'absent'}, {'dispatch_absent': False}, {'request_id': 'wrong'}):
                self.call('orca-rejected', {**reject, **bad}, ok=False)
            self.call('orca-rejected', reject)
            next_intent = {**intent, 'job': 'plan2', 'request_id': 'req2'}
            self.call('orca-intent', {**next_intent, 'native_run': 'other'}, ok=False)
            self.call('orca-intent', next_intent)
            self.call('orca-verify', {**run, 'job': 'plan'}, ok=False)

    def test_strict_orca_packets_artifacts_and_independent_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'},
                'profiles': {'planner': {'harness': 'antigravity', 'model': 'chosen', 'effort': 'medium'}},
                'base': 'main', 'branch': 'new'})
            run = {**prior, 'run_id': record['run_id']}
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'work', str(worktree), 'main')
            artifact = root / 'state' / record['run_id'] / 'plan.md'
            output = artifact.with_name('check.txt')
            packet = {'target': 'fixture CLI', 'change': 'plan its behavior',
                      'constraints': 'read-only; no publishing', 'ownership': 'report only',
                      'acceptance': 'name slices and subprocess seam',
                      'profile': record['profiles']['planner'], 'report_path': str(artifact),
                      'verification_commands': [['git', 'diff', '--check']]}
            compiled = self.call('orca-task', {'packet': packet})
            self.assertIn('Ownership:', compiled['spec'])
            for field in ('target', 'change', 'constraints', 'ownership', 'acceptance',
                          'profile', 'report_path', 'verification_commands'):
                bad = dict(packet)
                bad.pop(field)
                self.call('orca-task', {'packet': bad}, ok=False)
            intent = {**run, 'job': 'plan', 'request_id': 'req', 'native_run': 'native',
                      'native_task': 'task', 'role': 'planner', 'worktree': str(worktree),
                      'branch': 'work', 'base': record['baseline']}
            self.call('orca-intent', intent, ok=False)
            self.call('orca-intent', {**intent, 'packet': {**packet,
                      'profile': {'harness': 'other'}}}, ok=False)
            self.call('orca-intent', {**intent, 'packet': packet})
            self.call('orca-receipt', {**intent, 'dispatch': 'dispatch', 'evidence': 'native receipt'})
            report = {**intent, 'dispatch': 'dispatch', 'outcome': 'succeeded',
                      'commit': record['baseline'], 'checks': ['plan written'], 'questions': [],
                      'artifact_path': str(artifact), 'evidence': 'matching native worker_done'}
            self.call('orca-settle', report, ok=False)
            artifact.write_text('A durable plan at the approved seam.')
            self.call('orca-settle', report)
            self.assertFalse(self.call('show', run)['orca_jobs']['plan']['verified'])
            gate = {**run, 'job': 'plan', 'dispatch': 'dispatch', 'commit': record['baseline'],
                    'host': 'runtime', 'evidence': 'clean HEAD and native success alone'}
            self.call('orca-verify', gate, ok=False)
            output.write_text('Independent git diff --check passed')
            verification = {'stage': 'planner', 'checks': [{'argv': ['git', 'diff', '--check'],
                'exit_code': 0, 'commit': record['baseline'], 'output_path': str(output)}]}
            for bad in ({'stage': 'reviewer'}, {'checks': []}):
                self.call('orca-verify', {**gate, 'verification': {**verification, **bad}}, ok=False)
            for change in ({'exit_code': 1}, {'exit_code': False}, {'commit': 'other'},
                           {'argv': ['git', 'status']}, {'output_path': str(artifact)}):
                bad = {**verification, 'checks': [{**verification['checks'][0], **change}]}
                self.call('orca-verify', {**gate, 'verification': bad}, ok=False)
            artifact.write_text('Changed after settlement')
            self.call('orca-verify', {**gate, 'verification': verification}, ok=False)
            artifact.write_text('A durable plan at the approved seam.')
            self.call('orca-verify', {**gate, 'verification': verification})
            self.assertTrue(self.call('show', run)['orca_jobs']['plan']['verified'])

    def test_strict_review_success_with_findings_is_not_a_clean_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            profile = {'harness': 'antigravity', 'model': 'chosen', 'effort': 'medium'}
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'},
                'purpose': 'review-only', 'profiles': {'reviewer': profile}, 'base': 'main', 'branch': 'new'})
            run = {**prior, 'run_id': record['run_id']}
            self.call('approve', {**run, 'approved': {'review': 'user requested this fixed-point review'},
                                 'evidence': 'user request'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'review', str(worktree), 'main')
            artifact = root / 'state' / record['run_id'] / 'review.md'
            artifact.write_text('Spec: one Must-fix. Standards: clean.')
            output = artifact.with_name('independent.txt')
            output.write_text('Independent checks passed; review finding still open.')
            packet = {'target': 'fixed point and current branch', 'change': 'review both axes',
                      'constraints': 'read-only', 'ownership': 'report only', 'acceptance': 'all findings cited',
                      'profile': profile, 'report_path': str(artifact),
                      'verification_commands': [['git', 'diff', '--check']]}
            intent = {**run, 'job': 'review', 'request_id': 'req', 'native_run': 'native',
                      'native_task': 'task', 'role': 'reviewer', 'worktree': str(worktree),
                      'branch': 'review', 'base': record['baseline'], 'packet': packet}
            self.call('orca-intent', intent)
            self.call('orca-receipt', {**intent, 'dispatch': 'dispatch', 'evidence': 'native receipt'})
            self.call('orca-settle', {**intent, 'dispatch': 'dispatch', 'outcome': 'succeeded',
                      'commit': record['baseline'], 'checks': ['findings delivered'], 'questions': [],
                      'artifact_path': str(artifact), 'evidence': 'native success'})
            gate = {**run, 'job': 'review', 'dispatch': 'dispatch', 'commit': record['baseline'],
                    'host': 'runtime', 'evidence': 'independent report inspection'}
            proof = {'stage': 'reviewer', 'verdict': 'findings', 'must_fix': 1, 'checks': [{
                'argv': ['git', 'diff', '--check'], 'exit_code': 0, 'commit': record['baseline'],
                'output_path': str(output)}]}
            self.call('orca-verify', {**gate, 'verification': proof}, ok=False)
            self.assertFalse(self.call('show', run)['orca_jobs']['review']['verified'])

    def test_orca_resource_mutations_can_be_journaled(self):
        with tempfile.TemporaryDirectory() as directory:
            _, run = self.setup_run(Path(directory))
            for operation in ('run-create', 'task-create', 'worker-release'):
                payload = {**run, 'operation_id': operation, 'operation': operation,
                           'target': {'request_id': operation + '-request'}}
                self.call('operation-intent', payload)
                self.call('operation-intent', payload, ok=False)
                self.call('operation-result', {**payload, 'result': {'native_receipt': 'observed'}})

    def test_direct_preflight_rejection_can_resolve_an_unrecorded_request(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, prior = self.setup_run(root)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                'host': {'host': 'orca', 'session': 'runtime', 'pane': 'caller'}, 'orca_contract': 1,
                'profiles': {}, 'base': 'main', 'branch': 'new', 'concurrency': 1})
            run = {**prior, 'run_id': record['run_id']}
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'work', str(worktree), 'main')
            intent = {**run, 'job': 'plan', 'request_id': 'req', 'native_run': 'native',
                      'native_task': 'task', 'role': 'planner', 'worktree': str(worktree),
                      'branch': 'work', 'base': record['baseline']}
            self.call('orca-intent', intent)
            rejection = {'ok': False, 'error': {'code': 'task_not_startable', 'data': {
                'taskId': 'task', 'status': 'pending', 'orchestrationRequestId': 'req'}}}
            payload = {**intent, 'request_state': 'absent', 'task_state': 'pending',
                       'dispatch_absent': True, 'preflight_rejection': rejection,
                       'evidence': 'direct refusal plus native task and resource inspection'}
            for change in ({'preflight_rejection': None}, {'request_state': 'pending'},
                           {'dispatch_absent': False}, {'task_state': 'ready'}):
                self.call('orca-rejected', {**payload, **change}, ok=False)
            for change in ({'taskId': 'other'}, {'orchestrationRequestId': 'other'}):
                bad = json.loads(json.dumps(rejection))
                bad['error']['data'].update(change)
                self.call('orca-rejected', {**payload, 'preflight_rejection': bad}, ok=False)
            bad = json.loads(json.dumps(rejection))
            bad['error']['code'] = 'runtime_error'
            self.call('orca-rejected', {**payload, 'preflight_rejection': bad}, ok=False)
            self.call('orca-rejected', payload)
            saved = self.call('show', run)['orca_jobs']['plan']
            self.assertEqual(saved['rejection']['preflight_rejection'], rejection)
            self.assertNotIn('report', saved)
            self.call('orca-intent', {**intent, 'job': 'next', 'request_id': 'next'})

    def test_concurrency_is_validated_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            original = self.call('show', run)
            payload = {'state_root': str(root / 'state'), 'repo': str(repo),
                       'host': original['host'], 'profiles': {}, 'base': 'main', 'branch': 'new'}
            for value in (0, -2, True, '4'):
                self.call('create', {**payload, 'concurrency': value}, ok=False)
            created = self.call('create', {**payload, 'concurrency': 4})
            self.assertEqual(self.call('show', {**run, 'run_id': created['run_id']})['concurrency'], 4)

    def test_profiles_merge_whole_role_and_compile_native_flags(self):
        profile = {'harness': 'codex', 'model': 'gpt-6.1-sol', 'effort': 'medium',
                   'mode': 'full-access'}
        data = {'defaults': {'implementer': profile},
                'project': {'implementer': {'effort': 'high'}},
                'run': {'implementer': {'effort': 'low'}}}
        result = self.call('profiles', data)['implementer']
        self.assertEqual(result['profile']['effort'], 'low')
        self.assertIn('--dangerously-bypass-approvals-and-sandbox', result['argv'])
        self.assertFalse(result['availability_verified'])
        for override in [{'effort': 'magic'}, {'mode': 'plan'}, {'features': {'unknown': True}},
                         {'provider': 'unsupported'}, {'extra': 'ignored?'}]:
            self.call('profiles', {**data, 'run': {'implementer': override}}, ok=False)
        result = self.call('profiles', {'defaults': {'planner': {
            'harness': 'claude', 'model': 'claude-opus-5-5', 'effort': 'high', 'mode': 'plan'}}})
        self.assertIn('plan', result['planner']['argv'])
        agy = {'harness': 'agy', 'model': 'gemini-3.8-flash-high', 'effort': 'high',
               'mode': 'dangerously-skip-permissions'}
        result = self.call('profiles', {'defaults': {'implementer': agy}})['implementer']
        self.assertEqual(result['argv'], ['--model', 'gemini-3.8-flash-high', '--effort', 'high',
                                          '--dangerously-skip-permissions'])
        for override in [{'mode': 'full-access'}, {'effort': 'magic'}]:
            self.call('profiles', {'defaults': {'implementer': {**agy, **override}}}, ok=False)

    def git(self, repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

    def setup_run(self, root):
        repo = root / 'repo'
        repo.mkdir()
        self.git(repo, 'init', '-q', '-b', 'main')
        self.git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                 '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', 'base')
        payload = {'state_root': str(root / 'state'), 'repo': str(repo),
                   'host': {'host': 'herdr', 'session': 'fixture', 'pane': 'w1:p1'},
                   'approved': {'brief': 'fixture', 'plan': 'fixture', 'seams': ['CLI']},
                   'profiles': {}, 'base': 'main', 'branch': 'main'}
        run = self.call('create', payload)
        return repo, {'state_root': str(root / 'state'), 'run_id': run['run_id']}

    def test_run_records_are_private_and_survive_a_second_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            record = self.call('show', run)
            self.assertEqual(record['repo'], str(repo.resolve()))
            self.assertEqual(record['schema'], 1)
            self.assertEqual(record['baseline'], self.git(repo, 'rev-parse', 'HEAD'))
            self.assertEqual((root / 'state' / run['run_id']).stat().st_mode & 0o777, 0o700)
            self.call('task', {**run, 'task': 'build', 'dependencies': []})
            self.call('task', {**run, 'task': 'build', 'dependencies': []}, ok=False)
            self.assertEqual(self.call('show', run)['tasks']['build']['recoveries'], 0)
            self.call('show', {**run, 'run_id': '../escape'}, ok=False)

    def test_dispatch_intent_blocks_duplicate_and_uncertain_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'deliver-build', str(worktree), 'main')
            binding = {'worktree': str(worktree), 'branch': 'deliver-build',
                       'workspace': 'w2', 'pane': 'w2:p1', 'agent': 'delivery-build',
                       'session': 'fixture'}
            payload = {**run, 'task': 'build', 'resource': binding}
            attempt = self.call('attempt', payload)['tasks']['build']['attempts'][0]
            dispatch = {**run, 'task': 'build', 'attempt': attempt['id'], 'prompt': 'implement'}
            self.call('dispatch-intent', dispatch)
            self.call('dispatch-intent', dispatch, ok=False)
            self.call('recover', {**run, 'task': 'build'}, ok=False)
            self.assertEqual(self.call('show', run)['tasks']['build']['recoveries'], 0)

    def test_reports_need_matching_attempt_commit_and_independent_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'deliver-build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'deliver-build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'delivery-build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            payload = {**run, 'task': 'build', 'attempt': attempt['id']}
            self.call('dispatch-intent', {**payload, 'prompt': 'implement'})
            report = {'run_id': run['run_id'], 'task': 'build', 'attempt': attempt['id'],
                      'commit': self.git(worktree, 'rev-parse', 'HEAD'),
                      'checks': [{'command': 'fixture', 'result': 'passed'}], 'questions': []}
            self.call('report', {**payload, 'report': {**report, 'attempt': 'stale'}}, ok=False)
            self.call('report', {**payload, 'report': report})
            self.assertFalse(self.call('show', run)['tasks']['build']['verified'])
            self.call('verify', {**payload, 'commit': report['commit'],
                                 'evidence': 'independent fixture check', 'host': resource['session']})
            self.assertTrue(self.call('show', run)['tasks']['build']['verified'])
            self.assertTrue(Path(attempt['report_path']).is_file())
            self.call('task', {**run, 'task': 'review', 'dependencies': ['build']})
            self.call('attempt', {**run, 'task': 'review', 'resource': {**resource, 'agent': 'review'}})

    def test_recovery_requires_reconciliation_and_persists_two_attempt_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            for index in range(3):
                worktree = root / f'worker{index}'
                branch = f'deliver-build-{index}'
                self.git(repo, 'worktree', 'add', '-q', '-b', branch, str(worktree), 'main')
                resource = {'worktree': str(worktree), 'branch': branch, 'workspace': f'w{index+2}',
                            'pane': f'w{index+2}:p1', 'agent': f'build-{index}', 'session': 'fixture'}
                attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][-1]
                payload = {**run, 'task': 'build', 'attempt': attempt['id']}
                self.call('dispatch-intent', {**payload, 'prompt': 'build'})
                evidence = {'session': 'fixture', 'resource': resource, 'agent_state': 'exited',
                            'commit': attempt['base'], 'dispatch': 'not-submitted'}
                self.call('reconcile', {**payload, 'observation': evidence})
                self.call('recover', {**run, 'task': 'build'}, ok=index < 2)
            self.assertEqual(self.call('show', run)['tasks']['build']['recoveries'], 2)

    def test_existing_work_and_uncertain_dispatch_cannot_be_recovered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'deliver-build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'deliver-build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            payload = {**run, 'task': 'build', 'attempt': attempt['id']}
            self.call('dispatch-intent', {**payload, 'prompt': 'build'})
            observation = {'session': 'fixture', 'resource': resource, 'agent_state': 'exited',
                           'commit': attempt['base'], 'dispatch': 'uncertain'}
            self.call('reconcile', {**payload, 'observation': observation})
            self.call('recover', {**run, 'task': 'build'}, ok=False)
            (worktree / 'work.txt').write_text('preserve me')
            self.call('reconcile', {**payload, 'observation': {**observation, 'dispatch': 'not-submitted'}})
            self.call('recover', {**run, 'task': 'build'}, ok=False)

    def test_native_prompt_timeout_is_durable_and_never_resubmitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'deliver-build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'deliver-build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            fake = root / 'herdr'
            log = root / 'calls.jsonl'
            fake.write_text('#!/usr/bin/env python3\nimport json,sys\nfrom pathlib import Path\n'
                            f'log=Path({str(log)!r})\n'
                            'with log.open("a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
                            'if sys.argv[1:3] == ["agent", "get"]:\n'
                            ' print(json.dumps({"result":{"agent":{"pane_id":"w2:p1",'
                            '"workspace_id":"w2","agent_status":"idle",'
                            '"agent_session":{"value":"worker-session"}}}}))\n'
                            'else: sys.exit(1)\n')
            fake.chmod(0o700)
            payload = {**run, 'task': 'build', 'attempt': attempt['id'], 'prompt': 'literal; $(no shell)',
                       'herdr_bin': str(fake), 'worker_session': 'worker-session', 'timeout_ms': 100}
            record = self.call('prompt', payload)
            self.assertEqual(record['tasks']['build']['attempts'][0]['status'], 'dispatch-uncertain')
            self.call('prompt', payload, ok=False)
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            prompts = [args for args in calls if args[:2] == ['agent', 'prompt']]
            self.assertEqual(len(prompts), 1)
            self.assertEqual(prompts[0][2:4], ['w2:p1', 'literal; $(no shell)'])

    def test_cleanup_checks_tree_landing_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'deliver-build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'deliver-build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            payload = {**run, 'task': 'build', 'attempt': attempt['id']}
            self.call('dispatch-intent', {**payload, 'prompt': 'build'})
            self.call('cleanup-check', {**payload, 'observation': resource, 'landed': 'main'}, ok=False)
            report = {'run_id': run['run_id'], 'task': 'build', 'attempt': attempt['id'],
                      'commit': attempt['base'], 'checks': ['passed'], 'questions': []}
            self.call('report', {**payload, 'report': report})
            self.call('verify', {**payload, 'commit': report['commit'], 'host': 'fixture', 'evidence': 'checked'})
            self.call('cleanup-check', {**payload, 'observation': {**resource, 'pane': 'another'}, 'landed': 'main'}, ok=False)
            self.call('cleanup-check', {**payload, 'observation': resource, 'landed': 'main'})
            (worktree / 'preserve').write_text('dirty')
            self.call('cleanup-check', {**payload, 'observation': resource, 'landed': 'main'}, ok=False)
            self.assertTrue(Path(attempt['report_path']).exists())

    def test_single_writer_lock_rejects_another_process(self):
        import time
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            fake, submitted, release = root / 'herdr', root / 'submitted', root / 'release'
            fake.write_text('#!/usr/bin/env python3\nimport json,sys,time\nfrom pathlib import Path\n'
                            'if sys.argv[1:3] == ["agent", "get"]:\n'
                            ' print(json.dumps({"result":{"agent":{"pane_id":"w2:p1",'
                            '"workspace_id":"w2","agent_status":"idle",'
                            '"agent_session":{"value":"worker"}}}}))\n'
                            'else:\n'
                            f' Path({str(submitted)!r}).touch()\n'
                            f' while not Path({str(release)!r}).exists(): time.sleep(0.01)\n'
                            ' sys.exit(1)\n')
            fake.chmod(0o700)
            payload = {**run, 'task': 'build', 'attempt': attempt['id'], 'prompt': 'build',
                       'worker_session': 'worker', 'herdr_bin': str(fake), 'timeout_ms': 5000}
            process = subprocess.Popen(['python3', str(SCRIPT), 'prompt'], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                process.stdin.write(json.dumps(payload))
                process.stdin.close()
                deadline = time.monotonic() + 5
                while not submitted.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(submitted.exists(), 'recording Herdr did not receive prompt')
                self.assertIn('another orchestrator', self.call('task', {**run, 'task': 'other'}, ok=False))
            finally:
                release.touch()
                process.wait(timeout=10)
                process.stdout.close()
                process.stderr.close()
            self.assertNotIn('other', self.call('show', run)['tasks'])

    def test_dependency_frontier_and_parallel_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            for index in range(4):
                self.call('task', {**run, 'task': f'task{index}'})
                worktree = root / f'worker{index}'
                branch = f'deliver-{index}'
                self.git(repo, 'worktree', 'add', '-q', '-b', branch, str(worktree), 'main')
                resource = {'worktree': str(worktree), 'branch': branch, 'workspace': f'w{index}',
                            'pane': f'w{index}:p1', 'agent': f'worker{index}', 'session': 'fixture'}
                self.call('attempt', {**run, 'task': f'task{index}', 'resource': resource}, ok=index < 3)
            self.call('task', {**run, 'task': 'dependent', 'dependencies': ['task0']})
            self.call('attempt', {**run, 'task': 'dependent', 'resource': resource}, ok=False)

    def test_resource_mutation_intents_require_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            _, run = self.setup_run(Path(directory))
            intent = {**run, 'operation_id': 'create-build', 'operation': 'worktree-create',
                      'target': {'branch': 'deliver-build', 'path': '/fixture/build'}}
            self.call('operation-intent', intent)
            self.call('operation-intent', intent, ok=False)
            self.call('operation-result', {**run, 'operation_id': 'create-build',
                                           'result': {'workspace': 'w2', 'pane': 'w2:p1'}})
            self.assertEqual(self.call('show', run)['operations']['create-build']['status'], 'observed')

    def test_resume_checkpoint_records_replacement_without_switching_host(self):
        with tempfile.TemporaryDirectory() as directory:
            _, run = self.setup_run(Path(directory))
            data = {**run, 'stage': 'review', 'evidence': 'revalidated actual caller and repo',
                    'host': {'host': 'herdr', 'session': 'fixture', 'pane': 'w3:p1'}}
            record = self.call('checkpoint', data)
            self.assertEqual(record['host']['pane'], 'w3:p1')
            self.assertEqual(record['stage'], 'review')
            self.call('checkpoint', {**data, 'host': {**data['host'], 'session': 'another'}}, ok=False)

    def test_run_can_record_intended_branch_before_worktree_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            original = self.call('show', run)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                                         'base': 'main', 'branch': 'deliver-new',
                                         'host': original['host'], 'approved': original['approved'], 'profiles': {}})
            self.assertEqual(record['branch'], 'deliver-new')
            self.assertEqual(self.git(repo, 'branch', '--list', 'deliver-new'), '')

    def test_draft_run_can_plan_before_recording_user_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, existing = self.setup_run(root)
            original = self.call('show', existing)
            record = self.call('create', {'state_root': str(root / 'state'), 'repo': str(repo),
                                         'base': 'main', 'branch': 'draft',
                                         'host': original['host'], 'profiles': {}})
            run = {**existing, 'run_id': record['run_id']}
            self.assertEqual(record['approved'], {})
            worktree = root / 'planner'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'plan', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'plan', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'planner', 'session': 'fixture'}
            self.call('task', {**run, 'task': 'build'})
            error = self.call('attempt', {**run, 'task': 'build', 'resource': resource}, ok=False)
            self.assertIn('approved plan', error)
            self.call('task', {**run, 'task': 'planner', 'role': 'planner'})
            self.call('attempt', {**run, 'task': 'planner', 'resource': resource})
            result = self.call('approve', {**run, 'approved': original['approved'],
                                          'evidence': 'user approved brief, plan and seams'})
            self.assertEqual(result['approved']['seams'], ['CLI'])

    def test_answered_question_allows_followup_and_keeps_original_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, run = self.setup_run(root)
            self.call('task', {**run, 'task': 'build'})
            worktree = root / 'worker'
            self.git(repo, 'worktree', 'add', '-q', '-b', 'build', str(worktree), 'main')
            resource = {'worktree': str(worktree), 'branch': 'build', 'workspace': 'w2',
                        'pane': 'w2:p1', 'agent': 'build', 'session': 'fixture'}
            attempt = self.call('attempt', {**run, 'task': 'build', 'resource': resource})['tasks']['build']['attempts'][0]
            payload = {**run, 'task': 'build', 'attempt': attempt['id']}
            self.call('dispatch-intent', {**payload, 'prompt': 'build'})
            report = {'run_id': run['run_id'], 'task': 'build', 'attempt': attempt['id'],
                      'commit': attempt['base'], 'checks': ['read plan'], 'questions': ['Which name?']}
            self.call('report', {**payload, 'report': report})
            self.call('verify', {**payload, 'commit': attempt['base'], 'host': 'fixture', 'evidence': 'checked'}, ok=False)
            self.call('followup', {**payload, 'evidence': 'answer from approved plan: name is greeting'})
            record = self.call('show', run)
            followup = record['tasks']['build']['attempts'][-1]
            self.assertNotEqual(followup['id'], attempt['id'])
            self.assertEqual(record['tasks']['build']['recoveries'], 0)
            self.assertEqual(json.loads(Path(attempt['report_path']).read_text()), report)
            payload = {**run, 'task': 'build', 'attempt': followup['id']}
            self.call('dispatch-intent', {**payload, 'prompt': 'answer: greeting; continue'})
            self.call('report', {**payload, 'report': {**report, 'attempt': followup['id'], 'questions': []}})
            self.call('verify', {**payload, 'commit': attempt['base'], 'host': 'fixture', 'evidence': 'independent checked'})


if __name__ == '__main__':
    unittest.main()
