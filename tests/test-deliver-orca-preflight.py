#!/usr/bin/env python3
"""Version-derived Orca caller shapes and local process binding invariants."""
import copy
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
SCRIPT = (Path(__file__).resolve().parents[1] / 'skills/flyingnobita-deliver/scripts'
          / 'deliver-orca-preflight.py')
loader = importlib.machinery.SourceFileLoader('preflight', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class PreflightTests(unittest.TestCase):
    def fixture(self):
        env = {'ORCA_TERMINAL_HANDLE': 'term_own', 'ORCA_PANE_KEY': 'tab:leaf', 'CODEX_THREAD_ID': 'thread'}
        status = {'ok': True, '_meta': {'runtimeId': 'runtime'}, 'result': {
            'target': {'kind': 'local'}, 'runtime': {'reachable': True, 'runtimeId': 'runtime',
                                                   'appVersion': '1.4.237'}}}
        terminal = {'ok': True, '_meta': {'runtimeId': 'runtime'}, 'result': {'terminal': {
            'handle': 'term_own', 'connected': True, 'orphaned': False, 'executionHostId': 'local',
            'worktreePath': '/repo', 'tabId': 'tab', 'leafId': 'leaf', 'agentIdentity': 'codex'}}}
        ancestry = [{'pid': 100, 'harness': 'codex', 'identity': dict(env)}]
        current = {'ok': True, '_meta': {'runtimeId': 'runtime'}, 'result': {'run': None}}
        return [env, status, terminal, ancestry, True, '/repo', current]

    def test_terminal_has_no_chat_caller_and_no_run_is_valid(self):
        result = module.classify(*self.fixture())
        self.assertEqual(result['orca'], 'confirmed')
        self.assertEqual(result['host']['pane'], 'term_own')
        self.assertIsNone(result['evidence']['run'])

    def test_structured_session_requires_its_own_live_host_identity(self):
        args = self.fixture()
        args[0]['ORCA_AGENT_SESSION_ID'] = 'chat'
        args[1]['result']['caller'] = {'live': True, 'orcaSessionId': 'orca_session_id:chat'}
        self.assertEqual(module.classify(*args)['surface'], 'chat')
        for caller in ({}, {'live': False}, {'live': True, 'orcaSessionId': 'orca_session_id:sibling'}):
            args[1]['result']['caller'] = caller
            with self.assertRaises(ValueError):
                module.classify(*args)

    def test_stale_foreign_and_ambiguous_context_never_falls_back(self):
        for change in ({'connected': False}, {'orphaned': True}, {'handle': 'sibling'},
                       {'worktreePath': '/other'}, {'leafId': 'other'},
                       {'executionHostId': 'remote'}, {'agentIdentity': 'claude'}):
            args = self.fixture()
            args[2]['result']['terminal'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                module.classify(*args)
        for index, value in ((3, []), (3, self.fixture()[3] * 2), (4, False)):
            args = self.fixture()
            args[index] = value
            with self.assertRaises(ValueError):
                module.classify(*args)
        args = self.fixture()
        args[3][0]['identity']['CODEX_THREAD_ID'] = 'parent'
        with self.assertRaises(ValueError):
            module.classify(*args)
        args = self.fixture()
        args[6]['_meta']['runtimeId'] = 'restarted'
        with self.assertRaises(ValueError):
            module.classify(*args)

    def test_absent_context_never_probes_the_application(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith('ORCA_')}
        result = subprocess.run(['python3', str(SCRIPT)], input=json.dumps({'repo': '/missing'}),
                                text=True, capture_output=True, env=env, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'orca': 'absent'})

    def test_failed_native_resolution_cannot_confirm_a_caller(self):
        for response in ({'ok': False}, {'ok': True, '_meta': {'runtimeId': 'other'}}):
            args = self.fixture()
            args[6] = copy.deepcopy(response)
            with self.assertRaises(ValueError):
                module.classify(*args)


if __name__ == '__main__':
    unittest.main()
