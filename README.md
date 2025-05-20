# MCP Atlassian

![PyPI Version](https://img.shields.io/pypi/v/mcp-atlassian)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-atlassian)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-atlassian?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Run Tests](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml/badge.svg)](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-atlassian)

Model Context Protocol (MCP) server for Atlassian products (Confluence and Jira). This integration supports both Confluence & Jira Cloud and Server/Data Center deployments.

## Example Usage

Ask your AI assistant to:

- **📝 Automatic Jira Updates** - "Update Jira from our meeting notes"
- **🔍 AI-Powered Confluence Search** - "Find our OKR guide in Confluence and summarize it"
- **🐛 Smart Jira Issue Filtering** - "Show me urgent bugs in PROJ project from last week"
- **📄 Content Creation & Management** - "Create a tech design doc for XYZ feature"

### Feature Demo

https://github.com/user-attachments/assets/35303504-14c6-4ae4-913b-7c25ea511c3e

<details> <summary>Confluence Demo</summary>

https://github.com/user-attachments/assets/7fe9c488-ad0c-4876-9b54-120b666bb785

</details>

### Compatibility

| Product        | Deployment Type    | Support Status              |
|----------------|--------------------|-----------------------------|
| **Confluence** | Cloud              | ✅ Fully supported           |
| **Confluence** | Server/Data Center | ✅ Supported (version 6.0+)  |
| **Jira**       | Cloud              | ✅ Fully supported           |
| **Jira**       | Server/Data Center | ✅ Supported (version 8.14+) |

## Quick Start Guide

### 🔐 1. Authentication Setup

MCP Atlassian supports three authentication methods:

#### A. API Token Authentication (Cloud)

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**, name it
3. Copy the token immediately

#### B. Personal Access Token (Server/Data Center)

1. Go to your profile (avatar) → **Profile** → **Personal Access Tokens**
2. Click **Create token**, name it, set expiry
3. Copy the token immediately

#### C. OAuth 2.0 Authentication (Cloud)

1. Go to [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)
2. Create an "OAuth 2.0 (3LO) integration" app
3. Configure **Permissions** (scopes) for Jira/Confluence
4. Set **Callback URL** (e.g., `http://localhost:8080/callback`)
5. Run setup wizard:
   ```bash
   docker run --rm -i \
     -p 8080:8080 \
     -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
     ghcr.io/sooperset/mcp-atlassian:latest --oauth-setup -v
   ```
6. Follow prompts for `Client ID`, `Secret`, `URI`, and `Scope`
7. Complete browser authorization
8. Add obtained credentials to `.env` or IDE config:
   - `ATLASSIAN_OAUTH_CLOUD_ID` (from wizard)
   - `ATLASSIAN_OAUTH_CLIENT_ID`
   - `ATLASSIAN_OAUTH_CLIENT_SECRET`
   - `ATLASSIAN_OAUTH_REDIRECT_URI`
   - `ATLASSIAN_OAUTH_SCOPE`

> [!IMPORTANT]
> Include `offline_access` in scope for persistent auth (e.g., `read:jira-work write:jira-work offline_access`)

### 📦 2. Installation

MCP Atlassian is distributed as a Docker image. This is the recommended way to run the server, especially for IDE integration. Ensure you have Docker installed.

```bash
# Pull Pre-built Image
docker pull ghcr.io/sooperset/mcp-atlassian:latest
```

## 🛠️ IDE Integration

MCP Atlassian is designed to be used with AI assistants through IDE integration.

> [!TIP]
> **For Claude Desktop**: Locate and edit the configuration file directly:
> - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
> - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - **Linux**: `~/.config/Claude/claude_desktop_config.json`
>
> **For Cursor**: Open Settings → MCP → + Add new global MCP server

### ⚙️ Configuration Methods

There are two main approaches to configure the Docker container:

1. **Passing Variables Directly** (shown in examples below)
2. **Using an Environment File** with `--env-file` flag (shown in collapsible sections)

> [!NOTE]
> Common environment variables include:
>
> - `CONFLUENCE_SPACES_FILTER`: Filter by space keys (e.g., "DEV,TEAM,DOC")
> - `JIRA_PROJECTS_FILTER`: Filter by project keys (e.g., "PROJ,DEV,SUPPORT")
> - `READ_ONLY_MODE`: Set to "true" to disable write operations
> - `MCP_VERBOSE`: Set to "true" for more detailed logging
> - `ENABLED_TOOLS`: Comma-separated list of tool names to enable (e.g., "confluence_search,jira_get_issue")
>
> See the [.env.example](https://github.com/sooperset/mcp-atlassian/blob/main/.env.example) file for all available options.


### 📝 Configuration Examples

**Method 1 (Passing Variables Directly):**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token"
      }
    }
  }
}
```

<details>
<summary>Alternative: Using Environment File</summary>

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
        "/path/to/your/mcp-atlassian.env",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ]
    }
  }
}
```
</details>

