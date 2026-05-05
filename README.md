https://github.com/mcasperson/ScratchpadReset

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