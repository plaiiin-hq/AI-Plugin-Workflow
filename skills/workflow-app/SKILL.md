---
name: workflow-app
description: Use when working with plaiiin Workflow tickets in a repository checked out on THIS Mac, through the Workflow app's local MCP server (tools named `mcp__workflow__*` or `mcp__plugin_plaiiin-workflow_workflow__*`) — listing and reading tickets, creating one, moving it between states, patching fields, commenting, editing a type's fields, or syncing a signed workspace. Covers that the app must be running, that every tool takes the tracking folder as `workflow_root`, which tools change the repository and which only move the app's selection, and why ticket files are never edited by hand in a signed workspace. With no checkout or no app — only a server URL and a key — use `workflow-server` instead.
---

# Working tickets through the Workflow app

The Workflow app for Mac keeps tickets as files in a git repository and exposes an MCP server on
the Workflow app's Unix socket while it is running. This plugin registers it as the `workflow`
server. Everything you do through it is done **by the app**, as the person at this Mac — and in a
workspace with integrity on, signed with this Mac's device key.

## Before anything else

- **The app must be running.** A connection error means it is closed, not that the tools do not
  exist. Ask the person to open Workflow (or `open -a Workflow`) and try again.
- **`describe_app_state`** orients you: open windows, the focused one, recent folders.
- **`list_projects`** names the folders the app knows. Most tools take one as **`workflow_root`**:
  the absolute path of the tracking folder (the one holding the `<type>.workflow` folders), not
  the repository root.
- The app may only use folders it was granted. `list_folder_grants` shows them;
  `grant_folder_access` / `add_repo` ask for more — the first time, the person confirms a dialog.
- **A repository that is not on this Mac yet:** `clone_repo` (`url`, `into` — a parent folder inside a
  granted one —, `workspace`) clones it whole and adds it. The app signs in itself: an HTTPS host's
  user name and token from its keychain (a dialog asks the person once), ssh through the person's
  granted `~/.ssh`. `status: "needs"` says what the person must do first.

## Reading

| Want | Tool |
|---|---|
| The types in a workspace | `list_types` — its `failed` lists a type whose template does not load, with why; a type missing from `types` is there, not gone |
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

`take_screenshot` renders a Workflow window to a PNG from inside the app. It is a picture of the
app's own window, good for checking a layout; it is not a screen capture.

## Signed workspaces

A workspace with `.workflows/trust.json` has integrity on: every commit must be signed by a known
device or by its server, and the app audits the history. Then:

| Tool | Does |
|---|---|
| `integrity_status` | who this Mac signs as, whether its key is enrolled, open violations, pending rule changes |
| `enrol_device` | starts enrolling this Mac: returns a link the **person** opens and confirms, signed in |
| `sync_workspace` | fetch, fast-forward or a signed merge, push — never a rebase — then re-audit. A workspace no window has open is opened for the call (the enrolment is checked as usual), so no click is needed |
| `resolve_violation` | sign off or revert an open violation, as this Mac's person |

## Git accounts