<details>
<summary>Server/Data Center Configuration</summary>

For Server/Data Center deployments, use direct variable passing:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "-e", "CONFLUENCE_SSL_VERIFY",
        "-e", "JIRA_URL",
        "-e", "JIRA_PERSONAL_TOKEN",
        "-e", "JIRA_SSL_VERIFY",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://confluence.your-company.com",
        "CONFLUENCE_PERSONAL_TOKEN": "your_confluence_pat",
        "CONFLUENCE_SSL_VERIFY": "false",
        "JIRA_URL": "https://jira.your-company.com",
        "JIRA_PERSONAL_TOKEN": "your_jira_pat",
        "JIRA_SSL_VERIFY": "false"
      }
    }
  }
}
```

> [!NOTE]
> Set `CONFLUENCE_SSL_VERIFY` and `JIRA_SSL_VERIFY` to "false" only if you have self-signed certificates.

</details>

<details>
<summary>OAuth 2.0 Configuration (Cloud Only)</summary>
<a name="oauth-20-configuration-example-cloud-only"></a>

This example shows how to configure `mcp-atlassian` in your IDE (like Cursor or Claude Desktop) when using OAuth 2.0 for Atlassian Cloud. Ensure you have completed the [OAuth setup wizard](#c-oauth-20-authentication-cloud-only) first.

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v", "<path_to_your_home>/.mcp-atlassian:/home/app/.mcp-atlassian",
        "-e", "JIRA_URL",
        "-e", "CONFLUENCE_URL",
        "-e", "ATLASSIAN_OAUTH_CLIENT_ID",
        "-e", "ATLASSIAN_OAUTH_CLIENT_SECRET",
        "-e", "ATLASSIAN_OAUTH_REDIRECT_URI",
        "-e", "ATLASSIAN_OAUTH_SCOPE",
        "-e", "ATLASSIAN_OAUTH_CLOUD_ID",
        "ghcr.io/sooperset/mcp-atlassian:latest",
      ],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "ATLASSIAN_OAUTH_CLIENT_ID": "YOUR_OAUTH_APP_CLIENT_ID",
        "ATLASSIAN_OAUTH_CLIENT_SECRET": "YOUR_OAUTH_APP_CLIENT_SECRET",
        "ATLASSIAN_OAUTH_REDIRECT_URI": "http://localhost:8080/callback",
        "ATLASSIAN_OAUTH_SCOPE": "read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access",
        "ATLASSIAN_OAUTH_CLOUD_ID": "YOUR_CLOUD_ID_FROM_SETUP_WIZARD"
      }
    }
  }
}
```

> [!NOTE]
> - `ATLASSIAN_OAUTH_CLOUD_ID` is obtained from the `--oauth-setup` wizard output.
> - Other `ATLASSIAN_OAUTH_*` variables are those you configured for your OAuth app in the Atlassian Developer Console (and used as input to the setup wizard).
> - `JIRA_URL` and `CONFLUENCE_URL` for your Cloud instances are still required.

</details>

<details>
<summary>Proxy Configuration</summary>

MCP Atlassian supports routing API requests through standard HTTP/HTTPS/SOCKS proxies. Configure using environment variables:

- Supports standard `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `SOCKS_PROXY`.
- Service-specific overrides are available (e.g., `JIRA_HTTPS_PROXY`, `CONFLUENCE_NO_PROXY`).
- Service-specific variables override global ones for that service.

Add the relevant proxy variables to the `args` (using `-e`) and `env` sections of your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "... existing Confluence/Jira vars",
        "-e", "HTTP_PROXY",
        "-e", "HTTPS_PROXY",
        "-e", "NO_PROXY",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "... existing Confluence/Jira vars": "...",
        "HTTP_PROXY": "http://proxy.internal:8080",
        "HTTPS_PROXY": "http://proxy.internal:8080",
        "NO_PROXY": "localhost,.your-company.com"
      }
    }
  }
}
```

Credentials in proxy URLs are masked in logs. If you set `NO_PROXY`, it will be respected for requests to matching hosts.

</details>

<details> <summary>Single Service Configurations</summary>

**For Confluence Cloud only:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

