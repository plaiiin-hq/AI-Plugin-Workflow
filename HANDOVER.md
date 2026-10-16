# Workflow MCP handover

## What changed

| Area | Commit | State |
|---|---:|---|
| Workflow app | `03cbfb85` | MCP moved from TCP port `27184` to the App-Group Unix socket. |
| Workflow plugin | `554f12e` | Plugin MCP transport changed to `/usr/bin/nc -U …/workflow-mcp.sock`. |
| Workflow plugin | `34bddd6` | Released the transport change as plugin `2.0.2`. |

## Current constraint

Codex loads MCP definitions when a conversation starts. This conversation has the old
`http://127.0.0.1:27184/mcp` definition and cannot hot-reload it. A resumed conversation keeps
that registry; start a **new Codex conversation** after the steps below.

## Restart handover

1. Build and run the Workflow app containing `03cbfb85` (or install a signed build that contains it).
2. Confirm the app socket answers:

   ```sh
   printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}' \
     | /usr/bin/nc -U "$HOME/Library/Group Containers/LA8GX8Y3R9.group.plaiiin/run/workflow-mcp.sock"
   ```

3. Start a new Codex conversation and ask it to list Workflow projects.

## Verification already performed

| Check | Result |
|---|---|
| Socket unit tests | `2` passed |
| Unix-socket `initialize` smoke test | Passed |
| Unix-socket `tools/list` smoke test | Passed; `71` tools returned |
| CI | Not run; commits have not been pushed |

## Notes for the next agent

- The router is packaged for signed builds; Debug builds serve the socket directly because launchd
  will not persist an unsigned router.
- The plugin source has unrelated uncommitted onboarding edits. Preserve them.
- The installed plugin cache is at `~/.codex/plugins/cache/plaiiin-workflow/plaiiin-workflow/2.0.2`.
