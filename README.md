# plaiiin Workflow

Work with plaiiin Workflow from Claude Code, Codex and ChatGPT: tickets, their states and the
views over them, kept as files in a Git repository.

| Skill | For | Needs |
|---|---|---|
| `workflow-app` | a repository checked out on this Mac — read, create, move and comment on tickets through the Workflow app | the Workflow app, running |
| `workflow-server` | the same tickets from anywhere, over a Workflow server's REST API | the server's URL and an API key |

Both write changes the workspace's history can explain: the app signs with this Mac's device key,
the server commits in the name of the key's owner. Neither skill edits ticket files by hand.

## Claude Code

```
/plugin marketplace add plaiiin-hq/AI-Plugin-Workflow
/plugin install plaiiin-workflow@plaiiin-workflow
```

Then see [docs/setup.md](docs/setup.md).

## Codex and ChatGPT

This is a portable OpenAI plugin for Codex and ChatGPT Desktop. Add this repository as a Codex
marketplace, install `plaiiin-workflow`, then start a new conversation:

```
codex plugin marketplace add plaiiin-hq/AI-Plugin-Workflow
codex plugin add plaiiin-workflow@plaiiin-workflow
```

Codex uses the local Workflow MCP Unix socket while the Mac app is running. ChatGPT needs a Workflow
MCP server reachable at HTTPS or through Secure MCP Tunnel; it cannot reach the local socket directly.
For ChatGPT Desktop, restart the app, open **Plugins Directory**, select this repository's local
marketplace, and install `plaiiin-workflow`. After installation, run the plugin's `setup` skill for
the exact connection and verification steps.

## What is in here

- `skills/workflow-app/` — driving the app over its local MCP server, registered by this plugin as
  `workflow` through the Workflow app's Unix socket.
- `skills/workflow-server/` — the REST API, with `references/api.md` listing every call.
- `scripts/wf` — one call to a server with your key; the exit code says whether it worked.

## License

Apache-2.0.
