---
name: workflows-app
description: Use when working with plaiiin Workflows tickets in a repository checked out on THIS Mac, through the Workflows app's local MCP server (tools named `mcp__workflows__*` or `mcp__plugin_plaiiin-workflows_workflows__*`) — listing and reading tickets, creating one, moving it between states, patching fields, commenting, editing a type's fields, or syncing a signed workspace. Covers that the app must be running, that every tool takes the tracking folder as `workflow_root`, which tools change the repository and which only move the app's selection, and why ticket files are never edited by hand in a signed workspace. With no checkout or no app — only a server URL and a key — use `workflows-server` instead.
---

# Working tickets through the Workflows app

The Workflows app for Mac keeps tickets as files in a git repository and exposes an MCP server on
`http://127.0.0.1:27184/mcp` while it is running. This plugin registers it as the `workflows`
server. Everything you do through it is done **by the app**, as the person at this Mac — and in a
workspace with integrity on, signed with this Mac's device key.

## Before anything else

- **The app must be running.** A connection error means it is closed, not that the tools do not
  exist. Ask the person to open Workflows (or `open -a Workflows`) and try again.
- **`describe_app_state`** orients you: open windows, the focused one, recent folders.
- **`list_projects`** names the folders the app knows. Most tools take one as **`workflow_root`**:
  the absolute path of the tracking folder (the one holding the `<type>.workflow` folders), not
  the repository root.
- The app may only use folders it was granted. `list_folder_grants` shows them;
  `grant_folder_access` / `add_repo` ask for more — the first time, the person confirms a dialog.

## Reading

| Want | Tool |
|---|---|
| The types in a workspace | `list_types` |
| A type's fields, states and moves | `get_type` — read this before writing; do not guess field names or state ids |
| Tickets of a type (by state, archived or not) | `list_instances` |
| One ticket with its history | `get_instance` |
| Markdown docs in the workspace | `list_docs`, `get_doc_content` |
| Data stores (tables beside the tickets) | `list_stores`, `get_store`, `list_data_store_rows` |

## Changing tickets

| Do | Tool |
|---|---|
| Create a ticket (lands in the start state) | `create_instance` |
| Move it to another state — optionally with a field patch in the same change | `transition` |
| Change fields without moving it | `patch_fields` |
| Comment | `add_comment` |
| Archive / restore | `archive`, `unarchive` |

A move is only possible along an edge from the ticket's current state — `get_type` lists them.
A choice field takes its option's `id`; a link field takes the target ticket's `id`.

Each of these is one commit in the repository, made by the app. **Do not also `git add` or
`git commit` the files it wrote** — they are already committed.

## Changing a type

`add_workflow_field`, `set_workflow_field`, `set_workflow_field_options`, `rename_workflow_field`,
`change_workflow_field_type`, `reorder_workflow_fields`, `remove_workflow_field`, and
`create_type` for a new one. `rename_workflow_field` renames the stored key on every ticket;
to change only what people see, set `labels` with `set_workflow_field`.

In a signed workspace a change to a type is a **rule change**: it takes effect once a trust-file
admin has approved it. Until then it is listed as pending (`integrity_status`).

## Showing the person something

`select`, `select_type`, `select_instance`, `select_collection`, `select_doc`, `open_in_app`,
`open_flow_editor`, `open_project_settings`, `switch_workspace` move what the **app shows**. They
change nothing in the repository. `get_selection` reads back what is selected — useful when the
person says "this one".

`take_screenshot` renders a Workflows window to a PNG from inside the app. It is a picture of the
app's own window, good for checking a layout; it is not a screen capture.

## Signed workspaces

A workspace with `.workflows/trust.json` has integrity on: every commit must be signed by a known
device or by its server, and the app audits the history. Then:

| Tool | Does |
|---|---|
| `integrity_status` | who this Mac signs as, whether its key is enrolled, open violations, pending rule changes |
| `enrol_device` | starts enrolling this Mac: returns a link the **person** opens and confirms, signed in |
| `sync_workspace` | fetch, fast-forward or a signed merge, push — never a rebase — then re-audit |
| `resolve_violation` | sign off or revert an open violation, as this Mac's person |

🚨 **Never edit ticket files by hand in a signed workspace**, and never commit them with plain
`git`. A change the app or the server did not make is one history cannot explain: it is flagged
as a violation and somebody has to sign it off or revert it. Use the tools above; they write the
timeline entry and the signature that make the change legitimate.

🚨 **Never rebase, amend or force-push** a signed workspace's branch. Rewritten history is itself
a violation. `sync_workspace` is the way to bring it up to date.

## App or server?

| Situation | Use |
|---|---|
| The repository is checked out here and the app is running | this skill — changes are signed by this Mac |
| No checkout, another machine, or a scheduled job | `workflows-server` — a URL and an API key |
| Both are possible | prefer the app for work in the checkout you are already editing; `sync_workspace` afterwards so the server sees it |
