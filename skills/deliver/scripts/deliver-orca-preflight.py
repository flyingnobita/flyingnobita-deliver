#!/usr/bin/env python3
"""Read-only Orca caller preflight. Never chooses a caller from terminal inventory."""
import json
import os
import subprocess
import sys
from pathlib import Path

MARKERS = ('ORCA_AGENT_SESSION_ID', 'ORCA_TERMINAL_HANDLE', 'ORCA_PANE_KEY', 'ORCA_WORKTREE_ID')
IDENTITY = (*MARKERS, 'CODEX_THREAD_ID', 'CLAUDE_CODE_SESSION_ID')
HARNESSES = {'codex': 'codex', 'claude': 'claude', 'agy': 'antigravity'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def process_ancestry():
    result, pid = [], os.getpid()
    seen = set()
    while pid > 1 and pid not in seen:
        seen.add(pid)
        if sys.platform.startswith('linux'):
            root = Path('/proc') / str(pid)
            fields = (root / 'stat').read_text().rsplit(')', 1)[1].split()
            parent = int(fields[1])
            command = (root / 'comm').read_text().strip()
            named = {}
            if command in HARNESSES:
                for entry in (root / 'environ').read_bytes().split(b'\0'):
                    key, sep, value = entry.partition(b'=')
                    name = key.decode(errors='replace')
                    if sep and name in IDENTITY:
                        named[name] = value.decode(errors='replace')
        elif sys.platform == 'darwin':
            row = subprocess.check_output(['ps', '-p', str(pid), '-o', 'ppid=', '-o', 'comm='],
                                          text=True).strip().split(None, 1)
            parent, command = int(row[0]), Path(row[1]).name
            named = {}  # macOS ps exposes ancestry, not a safe parent-environment API.
        else:
            raise ValueError('process ancestry requires Linux or macOS; preserve context for inspection')
        if command in HARNESSES:
            result.append({'pid': pid, 'harness': HARNESSES[command], 'identity': named})
        pid = parent
    return result


def classify(env, status, terminal, ancestors, repo_matches, workspace, run_current):
    require(status.get('ok') is True and status['result']['runtime'].get('reachable') is True,
            'Orca runtime is not reachable')
    require(status['result']['target'].get('kind') == 'local', 'local caller preflight required')
    runtime = status['_meta']['runtimeId']
    require(runtime and status['result']['runtime'].get('runtimeId') == runtime, 'runtime identity mismatch')
    require(repo_matches, 'caller workspace belongs to another repository')
    require(len(ancestors) == 1, 'missing or ambiguous nested harness ancestry')
    executing = ancestors[0]
    for key in ('CODEX_THREAD_ID', 'CLAUDE_CODE_SESSION_ID'):
        parent = executing.get('identity', {}).get(key)
        require(not parent or parent == env.get(key), 'executing harness session mismatch')
    session = env.get('ORCA_AGENT_SESSION_ID')
    if session:
        caller = status['result'].get('caller') or {}
        require(caller.get('live') is True and
                caller.get('orcaSessionId') == 'orca_session_id:' + session.removeprefix('orca_session_id:'),
                'structured session caller is missing, refused or mismatched')
        binding, surface = caller['orcaSessionId'], 'chat'
    else:
        require(terminal and terminal.get('ok') is True and terminal['_meta']['runtimeId'] == runtime,
                'own terminal did not resolve on this runtime')
        live = terminal['result']['terminal']
        handle = env.get('ORCA_TERMINAL_HANDLE')
        require(handle and live.get('handle') == handle and live.get('connected') is True
                and live.get('orphaned') is False, 'own terminal is absent, disconnected or stale')
        require(live.get('executionHostId') == 'local' and
                str(Path(live['worktreePath']).resolve()) == str(Path(workspace).resolve()),
                'terminal workspace or execution host mismatch')
        require(live.get('agentIdentity') == executing['harness'], 'terminal/harness mismatch')
        pane = env.get('ORCA_PANE_KEY')
        require(not pane or pane == live.get('tabId', '') + ':' + live.get('leafId', ''),
                'terminal pane mismatch')
        inherited = executing.get('identity', {})
        require(not inherited or (pane and inherited.get('ORCA_PANE_KEY') == pane)
                or inherited.get('ORCA_TERMINAL_HANDLE') == handle,
                'harness does not descend from this terminal')
        binding, surface = handle, 'terminal'
    # Orca 1.4.256 omits `_meta` from run-current; status already confirmed the runtime.
    run_meta = run_current.get('_meta') or {}
    require(run_current.get('ok') is True and run_meta.get('runtimeId') in (None, runtime),
            'native caller resolution failed or runtime changed')
    return {'orca': 'confirmed', 'surface': surface,
            'host': {'host': 'orca', 'session': runtime, 'pane': binding},
            'evidence': {'workspace': workspace, 'harness': executing['harness'],
                         'harness_pid': executing['pid'],
                         'app_version': status['result']['runtime'].get('appVersion'),
                         'run': run_current['result'].get('run')}}


def native(cli, *args):
    result = subprocess.run([cli, *args, '--json'], capture_output=True, text=True, timeout=20)
    value = json.loads(result.stdout)
    require(result.returncode == 0 and value.get('ok') is True,
            'Orca read failed: ' + str(value.get('error', {}).get('code', 'unavailable')))
    return value


def main():
    data = json.load(sys.stdin)
    env = {key: os.environ.get(key) for key in IDENTITY}
    if not any(env.get(key) for key in MARKERS):
        print(json.dumps({'orca': 'absent'}))
        return
    require(not os.environ.get('ORCA_ENVIRONMENT') and not os.environ.get('ORCA_PAIRING_CODE'),
            'paired runtime selection cannot attest a local caller')
    cli = os.environ.get('ORCA_CLI_COMMAND') or ('orca-dev' if os.environ.get('ORCA_DEV_REPO_ROOT') else 'orca')
    status = native(cli, 'status')
    terminal = None
    if not env.get('ORCA_AGENT_SESSION_ID'):
        require(env.get('ORCA_TERMINAL_HANDLE'), 'terminal context has no inherited caller handle')
        terminal = native(cli, 'terminal', 'show', '--terminal', env['ORCA_TERMINAL_HANDLE'])
    workspace = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
    common = subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], text=True).strip()
    expected = subprocess.check_output(['git', '-C', data['repo'], 'rev-parse',
                                        '--path-format=absolute', '--git-common-dir'], text=True).strip()
    current = native(cli, 'orchestration', 'run-current')
    print(json.dumps(classify(env, status, terminal, process_ancestry(),
                             Path(common).resolve() == Path(expected).resolve(), workspace, current)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, IndexError, subprocess.SubprocessError) as error:
        print(json.dumps({'orca': 'broken', 'error': str(error)}))
        print('Error: Orca caller preflight failed; preserve context and inspect the named check.', file=sys.stderr)
        sys.exit(1)
