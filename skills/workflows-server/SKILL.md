---
name: workflows-server
description: Use when working with tickets on a plaiiin Workflows SERVER over its REST API — listing what is open, reading a ticket and its history, creating one, moving it to another state, commenting, or reading the progress and board views — from any machine, with no checkout of the repository. Covers X-API-Key auth and where the key lives (~/.plaiiin/workflows/env — read that before asking anyone for one), the /api boundary, the version number every write carries, and why a 404 on a workspace usually means "no access" rather than "no such thing". For a repository checked out on this Mac with the Workflows app running, use `workflows-app` instead.
---

# Working a Workflows server

A Workflows server serves **workspaces**. A workspace is a folder in a git repository; in it,
**types** (Task, Epic, Case …) are folders holding a `template.json` — the fields, the states and
the moves between them — and **instances** (the tickets) are folders holding a `data.json` and a
timeline. Every change you make through the server becomes one git commit in that repository,
made in your name.

Use this skill when you have a server URL and a key. If the repository is checked out on this Mac
and the Workflows app is running, `workflows-app` does the same work through the app.

## Access — set once, never asked again

The key and the server live in `~/.plaiiin/workflows/env`, two lines:

```
WORKFLOWS_URL=https://work.example.com
WORKFLOWS_API_KEY=twk_…
```

Keep the folder `700` and the file `600`. Variables of the same name already in the environment
win, so a one-off override works. Only when the file is absent **and** the variables are unset is
it right to ask the person for a key. `docs/setup.md` in this plugin has the commands.

**Getting a key:** signed in to the server's web app, account menu → **API keys** → name it →
*Create key*. The key is shown **once**. A key cannot create, list or revoke keys — that takes
the person, signed in.

**What a key may do:** exactly what its owner may, in every workspace they can open. There is no
narrower key. So treat it as the person: do not paste it into a ticket, a commit or a chat.

## Calling it

`scripts/wf` in this plugin makes one call and tells you plainly whether it worked:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/wf" GET /api/workspaces
"${CLAUDE_PLUGIN_ROOT}/scripts/wf" POST /api/workspaces/<ws>/workflows/task '{"fields":{"title":"…"}}'
```

The body goes to stdout, `HTTP <code>` to stderr, and the exit code is 0 only for a 2xx. Plain
`curl -H "X-API-Key: $WORKFLOWS_API_KEY"` works the same.

⚠️ **Only `/api/…` is the API.** Any other path is the web app and answers `200` with a page —
which looks like success and is not. `wf` refuses such a path.

## Finding your way

| Question | Call |
|---|---|
| Who am I here? | `GET /api/me` |
| Which workspaces may I open, and how? | `GET /api/workspaces` → `id`, `name`, `access` (`read`, `write`, or `submit` for a customer who may only open cases), `group` |
| Which ticket types does a workspace have? | `GET /api/workspaces/<ws>/workflows/types` |
| What are a type's fields, states and moves? | `GET /api/workspaces/<ws>/workflows/types/<type>` → `fields`, `nodes` (states), `edges` (moves: `from`, `to`) |
| The tickets of a type | `GET /api/workspaces/<ws>/workflows/<type>` — add `?state=<id>` to narrow, `?archived=true` for archived ones |
| Where is ticket X, or is there one about Y? | `GET /api/search?q=WF-12` or `?q=words+of+the+title` — every workspace at once. Search before filing, so the same thing is not filed twice |
| One ticket with its history | `GET /api/workspaces/<ws>/workflows/<type>/<id>` → `{ instance, timeline, trail }` |
| What does the project's architecture say? | `GET /api/workspaces/<ws>/docs` → each document's `path` and `title`; `GET …/docs/content?path=<path>` → its `markdown`. Read it before proposing a design that a document already settles |

**Start with the views** when the question is "what is going on" rather than about one ticket —
they are what people look at:

| View | Call | What it gives |
|---|---|---|
| Progress across everything | `GET /api/trees`, then `GET /api/trees/<id>` | one row per project with its epics, features and tasks underneath, and each row's numbers (done, counted, progress as a fraction 0–1) |
| A workspace's progress | `GET /api/workspaces/<ws>/trees`, then `…/trees/<id>` | the same outline for one workspace |
| Board, Now, Overview, Done | `GET /api/workspaces/<ws>/collections`, then `…/collections/<id>` | `sections` of tickets (id, title, state) and the board's `lanes` |

A view holds only what the key's owner may read, so its numbers count that, not everything.

## The repository itself

A server also serves the git repository behind its workspaces, so a checkout needs no account on
the git host:

```bash
git clone https://<server>/api/git/<repository>     # user name: anything · password: the API key
```

`GET /api/workspaces` gives each workspace's `repository` and its `root` folder inside it. Fetch
needs read access, push needs write. Tickets are still changed through the API, not by editing
files in that clone and pushing them.

## Changing things

Every write names the `version` you read; the server refuses a stale one, so you never overwrite
somebody else's change unseen.

| Do | Call | Body |
|---|---|---|
| Create a ticket (lands in the type's start state) | `POST …/workflows/<type>` → `201` | `{"fields": {"title": "…", …}}` |
| Change fields | `PATCH …/workflows/<type>/<id>/fields` | `{"fields": {…}, "version": <n>}` |
| Move it to another state | `POST …/workflows/<type>/<id>/transitions` | `{"to": "<state id>", "version": <n>}` |
| Comment | `POST …/workflows/<type>/<id>/comments` → `204` | `{"text": "…"}` |
| Archive / restore | `DELETE …/workflows/<type>/<id>` → `204` / `POST …/<id>/unarchive` | — |

Before a write:

1. **Read the type first.** Field names, which values a choice field takes and which moves exist
   from the current state are all in `types/<type>` — do not guess them. A move is only possible
   along an edge `from` the ticket's current state.
2. **Read the ticket for its `version`**, then write with it. On `409` re-read and decide again;
   do not just retry with the new number.
3. **Write values the way the type stores them:** a choice is its option's `id`; a link to another
   ticket (a task's `epic`) is that ticket's `id`; "several of a set" is a list of option ids.

## Reading a refusal

| Answer | Means |
|---|---|
| `401` `{"error":"Invalid API key"}` | the key is wrong or was revoked — ask the person, do not hunt for another |
| `401` with no key sent | you forgot the header (or the env file is not loaded) |
| `404` on `/api/workspaces/<ws>/…` | no such workspace **or the key's owner has no access to it** — the server does not say which. `GET /api/workspaces` lists what you can open |
| `403` | you are known, and this is not yours to do (key management with a key; a role you lack) |
| `409` `version_conflict` | someone changed the ticket since you read it — re-read |
| `400` `Unknown target state` | that state does not exist, or there is no move to it from where the ticket is |
| `200` with HTML | you left `/api/` — see above |

## Workspaces with integrity on

A workspace may carry a trust file (`.workflows/trust.json`). Then every commit in it must be
signed by a known device or by the server, and anything else shows up as a **violation** for the
workspace's admins to review (`GET /api/workspaces/<ws>/integrity`).

What that means for you: **change tickets through the server or the app, never by editing the
files in a checkout and committing them yourself.** An edit made that way is a change history
cannot explain — it will be flagged, and someone has to sign it off or revert it.

See `references/api.md` for the full list of calls.
