# Klaviyo MCP Server (Beta)

The Klaviyo [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server integrates with [Klaviyo's APIs](https://developers.klaviyo.com/en/reference/api_overview),
allowing you to interact with your Klaviyo data using a variety of MCP clients.

## Setup

### 1. Create a [Klaviyo private API key](https://help.klaviyo.com/hc/en-us/articles/7423954176283#h_01HDKDXQA1ZGSRCGM041B507KG)

To use all the available tools, you must either create a Full Access Key or a Custom Key with at least the following permissions:

| Scope         | Access |
| ------------- | ------ |
| Accounts      | Read   |
| Campaigns     | Full   |
| Catalogs      | Read   |
| Events        | Full   |
| Flows         | Full   |
| Images        | Full   |
| List          | Read   |
| Metrics       | Read   |
| Profiles      | Full   |
| Segments      | Full   |
| Subscriptions | Full   |
| Tags          | Read   |
| Templates     | Full   |

### 2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

For macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows:

```bat
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Add the server to your client

#### Claude Desktop

1. Download [Claude Desktop](https://claude.ai/download)
1. Open Claude Desktop. Within **Settings** -> **Developer** -> **Edit Config**, add the following, substituting your API key:

```json
{
  "mcpServers": {
    "klaviyo": {
      "command": "uvx",
      "args": ["klaviyo-mcp-server@latest"],
      "env": {
        "PRIVATE_API_KEY": "YOUR_API_KEY",
        "READ_ONLY": "false"
      }
    }
  }
}
```

> **_Note for free users:_** The free version of Claude Desktop has a very limited context window,
> and you may run into issues with all the tools enabled. Here are a few possible workarounds:
>
> 1. Only enable the tools you need
> 1. Use [read-only mode](#read-only-mode)
> 1. Use a different client

> **_Note on security:_** We do not recommend storing your API key in this file. See [below](#securing-your-api-key-with-claude-desktop-and-cursor) for an alternative.

#### Cursor

1. Download [Cursor](https://www.cursor.com/)
1. Open Cursor. Within **Settings** -> **Cursor Settings** -> **MCP Tools** -> **New MCP Server**, add the following, substituting your API key:

```json
{
  "mcpServers": {
    "klaviyo": {
      "command": "uvx",
      "args": ["klaviyo-mcp-server@latest"],
      "env": {
        "PRIVATE_API_KEY": "YOUR_API_KEY",
        "READ_ONLY": "false"
      }
    }
  }
}
```

> **_Note on security:_** We do not recommend storing your API key in this file. See [below](#securing-your-api-key-with-claude-desktop-and-cursor) for an alternative.

#### VS Code

1. Download [VS Code](https://code.visualstudio.com/)
1. Open VS Code. Within settings (`Ctrl + Shift + P` -> `Preferences: Open Settings (JSON)`), add the following:

```json
{
  "mcp": {
    "servers": {
      "klaviyo": {
        "command": "uvx",
        "args": ["klaviyo-mcp-server@latest"],
        "env": {
          "PRIVATE_API_KEY": "${input:klaviyo_api_key}",
          "READ_ONLY": "false"
        }
      }
    },
    "inputs": [
      {
        "type": "promptString",
        "id": "klaviyo_api_key",
        "description": "Klaviyo API Key",
        "password": true
      }
    ]
  }
}
```

## Configuration

### Read-only mode

To enable only the tools that do not modify any Klaviyo data, set the `READ_ONLY` environment variable to `"true"` in the above configurations.

### Securing your API key with Claude Desktop and Cursor

As of now, Claude Desktop and Cursor require that your API key exist in plaintext in your config file, which is not very secure.

Instead, we recommend saving your API key to an environment variable, and then using the below script to write from the environment variable to your config only while the client is running.

Note that as of now, this only supports macOS.

To run Claude Desktop:

```bash
uvx --from klaviyo-mcp-server run-claude NAME_OF_API_KEY_ENVIRONMENT_VARIABLE
```

To run Cursor:

```bash
uvx --from klaviyo-mcp-server run-cursor NAME_OF_API_KEY_ENVIRONMENT_VARIABLE
```

## Available Tools

| Category  | Tool name                             | Description                                                        |
| --------- | ------------------------------------- | ------------------------------------------------------------------ |
| Accounts  | `get_account_details`                 | Get details of your account.                                       |
| Campaigns | `get_campaigns`                       | List your campaigns.                                               |
| Campaigns | `get_campaign`                        | Get details of a campaign.                                         |
| Campaigns | `create_campaign`                     | Create a campaign.                                                 |
| Campaigns | `assign_template_to_campaign_message` | Assign an email template to a campaign message.                    |
| Catalogs  | `get_catalog_items`                   | List your catalog items.                                           |
| Events    | `get_events`                          | List events.                                                       |
| Events    | `create_event`                        | Create an event for a profile.                                     |
| Events    | `get_metrics`                         | List event metrics.                                                |
| Events    | `get_metric`                          | Get details of an event metric.                                    |
| Flows     | `get_flows`                           | List your flows.                                                   |
| Flows     | `get_flow`                            | Get details of a flow.                                             |
| Groups    | `get_lists`                           | List your lists.                                                   |
| Groups    | `get_list`                            | Get details of a list.                                             |
| Groups    | `get_segments`                        | List your segments.                                                |
| Groups    | `get_segment`                         | Get details of a segment.                                          |
| Images    | `upload_image_from_file`              | Upload image from a local file.                                    |
| Images    | `upload_image_from_url`               | Upload image from a URL.                                           |
| Profiles  | `get_profiles`                        | List your profiles.                                                |
| Profiles  | `get_profile`                         | Get details of a profile.                                          |
| Profiles  | `create_profile`                      | Create a profile.                                                  |
| Profiles  | `update_profile`                      | Update a profile.                                                  |
| Profiles  | `subscribe_profile_to_marketing`      | Subscribe a profile to marketing for a given channel and list.     |
| Profiles  | `unsubscribe_profile_from_marketing`  | Unsubscribe a profile from marketing for a given channel and list. |
| Reporting | `get_campaign_report`                 | Get a report of your campagin performance.                         |
| Reporting | `get_flow_report`                     | Get a report of your flow performance.                             |
| Templates | `create_email_template`               | Create an HTML email template.                                     |
| Templates | `get_email_template`                  | Get the details of an email template.                              |

## Feedback

We'd love to hear your feedback! Please fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSday2sqDvxfoRxjLrhROYZtxivRfHF151tcXV7o-ZYGF2SipQ/viewform?usp=header) with any issues, questions, or comments.