For Confluence Server/DC, use:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://confluence.your-company.com",
        "CONFLUENCE_PERSONAL_TOKEN": "your_personal_token"
      }
    }
  }
}
```

**For Jira Cloud only:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

For Jira Server/DC, use:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://jira.your-company.com",
        "JIRA_PERSONAL_TOKEN": "your_personal_token"
      }
    }
  }
}
```

</details>

### 👥 HTTP Transport Configuration

Instead of using `stdio`, you can run the server as a persistent HTTP service using either:
- `sse` (Server-Sent Events) transport at `/sse` endpoint
- `streamable-http` transport at `/mcp` endpoint

Both transport types support single-user and multi-user authentication:

**Authentication Options:**
- **Single-User**: Use server-level authentication configured via environment variables
- **Multi-User**: Each user provides their own authentication:
  - Cloud: OAuth 2.0 Bearer tokens
  - Server/Data Center: Personal Access Tokens (PATs)

<details> <summary>Basic HTTP Transport Setup</summary>

1. Start the server with your chosen transport:

    ```bash
    # For SSE transport
    docker run --rm -p 9000:9000 \
      --env-file /path/to/your/.env \
      ghcr.io/sooperset/mcp-atlassian:latest \
      --transport sse --port 9000 -vv

    # OR for streamable-http transport
    docker run --rm -p 9000:9000 \
      --env-file /path/to/your/.env \
      ghcr.io/sooperset/mcp-atlassian:latest \
      --transport streamable-http --port 9000 -vv
    ```

2. Configure your IDE (single-user example):

    **SSE Transport Example:**
    ```json
    {
      "mcpServers": {
        "mcp-atlassian-http": {
          "url": "http://localhost:9000/sse"
        }
      }
    }
    ```

    **Streamable-HTTP Transport Example:**
    ```json
    {
      "mcpServers": {
        "mcp-atlassian-service": {
          "url": "http://localhost:9000/mcp"
        }
      }
    }
    ```
</details>

<details> <summary>Multi-User Authentication Setup</summary>

Here's a complete example of setting up multi-user authentication with streamable-HTTP transport:

1. First, run the OAuth setup wizard to configure the server's OAuth credentials:
   ```bash
   docker run --rm -i \
     -p 8080:8080 \
     -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
     ghcr.io/sooperset/mcp-atlassian:latest --oauth-setup -v
   ```

2. Start the server with streamable-HTTP transport:
   ```bash
   docker run --rm -p 9000:9000 \
     --env-file /path/to/your/.env \
     ghcr.io/sooperset/mcp-atlassian:latest \
     --transport streamable-http --port 9000 -vv
   ```

3. Configure your IDE's MCP settings:

**Choose the appropriate Authorization method for your Atlassian deployment:**

- **Cloud (OAuth 2.0):** Use this if your organization is on Atlassian Cloud and you have an OAuth access token for each user.
- **Server/Data Center (PAT):** Use this if you are on Atlassian Server or Data Center and each user has a Personal Access Token (PAT).

**Cloud (OAuth 2.0) Example:**
```json
{
  "mcpServers": {
    "mcp-atlassian-service": {
      "url": "http://localhost:9000/mcp",
      "headers": {
        "Authorization": "Bearer <USER_OAUTH_ACCESS_TOKEN>"
      }
    }
  }
}
```

**Server/Data Center (PAT) Example:**
```json
{
  "mcpServers": {
    "mcp-atlassian-service": {
      "url": "http://localhost:9000/mcp",
      "headers": {
        "Authorization": "Token <USER_PERSONAL_ACCESS_TOKEN>"
      }
    }
  }
}
```

4. Required environment variables in `.env`:
   ```bash
   JIRA_URL=https://your-company.atlassian.net
   CONFLUENCE_URL=https://your-company.atlassian.net/wiki
   ATLASSIAN_OAUTH_CLIENT_ID=your_oauth_app_client_id
   ATLASSIAN_OAUTH_CLIENT_SECRET=your_oauth_app_client_secret
   ATLASSIAN_OAUTH_REDIRECT_URI=http://localhost:8080/callback
   ATLASSIAN_OAUTH_SCOPE=read:jira-work write:jira-work read:confluence-content.all write:confluence-content offline_access
   ATLASSIAN_OAUTH_CLOUD_ID=your_cloud_id_from_setup_wizard
   ```

> [!NOTE]
> - The server should have its own fallback authentication configured (e.g., via environment variables for API token, PAT, or its own OAuth setup using --oauth-setup). This is used if a request doesn't include user-specific authentication.
> - **OAuth**: Each user needs their own OAuth access token from your Atlassian OAuth app.
> - **PAT**: Each user provides their own Personal Access Token.
> - The server will use the user's token for API calls when provided, falling back to server auth if not
> - User tokens should have appropriate scopes for their needed operations