The accounts the app syncs and clones with over HTTPS (GitHub, Bitbucket, GitLab, a server of one's own). You can see them and choose
which one a host uses; signing in and out stays with the person (Project Settings ▸ Git & Sync). A token never passes through
you or the MCP.

| Tool | Does |
|---|---|
| `git_accounts` | per host: the kind, each account and which is the default; whether the app offers the browser sign-in. No token |
| `set_default_git_account` | makes one account the default for its host — the one sync and clone use. Needed when a host answers **404 for a private repository**: that is the wrong account being used (e.g. a personal account that is not in the organisation), not a missing repository |

## The app's own settings and keys

What the person can configure in Settings, an agent can read and set (per person, in the app, never in a workspace):

| Tool | Does |
|---|---|
| `list_settings` / `set_setting` / `reset_setting` | the app's preferences by key (`board.title_lines`, `commits.idle.seconds`, …) with type, range or options, default; a value that does not fit is refused and says what does. `trust.use_icloud` is the person's, not writable |
| `list_shortcuts` / `set_shortcut` / `clear_shortcut` / `reset_shortcut` | the key of each command (Search, Save, Sync Now, Open Workspace, …); `set_shortcut` takes `key` + `command`/`shift`/`option`/`control`, or `double_tap` (`command`, `option`, `control`, `shift`); refused with the reason when macOS or another command has it, accepted with a `warning` for known clashes. Search is double Shift by default |

`set_workspace_icon` gives a workspace an icon (or clears it with an empty `icon`): an image path; kept as a small PNG next to the workspace's `.workspace` file and named in its `icon` key, else in the app's support folder. The workspace is named by `workspace_id` or exactly by `name`.

## Working a ticket

**Work a ticket in the open, not at the end.** When you start a ticket (move it to its working state), write its plan as checklist items — the sub-tasks you will actually do, one `add_checklist_item` / checklist call each, for a code ticket typically: branch created and pushed · implementation complete · tests written first and passing · branch build green · review done · docs and skills updated. Tick each item the moment it is true, with the commit that made it so (`check_checklist_item`, `commit`), and add an item when you find new work. The ticket then shows where it is part-way, not only before and after; the definition of done (`dod`) stays the bar for closing, and an item you did not do stays open with a note, never ticked.

## Finding work

| Tool | Does |
|---|---|
| `query_instances` | **the one to use for "who works on what" and "what is unassigned in a state"**: filters `states` / `open`, `type_id`, `created_since` / `changed_since`, and `where: [{field, op, value}]` on any field by the name `get_type` shows (`eq` `ne` `in` `empty` `any`; value `me` = the caller); `group_by` a field, `state` or `type` for counts (`(empty)` is its own group); compact rows with `total`, `limit` / `offset`; no `workflow_root` = every workspace. A type that does not declare the field is not in that query, and the reply's `person_fields` names each type's person fields. Example: `{open: true, where: [{field: "<person field>", op: "empty"}], group_by: "state"}` |
| `query_instances` with `needs: true` | **what needs the caller**, each type deciding by its own attention rules (a `*.attention` file at the tracking root: rules `{id, label, when}`, `when` an expression with `me`, `node`, `state`, `fields`); a row says why in `needs` (`[{rule, label}]`); `group_by: "needs"` counts per reason. A type without rules but with a person field gives "Assigned to you" until it declares its own. Wrong files and rules come back in `attention_problems` (file, rule, message) — report them, never ignore them |
| `list_my_work` | the same question for the caller (or `actor`), compact rows with `needs`; the caller is the signer of a trust workspace; `include_finished` also lists finished tickets that hold the caller |
| `search_instances` | free text over ids, text fields and type names; for field filters and counts use `query_instances` |
| `get_timeline` | one instance's audit trail — created, moved, changed, commented — optionally one `kind` |
| `get_actor` | who writes are signed and attributed as, and where that came from |
| `list_pinned_instances` · `pin_instance` · `unpin_instance` | the instances pinned in the app |

For "who works on what" or "what is unassigned in a state" across projects, ask `query_instances` — one call.

🚨 **Never edit ticket files by hand in a signed workspace**, and never commit them with plain
`git`. A change the app or the server did not make is one history cannot explain: it is flagged
as a violation and somebody has to sign it off or revert it. Use the tools above; they write the
timeline entry and the signature that make the change legitimate.

🚨 **Never rebase, amend or force-push** a signed workspace's branch. Rewritten history is itself
a violation. `sync_workspace` is the way to bring it up to date.

## How a card looks

`get_card` shows how a type's cards are drawn: `declared` (its `<type>.card` files), `effective` (what is drawn: the declared slots, the generated default's for the rest) and `defaults`. `set_card` writes the layout, refusing an unknown widget, a field the type lacks or a widget that needs a field and has none, with every reason. A layout is `{leading, lines, trailing, footer, footerSpans}` of widgets (`icon`, `text`, `id`, `state`, `person`, `progress`, `date`, `chips`, `needs`, `spacer`); `footerSpans` says which outer columns (`leading`, `trailing`) the footer reaches under. A slot a layout leaves out keeps the default; an empty list clears it; `reset: true` removes the file. Pass `collection_id` to read or set a **collection's own** layout for the type instead: it lies over the type's slot by slot. Both write plain tracked files, not rule files; sync afterwards.

## A link for the person

To make the app show something, use `open_in_app` or `select_instance`. When the person should open a **web** link instead (a message, a ticket comment, someone on another machine), the address of a ticket on the server is `<WORKFLOW_URL>/app/w/<workspace>/workflows/<type>/<id>` — with `/app`; `/w/…` without it is an error page. `<WORKFLOW_URL>` is in `~/.plaiiin/workflow/env`; the workspace id comes from the server's `GET /api/workspaces`. `workflow-server` has the details.

## App or server?

| Situation | Use |
|---|---|
| The repository is checked out here and the app is running | this skill — changes are signed by this Mac |
| No checkout, another machine, or a scheduled job | `workflow-server` — a URL and an API key |
| Both are possible | prefer the app for work in the checkout you are already editing; `sync_workspace` afterwards so the server sees it |
