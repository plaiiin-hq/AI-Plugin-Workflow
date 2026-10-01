# Workflows server — the API

Everything is under `/api/`, takes `X-API-Key`, and speaks JSON. `<ws>` is a workspace id from
`GET /api/workspaces`. Paths under "the workflow surface" are relative to
`/api/workspaces/<ws>/workflows`.

## You and your workspaces

| Call | Answer |
|---|---|
| `GET /api/me` | `email`, `displayName`, `admin` |
| `GET /api/workspaces` | each workspace: `id`, `name`, `access`, `available`, optional `group`, `icon` |
| `GET /api/workspaces/<ws>/icon` | the workspace's app icon (PNG), when it has one |
| `GET /api/me/keys` · `POST /api/me/keys` · `DELETE /api/me/keys/<id>` | your API keys — **signed in only; a key gets `403`** |

## The workflow surface

| Call | What |
|---|---|
| `GET /types` | the types: `id`, `name`, `icon` |
| `GET /types/<type>` | one type in full: `fields`, `nodes`, `edges` |
| `GET /field-types` | the field types the workspace knows |
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
| `POST /types` · `PUT /types/<type>` | create or replace a type — needs the workspace's types-admin role |

An instance: `id`, `type`, `state`, `version`, `fields`, `createdBy`, `createdAt`, `updatedAt`.
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
| `GET /api/workspaces/<ws>/roles` | people, groups, who may grant what, and what you may grant |
| `POST /api/workspaces/<ws>/roles` | change them — each change is your own commit |
| `GET /api/workspaces/<ws>/integrity` | `enabled`, and when it is: `open` violations, `resolved`, `canResolve` |
| `POST /api/workspaces/<ws>/integrity/<id>/sign-off` · `…/revert` | accept or undo a violation — trust-file admins only |
