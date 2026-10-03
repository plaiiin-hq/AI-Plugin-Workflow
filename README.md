# plaiiin Workflows for Claude Code

Work with plaiiin Workflows from Claude: tickets, their states and the views over them, kept as
files in a git repository.

| Skill | For | Needs |
|---|---|---|
| `workflows-app` | a repository checked out on this Mac — read, create, move and comment on tickets through the Workflows app | the Workflows app, running |
| `workflows-server` | the same tickets from anywhere, over a Workflows server's REST API | the server's URL and an API key |

Both write changes the workspace's history can explain: the app signs with this Mac's device key,
the server commits in the name of the key's owner. Neither skill edits ticket files by hand.

## Install

```
/plugin marketplace add plaiiin-hq/plaiiin-workflows-plugin
/plugin install plaiiin-workflows@plaiiin-workflows
```

Then see [docs/setup.md](docs/setup.md).

## Codex

This repository is also a portable Codex plugin. Add it as a marketplace, then install
`plaiiin-workflows` from that source:

```
codex plugin marketplace add plaiiin-hq/plaiiin-workflows-plugin
codex plugin add plaiiin-workflows@plaiiin-workflows
```

Codex uses the same skills and local Workflows MCP endpoint as Claude Code.

## What is in here

- `skills/workflows-app/` — driving the app over its local MCP server (registered by this plugin
  as `workflows`, at `http://127.0.0.1:27184/mcp`).
- `skills/workflows-server/` — the REST API, with `references/api.md` listing every call.
- `scripts/wf` — one call to a server with your key; the exit code says whether it worked.

## License

Apache-2.0.
