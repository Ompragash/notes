# Chapter 6: Scope Handling

In [Chapter 5: Harness API Client](05_harness_api_client_.md), we learned how our `harness-mcp` server uses a dedicated "courier" – the API Client – to talk to the Harness platform. This courier is great at delivering messages, but Harness is a big place! How does the courier know exactly *where* in Harness to deliver the message or pick up information? For example, if we ask for a list of pipelines, Harness needs to know: "Pipelines for *which* account? In *which* organization? And for *which* project?"

This is where **Scope Handling** comes in. It's like making sure every piece of mail has the correct and complete address (Account, Organization, Project) so Harness knows exactly which part of its system to interact with.

## The "Where" Question: Why Scope Matters

Many actions you perform in Harness are specific to a certain context. You don't just create "a pipeline"; you create a pipeline *within* a specific Project, which lives *within* an Organization, which is part of your Harness Account.

*   **Account ID**: Identifies your overall Harness account. This is almost always needed.
*   **Organization ID (Org ID)**: Within an account, you can have multiple organizations to group your projects.
*   **Project ID**: Within an organization, projects hold your pipelines, services, environments, etc.

When the `harness-mcp` server makes an API call to Harness (using the [Harness API Client](05_harness_api_client_.md)), it usually needs to provide these IDs to tell Harness the exact "scope" or "location" for the operation.

**Use Case Example**: Imagine you want to use a tool to list pipelines. The `harness-mcp` server needs to ask Harness:
*   "Please list pipelines for Account `A`." (If your API key is only for Account `A`)
*   Often, it's more specific: "Please list pipelines for Account `A`, within Organization `OrgX`, and inside Project `ProjectY`."

Scope Handling is the mechanism `harness-mcp` uses to manage and apply this crucial addressing information.

## Setting the Address: Global vs. Per-Tool

`harness-mcp` offers two ways to provide this scope information:

1.  **Global Configuration**:
    When you start the `harness-mcp-server`, you can provide your main Account ID, and optionally a default Organization ID and Project ID. You learned about this in [Chapter 4: Server Configuration](04_server_configuration_.md).
    *   Example: `./harness-mcp-server stdio --account-id "my_account" --org-id "my_org" --project-id "my_project"`
    These become the default "address" for all tools.

2.  **Per-Tool Invocation**:
    Even if you have global defaults, a client (like an AI assistant) might want to operate on a *different* Organization or Project for a specific tool call, without changing the server's global settings. Many tools in `harness-mcp` allow the client to specify `org_id` and `project_id` as parameters when calling the tool.
    *   Example: A client requests to use the `list_pipelines` tool and provides: `org_id: "another_org"`, `project_id: "special_project"`. These would then override the global defaults *for that specific request only*.

The `AccountID` is typically set globally when the server starts and isn't usually overridden per tool call because API keys are often tied to a specific account. However, `OrgID` and `ProjectID` are more flexible.

## How Tools Handle Scope

Let's see how a tool would be defined to accept scope parameters and how it would use them.

**1. Defining Scope Parameters for a Tool**

When a new tool is created (as seen in [Chapter 1: Tools & Toolsets](01_tools___toolsets_.md)), it can declare that it accepts `org_id` and `project_id` as optional parameters. The `harness-mcp` project provides a helper function for this.

Imagine we're defining a `list_secrets` tool. The `config` object here is the global server configuration we discussed in [Chapter 4: Server Configuration](04_server_configuration_.md).

```go
// Simplified from how a tool might be defined (e.g., in pkg/harness/secrets.go)
import (
	"github.com/harness/harness-mcp/pkg/harness" // Our harness-specific helpers
	"github.com/harness/harness-mcp/cmd/harness-mcp-server/config" // Server config
	"github.com/mark3labs/mcp-go/mcp" // MCP library
)

func ListSecretsTool(cfg *config.Config, apiClient *client.Client) (mcp.Tool, server.ToolHandlerFunc) {
	return mcp.NewTool("list_secrets",
			mcp.WithDescription("Lists secrets in a project."),
			// Use the WithScope helper!
			harness.WithScope(cfg, true), // 'true' means org/project are required for this tool
			// ... other parameters for list_secrets if any ...
		),
		// ... The tool handler function goes here ...
		func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
			// ... handler logic will use fetchScope (see below) ...
			return nil, nil // Placeholder
		}
}
```
*   `harness.WithScope(cfg, true)`: This is the key part. It's a helper function from `pkg/harness/scope.go`.
    *   It automatically adds `org_id` and `project_id` string parameters to the `list_secrets` tool.
    *   It uses the `cfg.OrgID` and `cfg.ProjectID` from the global server configuration as the *default values* for these parameters.
    *   The `true` argument means that for *this specific tool*, an Org ID and Project ID are considered *required*. If they aren't available either from global config or tool input, an error might occur. If it were `false`, they'd be optional.

**2. Fetching Scope Inside a Tool Handler**

