# Cloud PC Management MCP Server

MCP Server for managing Azure Cloud PCs using the Microsoft Graph API.

### Features
The MCP server currently uses 'curl' to send Graph API requests, because Python msgraph-sdk documentation doesn't match the current sdk implementation.

## Tools
* `cloud_pc_list_users`
   - List all registered users
   - Returns: List of information about users in JSON formated string
* `cloud_pc_list`
   - List all Cloud PCs available to the current tenant
   - Returns: List of Cloud PCs in JSON formated string
* `cloud_pc_reboot`
   - Reboot Cloud PCs with the given ID
   - Args: Cloud PC ID
* `cloud_pc_rename`
   - Set new display name for a Cloud PC with the given ID.
   - Arg: Cloud PC ID
   - Arg: New display name for the Cloud PC
* `cloud_pc_troubleshoot`
   - Troubleshoot a Cloud PC with the given ID.
   - Arg: Cloud PC ID
* `cloud_pc_end_grace_period`
   - End grace period for a Cloud PC with the given ID.
   - Arg: Cloud PC ID
* `cloud_pc_get_review_status`
   - Retrieve review status for the Cloud PC with particular ID.
   - Arg: Cloud PC ID
* `cloud_pc_reprovision`
   - Reprovision the Cloud PC with particular ID with Windows 10 or 11 OS, set up redeployed user type 
   - Arg: Cloud PC ID
   - Arg: Windows user account type (avalilable types: standardUser, administrator)
   - Arg: Windows operating system version (avalilable versions: windows10, windows11)


### Usage with Claude Desktop
To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-cloud-pc": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/mcp-cloud-pc",
        "mcp-cloud-pc.py"
      ],
      "env": {
        "MSGRAPH_TENANT_ID": "<YOUR GRAPH API TENANT ID>",
        "MSGRAPH_CLIENT_ID": "<YOUR GRAPH API CLIENT ID>",
        "MSGRAPH_CLIENT_SECRET": "<YOUR GRAPH API CLIENT SECRET>"
      }
    }
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
