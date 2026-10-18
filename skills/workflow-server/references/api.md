# Workflow server — the API

Everything is under `/api/`, takes `X-API-Key`, and speaks JSON. `<ws>` is a workspace id from
`GET /api/workspaces`. Paths under "the workflow surface" are relative to
`/api/workspaces/<ws>/workflows`.

## You and your workspaces

| Call | Answer |
|---|---|
| `GET /api/me` | `email`, `displayName`, `admin` |
| `GET /api/workspaces` | each workspace: `id`, `name`, `access`, `available`, optional `group`, `icon` |
| `GET /api/workspaces/<ws>/icon` | the workspace's app icon (PNG), when it has one |
| `GET /api/search?q=…` | find a ticket by id or by words of its title, across every workspace you may read: each hit has `workspace`, `type`, `id`, `title`, `state`. An exact id first; at most 20 (`limit` is ignored, no total). A `<field>=<value>` word filters on that field — `me`, `empty` or an address, by the type's own field name; `state` is not a field, so "unassigned in active" is not one query: list the type (`GET …/workflows/<type>`) per workspace and filter the `fields` yourself, until WF-144 |
| `GET /api/workspaces/<ws>/docs` | the workspace's documents (architecture, plans, notes): `path` from its root and `title`. Read one with `GET …/docs/content?path=<path>` → `markdown`. Read only |
| `GET /api/me/keys` · `POST /api/me/keys` · `DELETE /api/me/keys/<id>` | your API keys — **signed in only; a key gets `403`** |

## The workflow surface

| Call | What |
|---|---|
| `GET /types` | the types: `id`, `name`, `icon` |
| `GET /types/<type>` | one type in full: `fields`, `nodes`, `edges` |
| `GET /field-types` | the field types the workspace knows |
| `GET /people` (`?q=`) | the people a user field may name — everyone with access to the workspace: `id` (the address a field stores), `name`, `initials`, `roles`; you first |
| `GET /<type>` (`?state=`, `?archived=true`) | instances of a type |
| `GET /<type>/<id>` | `{ instance, timeline, trail }` |
| `POST /<type>` | create — `{"fields": {…}}`, optional `"id"` |
| `PATCH /<type>/<id>/fields` | `{"fields": {…}, "version": n}` |
| `POST /<type>/<id>/transitions` | `{"to": "<state>", "version": n}` |
| `POST /<type>/<id>/comments` | `{"text": "…"}`, optional `"audience"` (one the type's access rules declare) |
| `POST /<type>/<id>/actions/<action>` | run an action the type declares — `{"params": {…}}` |
| `DELETE /<type>/<id>` · `POST /<type>/<id>/unarchive` | archive · restore |
| `POST /<type>/<id>/attach` · `DELETE /<type>/<id>/attach/<kind>/<refId>` | attach or detach a reference — `{"kind": "…", "id": "…"}` |
| `POST /<type>/<id>/fields/<field>/files` · `GET …/files/<name>` · `DELETE …/files/<name>` | files in a file field |
| `POST /types` · `PUT /types/<type>` | create or replace a type — needs the workspace's types-admin role. `PUT` takes the whole type: `GET` it, change `fields`, send it back. It is a signed, approved rule change; the server commits `<type>: template updated` and the type reads back within seconds, not at once (2026-10-18: `assignee` was added to every project's `task` this way) |
| `GET /<type>/<id>/watch` · `PUT …/watch` · `DELETE …/watch` | your watch on a ticket (404: not watching) — `{"comments": true, "states": ["done"], "fields": null}`; for `states`/`fields`, `null` is never and `[]` is any |

An instance: `id`, `type`, `state`, `version`, `fields`, `createdBy`, `createdAt`, `updatedAt`.

**User fields** (type `user`): a field holds a person by their address — `"assignee": "alex@plaiiin.com"` — or, when its `format.multiple` is true, a list of them. Write any user field by its name, as you do every field; the server refuses a stranger (`422 unknown_user`) and someone outside the field's `format.limitTo` (`user_not_allowed`), and a field with `format.from` (`creator`, `lastChangedBy`) is the system's to fill (`403 field_not_editable`). `null` is "no one". A step's `assign` may put the mover into a field: creating a task may make you its assignee, and the move's event says so under `assigned`. Which field "mine" means is the one with `format.mine`.
A timeline entry says what happened (`created`, `transitioned`, `commented`, …), who did it and when.

## Views

| Call | What |
|---|---|
| `GET /api/trees` · `GET /api/trees/<id>` | progress trees that span the workspaces |
| `GET /api/workspaces/<ws>/trees` · `…/trees/<id>` | a workspace's own trees |
| `GET /api/workspaces/<ws>/collections` · `…/collections/<id>` | its collections |

A tree answers `metrics` (the columns: `id`, `label`, `as` — `number`, `percent` or `bar`),
`roots` (rows) and `issues`. A row: `kind` (`item`, `group`, `unassigned`), `label`, and for an
item `type`, `instanceId`, `state`, `stateLabel`, plus `workspace` in a tree that spans several;
`leafCount`; `metrics` (column id → number; a `percent` is a fraction 0–1); `children`.
Only leaves are counted, so a parent's numbers are those of the work beneath it.

A collection answers `mode` (`list` or `board`), `sections` (one per query: `label`, `type`,
`items`) and `lanes` (`id`, `label`, `states`). An item: `id`, `type`, `title`, `state`,
`stateLabel`, `updatedAt`, `version` (what a move or a field change must name), and `parent` as
`<type>/<id>` when it links one.

## People and integrity

| Call | What |
|---|---|
| `GET /api/workspaces/<ws>/roles` | `access`: **everyone** who can open the workspace — `id`, `name`, `roles`, and `via`, where each way in comes from (`file` = this workspace's users.json; `grant` with the workspace it names and its `level` — this workspace, or a shared one such as `work`; `role` = a workspace role; `admin` = the server's admin role). `people`, `groups`, `grants` are **only** what the workspace's own users.json holds — on a server where access is given through realm roles they are empty for every workspace, which means "no workspace-specific roles", never "nobody". Then the known `roles` and what you (`me`) may grant |
| `POST /api/workspaces/<ws>/roles` | change them — each change is your own commit |
| `GET /api/workspaces/<ws>/integrity` | `enabled`, and when it is: `open` violations, `resolved`, `canResolve` |
| `POST /api/workspaces/<ws>/integrity/<id>/sign-off` · `…/revert` | accept or undo a violation — trust-file admins only |

## Notifications (yours)

Whoever created or commented on a ticket hears of its comments and moves; a watch adds what it
picked. Never of your own actions — so changes made with your key notify everyone but you.

| Call | What |
|---|---|
| `GET /api/notify/inbox` (`?limit=`, max 200) | `unread`, `items` newest first: `id`, `kind`, `subject`, `text`, `link`, `read` |
| `POST /api/notify/inbox/read` | `{"ids": [n, …]}` or `{"all": true}` |
| `GET /api/notify/preferences` · `PUT …` | per kind (`involved`, `watched`): `timing` (`INSTANT`, `DAILY`, `WEEKLY`, `OFF`) and `channels` (`mail`, `inbox`) on or off; `digestAt`, `digestDay`, `zone`. A PUT changes only what it names |
| `POST /api/notify/test` | one test mail to you, at most one a minute |