When the tool is called, its handler function needs to figure out the final Account, Org, and Project IDs to use. It will use another helper function, `fetchScope`.

```go
// Simplified handler logic for 'list_secrets'
import (
	"github.com/harness/harness-mcp/client/dto" // For dto.Scope
	// ... other imports from previous snippet ...
)

// ... inside the ListSecretsTool's handler function ...
func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	// Fetch the effective scope for this tool call
	currentScope, err := harness.fetchScope(cfg, request, true) // 'cfg' is the global server config
	if err != nil {
		return mcp.NewErrorResult("scope_error", err.Error()), nil
	}

	// Now 'currentScope' contains AccountID, OrgID, and ProjectID
	// Log the scope being used
	slog.Info("Operating with scope", 
		"account", currentScope.AccountID, 
		"org", currentScope.OrgID, 
		"project", currentScope.ProjectID)

	// Use currentScope when calling the Harness API Client
	// For example: secrets, err := apiClient.Secrets.List(ctx, currentScope, /* other params */)
	// ...
	
	return mcp.NewToolResultText("Secrets listed (details omitted for brevity)"), nil
}
```
*   `harness.fetchScope(cfg, request, true)`: This function (from `pkg/harness/scope.go`) does the magic:
    1.  It takes the global `cfg` (which has the default Account, Org, Project IDs).
    2.  It looks at the incoming `request` from the client.
    3.  It checks if the client provided `org_id` or `project_id` parameters in the `request`.
    4.  **Priority**:
        *   The Account ID always comes from `cfg.AccountID`.
        *   If `org_id` was in the `request`, that value is used. Otherwise, `cfg.OrgID` is used.
        *   If `project_id` was in the `request`, that value is used. Otherwise, `cfg.ProjectID` is used.
    5.  The `true` argument means it will return an error if, after this logic, `OrgID` or `ProjectID` are still empty (because the tool declared them as required).
*   `currentScope`: This variable (of type `dto.Scope`) now holds the resolved Account, Org, and Project IDs. This `currentScope` is then passed to the [Harness API Client](05_harness_api_client_.md) methods.

The `dto.Scope` struct is very simple:
```go
// From: client/dto/scope.go
package dto

type Scope struct {
	AccountID string `json:"accountIdentifier"`
	OrgID     string `json:"orgIdentifier"`
	ProjectID string `json:"projectIdentifier"`
}
```
This struct is then used by the API client methods to set the necessary query parameters (`accountIdentifier`, `orgIdentifier`, `projectIdentifier`) for the HTTP requests to Harness.

## Under the Hood: Resolving the Scope

Let's trace how the scope is determined when a tool using `fetchScope` is called.

**Scenario**:
*   Server started with global config: `AccountID="acc_global"`, `OrgID="org_global"`, `ProjectID="proj_global"`.
*   Client calls `list_secrets` tool with parameter: `project_id: "proj_tool_override"`. (No `org_id` provided in the tool call).

**Steps inside `fetchScope(cfg, request, true)`**:

1.  **Account ID**: Always taken from global config. `result.AccountID = "acc_global"`.
2.  **Organization ID**:
    *   Was `org_id` in `request`? No.
    *   Use global config's OrgID. `result.OrgID = "org_global"`.
3.  **Project ID**:
    *   Was `project_id` in `request`? Yes, it's `"proj_tool_override"`.
    *   Use this value from the request. `result.ProjectID = "proj_tool_override"`.
4.  **Required Check**: The tool marked scope as required (`true`).
    *   Is `result.OrgID` empty? No (`"org_global"`).
    *   Is `result.ProjectID` empty? No (`"proj_tool_override"`).
    *   All good.
5.  **Return**: `fetchScope` returns a `dto.Scope` object: `{AccountID:"acc_global", OrgID:"org_global", ProjectID:"proj_tool_override"}`.

This resolved scope is then passed to the [Harness API Client](05_harness_api_client_.md).

Here's a diagram illustrating this decision process:

```mermaid
graph TD
    A[Start fetchScope(config, request)] --> B{Global AccountID exists?};
    B -- Yes --> C[Use Global AccountID];
    B -- No (Error case) --> Z[Error: AccountID missing];

    C --> D{Tool Request has org_id?};
    D -- Yes --> E[Use Request org_id];
    D -- No --> F{Global OrgID exists?};
    F -- Yes --> G[Use Global OrgID];
    F -- No --> H[org_id is empty];

    E --> I{Tool Request has project_id?};
    G --> I;
    H --> I;

    I -- Yes --> J[Use Request project_id];
    I -- No --> K{Global ProjectID exists?};
    K -- Yes --> L[Use Global ProjectID];
    K -- No --> M[project_id is empty];

    J --> N{Tool Declared Scope as Required?};
    L --> N;
    M --> N;
    
    N -- Yes --> O{OrgID or ProjectID empty?};
    O -- Yes --> Z2[Error: Org/Project Required but missing];
    O -- No --> P[Return Resolved Scope];
    N -- No (Optional) --> P;
```

