"""Contract checks for the plugin package consumed by Codex and ChatGPT."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OpenAIPackageTests(unittest.TestCase):
    def test_portable_manifest_declares_openai_onboarding(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())

        openai = manifest["extensions"]["com.openai"]
        self.assertEqual(openai["onboardingSkill"], "./skills/setup/SKILL.md")
        self.assertEqual(openai["interface"]["displayName"], "plaiiin Workflow")

    def test_onboarding_explains_codex_and_chatgpt_connections(self):
        onboarding = (ROOT / "skills/setup/SKILL.md").read_text()

        self.assertIn("Codex", onboarding)
        self.assertIn("ChatGPT", onboarding)
        self.assertIn("Secure MCP Tunnel", onboarding)

    def test_readme_explains_chatgpt_plugin_installation(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("ChatGPT Desktop", readme)
        self.assertIn("Plugins Directory", readme)

    def test_all_customer_manifests_use_the_unix_socket(self):
        expected = {
            "type": "stdio",
            "command": "/usr/bin/nc",
            "args": [
                "-U",
                "${HOME}/Library/Group Containers/LA8GX8Y3R9.group.plaiiin/run/workflow-mcp.sock",
            ],
        }
        portable = json.loads((ROOT / "mcp.json").read_text())
        codex = json.loads((ROOT / ".mcp.json").read_text())
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())

        self.assertEqual(portable["mcpServers"]["workflow"], expected)
        self.assertEqual(codex["mcpServers"]["workflow"], expected)
        self.assertEqual(claude["mcpServers"]["workflow"], expected)

    def test_local_marketplace_points_at_the_plugin_root(self):
        marketplace = json.loads(
            (ROOT / ".agents/plugins/marketplace.json").read_text()
        )

        self.assertEqual(
            marketplace["plugins"][0]["source"]["path"], "./"
        )

    def test_codex_compatibility_manifest_matches_package_version(self):
        portable = json.loads((ROOT / "plugin.json").read_text())
        compatibility = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text()
        )

        self.assertEqual(portable["version"], "2.0.5")
        self.assertEqual(compatibility["version"], portable["version"])


if __name__ == "__main__":
    unittest.main()
