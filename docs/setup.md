# Setup

The plugin has two halves. Use either or both.

## The Workflows app on this Mac

Nothing to configure: the plugin registers the app's local MCP server
(`http://127.0.0.1:27184/mcp`). It answers while the app is running. Open Workflows, then ask
Claude to `describe_app_state`.

The app only uses folders it was granted. The first time Claude adds a repository, the app shows
a dialog — confirm it once for the repository root and every tracking folder below it is covered.

## A Workflows server

1. Sign in to the server's web app. Account menu → **API keys** → name the key for what will use
   it ("Claude on my Mac") → **Create key**. It is shown once.
2. Put it where the skill reads it:

   ```bash
   mkdir -p ~/.plaiiin/workflows && chmod 700 ~/.plaiiin/workflows
   printf 'WORKFLOWS_URL=%s\nWORKFLOWS_API_KEY=%s\n' 'https://work.example.com' 'twk_…' > ~/.plaiiin/workflows/env
   chmod 600 ~/.plaiiin/workflows/env
   ```

   No trailing slash on the URL.

3. Check it: `scripts/wf GET /api/workspaces` lists the workspaces you can open.

For a second server, keep a second file and point at it for one call:
`WORKFLOWS_ENV=~/.plaiiin/workflows/support.env scripts/wf GET /api/workspaces`.

### What the key can do

A key is its owner: it may do what they may, in every workspace they can open. There is no
read-only key yet. Revoke one in the same place it was made; a revoked key answers `401` at once.
A key cannot list, create or revoke keys.