### Code Implementation Details

**1. `pkg/harness/scope.go`**

This file contains the core logic for scope handling within `harness-mcp`.

*   `WithScope()`: This function adds `org_id` and `project_id` parameters to a tool definition.
    ```go
    // Simplified from pkg/harness/scope.go
    func WithScope(config *config.Config, required bool) mcp.ToolOption {
        return func(tool *mcp.Tool) { // It's a function that modifies a tool
            var opt mcp.PropertyOption
            if required {
                opt = mcp.Required() // Mark as required if needed
            }
            // Add org_id parameter
            tool.AddParameter(mcp.NewStringParameter("org_id").
                WithDescription("The ID of the organization.").
                WithDefault(config.OrgID). // Default from global config
                AddOptions(opt),            // Apply required option if set
            )
            // Add project_id parameter similarly
            tool.AddParameter(mcp.NewStringParameter("project_id").
                WithDescription("The ID of the project.").
                WithDefault(config.ProjectID).
                AddOptions(opt),
            )
        }
    }
    ```
    This function uses features of the `mcp-go` library (which `harness-mcp` is built upon) to define tool parameters with descriptions and default values.

*   `fetchScope()`: This function resolves the scope.
    ```go
    // Simplified from pkg/harness/scope.go
    func fetchScope(config *config.Config, request mcp.CallToolRequest, required bool) (dto.Scope, error) {
        if config.AccountID == "" {
            return dto.Scope{}, fmt.Errorf("account ID is required from server configuration")
        }

        scope := dto.Scope{
            AccountID: config.AccountID,
            OrgID:     config.OrgID,     // Start with global defaults
            ProjectID: config.ProjectID, // Start with global defaults
        }

        // Check if provided in the tool request and override if so
        orgFromRequest, foundOrg := request.Params.GetString("org_id")
        if foundOrg && orgFromRequest != "" {
            scope.OrgID = orgFromRequest
        }

        projectFromRequest, foundProject := request.Params.GetString("project_id")
        if foundProject && projectFromRequest != "" {
            scope.ProjectID = projectFromRequest
        }

        if required { // If tool declared org/project as required...
            if scope.OrgID == "" || scope.ProjectID == "" {
                return scope, fmt.Errorf("org ID and project ID are required for this tool")
            }
        }
        return scope, nil
    }
    ```
    This clearly shows the logic: start with global config, override with tool request parameters if present, and then validate if required.

**2. How the API Client Uses Scope (`client/client.go`)**

The [Harness API Client](05_harness_api_client_.md) has an internal helper `addScope` (not directly exported but used by its service methods) to take the `dto.Scope` object and add the correct query parameters to API requests.

```go
// Simplified from client/client.go
// This function is typically called by methods like client.Get() or client.Post()
// before making the HTTP request.
// 'params' is a map that will be converted to URL query parameters e.g. ?key1=value1&key2=value2

func addScope(scope dto.Scope, params map[string]string) {
	params["accountIdentifier"] = scope.AccountID
	if scope.OrgID != "" { // Only add if not empty
		params["orgIdentifier"] = scope.OrgID
	}
	if scope.ProjectID != "" { // Only add if not empty
		params["projectIdentifier"] = scope.ProjectID
	}
}

// Example usage within a service method (e.g., Pipelines.Get)
// ...
// resolvedScope, _ := harness.fetchScope(...)
// queryParams := make(map[string]string)
// addScope(resolvedScope, queryParams) // Populates queryParams
// apiClient.Get(ctx, path, queryParams, &responseData) // queryParams used here
// ...
```
When the API client's `Get` or `Post` methods are called (as seen in [Chapter 5: Harness API Client](05_harness_api_client_.md)), they internally use `addScope` (or similar logic via `addQueryParams`) to ensure that `accountIdentifier`, `orgIdentifier`, and `projectIdentifier` are correctly included in the API request URL if the `dto.Scope` provides them.

## Conclusion

Scope Handling is all about ensuring that `harness-mcp` tells the Harness API *where* to perform an action. By defining a **scope** (Account ID, Organization ID, Project ID), either globally through [Server Configuration](04_server_configuration_.md) or specifically per tool invocation, you provide the necessary "address" for API calls. Helper functions like `harness.WithScope` make it easy for tools to declare they accept scope parameters, and `harness.fetchScope` intelligently resolves the correct scope to use, prioritizing tool-specific inputs over global defaults.

This precise addressing ensures that when `harness-mcp` interacts with Harness via the [Harness API Client](05_harness_api_client_.md), it's always working in the right context.

Now that we understand how the server is configured, how it talks to Harness, and how it knows the context for its actions, what about the actual data it exchanges with Harness? What format does it come in, and how does `harness-mcp` understand it? That's what we'll explore next!

Next up: [Chapter 7: Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos__.md)