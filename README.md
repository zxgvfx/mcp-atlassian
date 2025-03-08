# MCP Atlassian

Model Context Protocol (MCP) server for Atlassian products (Confluence and Jira). This integration supports both Atlassian Cloud and Jira Server/Data Center deployments.

### Feature Demo
![Demo](https://github.com/user-attachments/assets/995d96a8-4cf3-4a03-abe1-a9f6aea27ac0)

### Compatibility

| Product | Deployment Type | Support Status |
|---------|----------------|----------------|
| **Confluence** | Cloud | ✅ Fully supported |
| **Confluence** | Server/Data Center | ❌ Not yet supported |
| **Jira** | Cloud | ✅ Fully supported |
| **Jira** | Server/Data Center | ✅ Supported (version 8.14+) |

## Installation

### Using uv (recommended)

On macOS:
```bash
brew install uv
```

When using [`uv`](https://docs.astral.sh/uv/), no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-atlassian*.

```bash
uvx mcp-atlassian
```

### Using PIP

Alternatively you can install mcp-atlassian via pip:

```bash
pip install mcp-atlassian
```

### Installing via Smithery

To install Atlassian Integration for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-atlassian):

```bash
npx -y @smithery/cli install mcp-atlassian --client claude
```

## Configuration

The MCP Atlassian integration supports using either Confluence, Jira, or both services. You only need to provide the environment variables for the service(s) you want to use.

### Authentication

#### For Atlassian Cloud (Confluence and Jira Cloud)

1. Get API tokens from: https://id.atlassian.com/manage-profile/security/api-tokens

#### For Jira Server/Data Center

1. Generate a Personal Access Token in your Jira Server/Data Center (version 8.14 or later):
   - Navigate to your profile by clicking on your avatar in the top right corner
   - Select **Profile** → **Personal Access Tokens**
     *(Alternative path in some versions: Account Settings → Security → Personal Access Tokens)*
   - Click **Create token**
   - Give your token a meaningful name (e.g., "MCP Integration")
   - Set an expiry date (or choose "Never" if permitted by your organization)
   - Copy the generated token immediately (you won't be able to see it again)

### Usage with Claude Desktop

> **Note:** For all configuration methods, include only the environment variables needed for your services:
> - For Confluence only (Cloud): Include `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, and `CONFLUENCE_API_TOKEN`
> - For Jira Cloud: Include `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN`
> - For Jira Server/Data Center: Include `JIRA_URL` and `JIRA_PERSONAL_TOKEN`
> - For multiple services: Include the variables for each service you want to use

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@domain.com",
        "CONFLUENCE_API_TOKEN": "your_api_token",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_USERNAME": "your.email@domain.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

For Jira Server/Data Center:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@domain.com",
        "CONFLUENCE_API_TOKEN": "your_api_token",
        "JIRA_URL": "https://jira.your-company.com",
        "JIRA_PERSONAL_TOKEN": "your_personal_access_token"
      }
    }
  }
}
```

</details>

<details>
<summary>Using pip</summary>

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "python",
      "args": ["-m", "mcp-atlassian"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@domain.com",
        "CONFLUENCE_API_TOKEN": "your_api_token",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_USERNAME": "your.email@domain.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

</details>

<details>
<summary>Using docker</summary>

There are two ways to configure the Docker environment:

1. Using environment variables directly in the config:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp/atlassian"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@domain.com",
        "CONFLUENCE_API_TOKEN": "your_api_token",
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_USERNAME": "your.email@domain.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

2. Using an environment file:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/path/to/your/.env",
        "mcp/atlassian"
      ]
    }
  }
}
```

The .env file should contain:
```env
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@domain.com
CONFLUENCE_API_TOKEN=your_api_token
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your.email@domain.com
JIRA_API_TOKEN=your_api_token
```

</details>

### Cursor IDE Configuration

To integrate the MCP server with Cursor IDE:

![image](https://github.com/user-attachments/assets/dee83445-c694-4b2e-8e47-7c280f806964)

Configure the server:
- Open Cursor Settings
- Navigate to `Features` > `MCP Servers`
- Click `Add new MCP server`
- Enter this configuration:
  ```yaml
  name: mcp-atlassian
  type: command
  command: uvx mcp-atlassian --confluence-url=https://your-domain.atlassian.net/wiki --confluence-username=your.email@domain.com --confluence-token=your_api_token --jira-url=https://your-domain.atlassian.net --jira-username=your.email@domain.com --jira-token=your_api_token
  ```

### Using a Local Development Version

If you've cloned the repository and want to run a local version of `mcp-atlassian`:

Configure in Claude Desktop:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/your/mcp-atlassian",
        "run", "mcp-atlassian",
        "--confluence-url=https://your-domain.atlassian.net/wiki",
        "--confluence-username=your.email@domain.com",
        "--confluence-token=your_api_token",
        "--jira-url=https://your-domain.atlassian.net",
        "--jira-username=your.email@domain.com",
        "--jira-token=your_api_token"
      ]
    }
  }
}
```

## Resources

> **Note:** The MCP server filters resources to only show Confluence spaces and Jira projects that the user is actively interacting with, based on their contributions and assignments.

- `confluence://{space_key}`: Access Confluence spaces
- `jira://{project_key}`: Access Jira projects

## Available Tools

| Tool | Description |
|------|-------------|
| `confluence_search` | Search Confluence content using CQL |
| `confluence_get_page` | Get content of a specific Confluence page |
| `confluence_get_comments` | Get comments for a specific Confluence page |
| `confluence_create_page` | Create a new Confluence page |
| `confluence_update_page` | Update an existing Confluence page |
| `jira_get_issue` | Get details of a specific Jira issue |
| `jira_search` | Search Jira issues using JQL |
| `jira_get_project_issues` | Get all issues for a specific Jira project |
| `jira_create_issue` | Create a new issue in Jira |
| `jira_update_issue` | Update an existing Jira issue |
| `jira_delete_issue` | Delete an existing Jira issue |
| `jira_get_transitions` | Get available status transitions for a Jira issue |
| `jira_transition_issue` | Transition a Jira issue to a new status |
| `jira_add_worklog` | Add a worklog entry to a Jira issue |
| `jira_get_worklog` | Get worklog entries for a Jira issue |
| `jira_link_to_epic` | Link an issue to an Epic |
| `jira_get_epic_issues` | Get all issues linked to a specific Epic |

## Debugging

You can use the MCP inspector to debug the server:

```bash
npx @modelcontextprotocol/inspector uvx mcp-atlassian
```

For development installations:
```bash
cd path/to/mcp-atlassian
npx @modelcontextprotocol/inspector uv run mcp-atlassian
```

View logs with:
```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```
## Build

Docker build:
```bash
docker build -t mcp/atlassian .
```

## Security

- Never share API tokens
- Keep .env files secure and private
- See [SECURITY.md](SECURITY.md) for best practices

## License

Licensed under MIT - see [LICENSE](LICENSE) file. This is not an official Atlassian product.
