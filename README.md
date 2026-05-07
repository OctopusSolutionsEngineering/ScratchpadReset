https://github.com/OctopusSolutionsEngineering/ScratchpadReset

This MCP server deletes and recreates a space in Octopus Deploy. This is used to test the creation of Octopus resources 
in a fresh environment as part of agentic workflows.

```json
{
  "servers": {
    "scratchpadreset": {
      "command": "podman",
      "args": [
        "run",
        "--pull=always",
        "--rm",
        "--interactive",
        "--network=host",
        "--env",
        "OCTOPUS_CLI_API_KEY=API-ABCDEFGHIJKLMNOPQURSTUVWXYZ",
        "ghcr.io/mcasperson/scratchpadreset"
      ],
      "type": "stdio"
    }
  }
}
```