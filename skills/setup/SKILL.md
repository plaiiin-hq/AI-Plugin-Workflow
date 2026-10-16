---
name: setup
description: Connect plaiiin Workflow to Codex or ChatGPT, then verify that ticket tools are available.
---

# Set up plaiiin Workflow

Use this skill immediately after installing the plugin, or when its `workflow` tools are missing.

## Codex on this Mac

1. Open the Workflow Mac app. It exposes its local MCP server through the plugin's Unix-socket
   connection while it is running.
2. Install this plugin from its marketplace and start a new Codex conversation.
3. Ask Codex to call `describe_app_state`. If it cannot find the `workflow` tools, refresh the
   marketplace/plugin installation and start another new conversation.
4. Before changing a ticket, list projects and read the type schema. The tracking folder, rather
   than the repository root, is the required `workflow_root`.

## ChatGPT

ChatGPT cannot directly call the loopback address on this Mac. Connect either:

- a Workflow MCP server at a public HTTPS `/mcp` endpoint; or
- the local Workflow app through Secure MCP Tunnel.

In ChatGPT, open **Plugins**, choose **Add custom MCP server**, connect the endpoint or tunnel,
and create the plugin connection. Install this plugin from the local marketplace, start a new Work
chat, and select it with `@` before asking to list or create tickets.

For write actions, use the confirmation ChatGPT presents. Keep the server URL and any API key out
of ticket text and repository files.

## Verify

Ask the connected agent to list projects. A successful result shows the available tracking folders.
Then ask it to list types for the intended folder; that proves it can read the workspace before any
ticket mutation.