</details>

## Tools

### Key Tools

#### Jira Tools

- `jira_get_issue`: Get details of a specific issue
- `jira_search`: Search issues using JQL
- `jira_create_issue`: Create a new issue
- `jira_update_issue`: Update an existing issue
- `jira_transition_issue`: Transition an issue to a new status
- `jira_add_comment`: Add a comment to an issue

#### Confluence Tools

- `confluence_search`: Search Confluence content using CQL
- `confluence_get_page`: Get content of a specific page
- `confluence_create_page`: Create a new page
- `confluence_update_page`: Update an existing page

<details> <summary>View All Tools</summary>

| Operation | Jira Tools                    | Confluence Tools               |
|-----------|-------------------------------|--------------------------------|
| **Read**  | `jira_search`                 | `confluence_search`            |
|           | `jira_get_issue`              | `confluence_get_page`          |
|           | `jira_get_project_issues`     | `confluence_get_page_children` |
|           | `jira_get_worklog`            | `confluence_get_comments`      |
|           | `jira_get_transitions`        | `confluence_get_labels`        |
|           | `jira_get_agile_boards`       |                                |
|           | `jira_get_board_issues`       |                                |
|           | `jira_get_sprints_from_board` |                                |
|           | `jira_get_sprint_issues`      |                                |
|           | `jira_get_issue_link_types`   |                                |
|           | `jira_batch_get_changelogs`*  |                                |
|           | `jira_get_user_profile`       |                                |
|           | `jira_download_attachments`   |                                |
| **Write** | `jira_create_issue`           | `confluence_create_page`       |
|           | `jira_update_issue`           | `confluence_update_page`       |
|           | `jira_delete_issue`           | `confluence_delete_page`       |
|           | `jira_batch_create_issues`    | `confluence_add_label`         |
|           | `jira_add_comment`            | `confluence_add_comment`       |
|           | `jira_transition_issue`       |                                |
|           | `jira_add_worklog`            |                                |
|           | `jira_link_to_epic`           |                                |
|           | `jira_create_sprint`          |                                |
|           | `jira_update_sprint`          |                                |
|           | `jira_create_issue_link`      |                                |
|           | `jira_remove_issue_link`      |                                |

*Tool only available on Jira Cloud

</details>

### Tool Filtering and Access Control

The server provides two ways to control tool access:

1. **Tool Filtering**: Use `--enabled-tools` flag or `ENABLED_TOOLS` environment variable to specify which tools should be available:

   ```bash
   # Via environment variable
   ENABLED_TOOLS="confluence_search,jira_get_issue,jira_search"

   # Or via command line flag
   docker run ... --enabled-tools "confluence_search,jira_get_issue,jira_search" ...
   ```

2. **Read/Write Control**: Tools are categorized as read or write operations. When `READ_ONLY_MODE` is enabled, only read operations are available regardless of `ENABLED_TOOLS` setting.

## Troubleshooting & Debugging

### Common Issues

- **Authentication Failures**:
    - For Cloud: Check your API tokens (not your account password)
    - For Server/Data Center: Verify your personal access token is valid and not expired
    - For older Confluence servers: Some older versions require basic authentication with `CONFLUENCE_USERNAME` and `CONFLUENCE_API_TOKEN` (where token is your password)
- **SSL Certificate Issues**: If using Server/Data Center and encounter SSL errors, set `CONFLUENCE_SSL_VERIFY=false` or `JIRA_SSL_VERIFY=false`
- **Permission Errors**: Ensure your Atlassian account has sufficient permissions to access the spaces/projects

### Debugging Tools

```bash
# Using MCP Inspector for testing
npx @modelcontextprotocol/inspector uvx mcp-atlassian ...

# For local development version
npx @modelcontextprotocol/inspector uv --directory /path/to/your/mcp-atlassian run mcp-atlassian ...

# View logs
# macOS
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
# Windows
type %APPDATA%\Claude\logs\mcp*.log | more
```

## Security

- Never share API tokens
- Keep .env files secure and private
- See [SECURITY.md](SECURITY.md) for best practices

## Contributing

We welcome contributions to MCP Atlassian! If you'd like to contribute:

1. Check out our [CONTRIBUTING.md](CONTRIBUTING.md) guide for detailed development setup instructions.
2. Make changes and submit a pull request.

We use pre-commit hooks for code quality and follow semantic versioning for releases.

## License

Licensed under MIT - see [LICENSE](LICENSE) file. This is not an official Atlassian product.
