# Chapter 4: Scope Management (Account, Org, Project)

In [Chapter 3: Tools and Toolsets](03_tools_and_toolsets_.md), we learned about the specific actions (Tools) that `mcp-server` can perform, like `get_pipeline`. But when you ask the server to get a pipeline, how does it know *which* Harness account, organization, or project that pipeline belongs to? This is where **Scope Management** comes in.

## What's the Big Idea? Finding the Right Address

Imagine you want to send a package. You can't just write "John Doe" on it and expect it to arrive. You need a full address:
*   Country (like your Harness **Account ID**)
*   State/Region (like your Harness **Organization ID**)
*   City (like your Harness **Project ID**)
*   Street & House Number (like the specific resource ID, e.g., `pipeline_id`)

**Scope Management** in `mcp-server` is all about figuring out this "full address" (Account, Organization, Project) for any operation. Many Harness API calls need this scope to know exactly where to look for or create resources. Without the correct scope, the Harness API wouldn't know which specific account, organization, or project your request pertains to.

**Use Case: Getting a Specific Pipeline**

Let's say you want `mcp-server` to fetch details for a pipeline named `my_app_pipeline`. The `get_pipeline` tool needs to know:
1.  Which **Harness Account** contains this pipeline?
2.  Within that account, which **Organization**?
3.  And within that organization, which **Project**?

Scope management helps `mcp-server` answer these "where" questions so it can accurately target the right resources in Harness.

## What is "Scope"? The "Where" for Your Resources

In Harness, your resources (like pipelines, connectors, services, etc.) are organized in a hierarchy:

1.  **Account:** This is your top-level Harness subscription. Everything you do in Harness lives within an account. The `mcp-server` typically knows your Account ID from the API key you provide during [Configuration Management](02_configuration_management_.md).
2.  **Organization (Org):** Within an account, you can create multiple Organizations. Orgs help you group related projects, often for different business units or teams. Example: `default_org`, `finance_org`.
3.  **Project:** Within an Organization, you can create multiple Projects. Projects are where you define and manage your actual software delivery pipelines, services, and environments. Example: `my_application_project`, `platform_services_project`.

So, the "scope" is the combination of `AccountID`, `OrgID`, and `ProjectID` that pinpoints the exact location of a resource.

## How `mcp-server` Determines Scope

`mcp-server` is clever about figuring out the scope. It can get this information in a couple of ways:

1.  **Default Scope (from Server Configuration):**
    When you set up `mcp-server`, you can provide default values for your Organization ID and Project ID (e.g., using environment variables `HARNESS_DEFAULT_ORG_ID` and `HARNESS_DEFAULT_PROJECT_ID`, as discussed in [Configuration Management](02_configuration_management_.md)). The Account ID is usually derived automatically from your `HARNESS_API_KEY`.
    If you don't specify an org or project in your request, `mcp-server` will use these defaults. This is super handy if you mostly work within one main project.

2.  **Request-Specific Scope (from User's Request):**
    When you (or a client application) send a request to `mcp-server` to execute a tool, you can explicitly include `org_id` and `project_id` as parameters in that request. This tells `mcp-server` to use these specific values for *this particular operation*.

3.  **The Precedence Rule: Request Overrides Defaults!**
    This is important: If you provide `org_id` or `project_id` in your request, those values will **override** any default org/project IDs set in the server's configuration for that specific request. The Account ID, however, is typically fixed by the server's configuration (API key).

## Use Case: Getting a Specific Pipeline (with Scope!)

Let's see how this works with our `get_pipeline` tool. We want to get details for a pipeline with `pipeline_id = "P123"`.

**Scenario A: Relying on Default Scope**

*   **Your `mcp-server` Configuration (e.g., from environment variables):**
    *   `HARNESS_API_KEY` (which implies `AccountID = "acc_alpha"`)
    *   `HARNESS_DEFAULT_ORG_ID = "org_main"`
    *   `HARNESS_DEFAULT_PROJECT_ID = "project_frontend"`
*   **Your MCP Request to `mcp-server`:**
    ```json
    {
        "tool_name": "get_pipeline",
        "parameters": {
            "pipeline_id": "P123"
        }
    }
    ```
    (Notice: no `org_id` or `project_id` in the request parameters)
*   **Resolved Scope by `mcp-server`:**
    *   Account ID: `acc_alpha` (from API key)
    *   Organization ID: `org_main` (from default config)
    *   Project ID: `project_frontend` (from default config)
    The `mcp-server` will ask Harness for pipeline "P123" located at `acc_alpha / org_main / project_frontend`.

**Scenario B: Specifying Scope in the Request**

*   **Your `mcp-server` Configuration (same defaults as above):**
    *   `HARNESS_API_KEY` (`AccountID = "acc_alpha"`)
    *   `HARNESS_DEFAULT_ORG_ID = "org_main"`
    *   `HARNESS_DEFAULT_PROJECT_ID = "project_frontend"`
*   **Your MCP Request to `mcp-server` (this time, with explicit org and project):**
    ```json
    {
        "tool_name": "get_pipeline",
        "parameters": {
            "pipeline_id": "P123",
            "org_id": "org_backend_services",
            "project_id": "project_api_gateway"
        }
    }
    ```
*   **Resolved Scope by `mcp-server`:**
    *   Account ID: `acc_alpha` (from API key)
    *   Organization ID: `org_backend_services` (from request, overrides default)
    *   Project ID: `project_api_gateway` (from request, overrides default)
    Now, `mcp-server` will look for pipeline "P123" at the explicitly requested location: `acc_alpha / org_backend_services / project_api_gateway`.

This flexibility allows you to set convenient defaults for common tasks while still being able to target resources in any org or project when needed.

## Under the Hood: How Scope is Managed Internally

Let's peek behind the curtain to see how `mcp-server` handles scope when a request comes in.

### The Big Picture: Step-by-Step

1.  **Request Arrives:** A client sends an MCP request to the [MCP Server Core](01_mcp_server_core_.md), specifying a tool (e.g., `get_pipeline`) and its parameters (e.g., `pipeline_id`, and optionally `org_id`, `project_id`).
2.  **Tool Handler Invoked:** The Server Core calls the specific handler function for the requested tool.
3.  **Scope Determination:** Inside the tool's handler, a special helper function (like `fetchScope` in `mcp-server`) is typically called. This function is responsible for figuring out the correct Account, Org, and Project IDs.
4.  **Check Request Parameters:** The `fetchScope` helper first looks at the parameters sent in the current MCP request. Does the request include `org_id` or `project_id`?
5.  **Use Defaults if Necessary:** If `org_id` or `project_id` are *not* found in the request parameters, the `fetchScope` helper falls back to using the default Org ID and Project ID that were loaded from the server's [Configuration Management](02_configuration_management_.md).
6.  **Account ID from Config:** The Account ID is almost always taken directly from the server's configuration (derived from the API key).
7.  **Scope Object Created:** These three pieces of information (Account ID, Org ID, Project ID) are bundled together into a structured object, often called a `Scope` object (like `dto.Scope` in `mcp-server`).
8.  **Pass Scope to API Client:** This `Scope` object is then passed along to the [Harness API Client](06_harness_api_client_.md) when it makes the actual call to the Harness API. The API client uses these IDs to construct the correct API endpoint URL or request payload.

Here’s a simplified diagram of this flow:

```mermaid
sequenceDiagram
    participant Client as Client
    participant MCPServerCore as MCP Server Core
    participant ToolHandler as Tool (e.g., get_pipeline)
    participant ScopeHelper as Scope Helper (fetchScope)
    participant ServerConfig as Server Configuration
    participant APIClient as Harness API Client

    Client->>MCPServerCore: Request (tool: "get_pipeline", params: {pipeline_id: "X", org_id: "user_org"})
    MCPServerCore->>ToolHandler: Execute get_pipeline handler
    ToolHandler->>ScopeHelper: fetchScope(request_params, server_config)
    ScopeHelper->>ServerConfig: Read default_org_id, default_project_id, account_id
    ServerConfig-->>ScopeHelper: Defaults (e.g., default_org="default_o", account_id="acc1")
    Note over ScopeHelper: User's "user_org" from request_params overrides default_org. Project uses default.
    ScopeHelper-->>ToolHandler: Resolved Scope (account_id="acc1", org_id="user_org", project_id="default_proj_id_from_config")
    ToolHandler->>APIClient: Call Harness API (e.g., GetPipeline) with Resolved Scope
    APIClient-->>APIClient: Construct API call using scope IDs
    APIClient-->>ToolHandler: API Response
    ToolHandler-->>MCPServerCore: Result
    MCPServerCore-->>Client: MCP Response
end
```

### Diving into the Code (Simplified)

Let's look at some simplified code snippets to see how this is implemented in `mcp-server`.

**1. Defining Scope Parameters for a Tool (`pkg/harness/scope.go`)**

When a tool (like `get_pipeline`) is defined, it can be set up to accept `org_id` and `project_id` as optional parameters. The `WithScope` function helps with this.

```go
// From pkg/harness/scope.go (simplified)
// 'config' here is the server's loaded configuration.
// 'required' would be true if the tool *must* have org/project.
func WithScope(config *config.Config, required bool) mcp.ToolOption {
    return func(tool *mcp.Tool) {
        // Define the 'org_id' parameter for the tool
        mcp.WithString("org_id", // Parameter name
            mcp.Description("Optional ID of the organization."),
            // If a default org ID is set in server config, make it the default for this param
            mcp.DefaultString(config.DefaultOrgID),
            // If 'required' is true, this parameter would be marked as mcp.Required()
        )(tool)

        // Define the 'project_id' parameter similarly
        mcp.WithString("project_id",
            mcp.Description("Optional ID of the project."),
            mcp.DefaultString(config.DefaultProjectID),
        )(tool)
    }
}
```
This `WithScope` function is used when defining a tool. For example, if `get_pipeline` needs scope, its definition might include `GetPipelineTool(..., WithScope(serverConfig, true))`. This tells the [MCP Server Core](01_mcp_server_core_.md) that `get_pipeline` can accept `org_id` and `project_id` from the client, and if they aren't provided, the defaults from `serverConfig` should be hinted.

**2. Fetching and Resolving the Scope (`pkg/harness/scope.go`)**

The `fetchScope` function is the workhorse that actually figures out the final scope to use.

```go
// From pkg/harness/scope.go (simplified)
// 'config' is the server's configuration.
// 'request' is the incoming MCP call data.
// 'required' indicates if org/project are mandatory for this specific API call.
func fetchScope(config *config.Config, request mcp.CallToolRequest, required bool) (dto.Scope, error) {
    // Start with defaults from server configuration
    scope := dto.Scope{
        AccountID: config.AccountID, // Account ID always comes from server config
        OrgID:     config.DefaultOrgID,
        ProjectID: config.DefaultProjectID,
    }

    // Check if 'org_id' was provided in the request parameters
    orgFromRequest, foundOrg := request.Params.GetString("org_id")
    if foundOrg && orgFromRequest != "" {
        scope.OrgID = orgFromRequest // Override default with request value
    }

    // Check for 'project_id' from request parameters similarly
    projectFromRequest, foundProject := request.Params.GetString("project_id")
    if foundProject && projectFromRequest != "" {
        scope.ProjectID = projectFromRequest // Override default
    }

    // If org/project are required for this tool, check they are now set
    if required {
        if scope.OrgID == "" {
            return scope, fmt.Errorf("org ID is required for this operation but not found")
        }
        // Similar check for ProjectID
    }
    return scope, nil
}
```
This function first sets up a `dto.Scope` object (defined in `client/dto/scope.go`) using the server's Account ID and default Org/Project IDs. Then, it checks if the incoming `request` has `org_id` or `project_id` parameters. If yes, it updates the `scope` object with these values, effectively overriding the defaults.

**3. Using the Scope in a Tool Handler (Conceptual)**

Inside a tool's handler function (the code that runs when a tool is called), `fetchScope` is used:

```go
// Conceptual tool handler for 'get_pipeline'
// 'config' and 'apiClient' are available to the handler.
handler := func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    // Determine the scope for this operation.
    // Let's say for get_pipeline, org and project are always required.
    currentScope, err := fetchScope(config, request, true)
    if err != nil {
        return nil, fmt.Errorf("failed to determine scope: %w", err)
    }

    // Get other parameters, like pipeline_id
    pipelineID, _ := request.Params.GetString("pipeline_id")

    // Now, use the 'currentScope' and 'pipelineID' to call the Harness API
    // via the apiClient (Harness API Client).
    // pipelineData, err := apiClient.Pipelines.Get(ctx, currentScope, pipelineID)
    // ... handle response and return ...
    return mcp.NewToolResultText("Pipeline data for " + pipelineID), nil
}
```
The `currentScope` (which is a `dto.Scope` struct) now holds the definitive Account, Org, and Project IDs to be used for this specific API call.

**4. How the [Harness API Client](06_harness_api_client_.md) Uses the Scope (`client/client.go`)**

Finally, the `dto.Scope` object is passed to methods of the [Harness API Client](06_harness_api_client_.md). The client then uses these IDs to construct the correct query parameters for the Harness API.

```go
// From client/client.go (simplified)
// This helper function adds scope identifiers to a map of API query parameters.
func addScope(scope dto.Scope, params map[string]string) {
    params["accountIdentifier"] = scope.AccountID
    if scope.OrgID != "" { // Only add if present
        params["orgIdentifier"] = scope.OrgID
    }
    if scope.ProjectID != "" { // Only add if present
        params["projectIdentifier"] = scope.ProjectID
    }
}

// Example of how a service method in the API client might use addScope:
// (Conceptual - actual methods are in files like client/pipeline.go)
/*
func (s *PipelineService) Get(ctx context.Context, scope dto.Scope, pipelineID string) (*dto.Pipeline, error) {
    apiParams := make(map[string]string) // Parameters for the HTTP GET request
    addScope(scope, apiParams)           // Add account, org, project from resolved scope
    // ... add other necessary parameters like pipelineID ...

    // The client.Get method would then build a URL like:
    // .../pipelines/pipelineID?accountIdentifier=...&orgIdentifier=...&projectIdentifier=...
    // return s.client.Get(ctx, path, apiParams, nil, &pipelineResponse)
}
*/
```
The `addScope` function ensures that the `accountIdentifier`, `orgIdentifier`, and `projectIdentifier` query parameters are correctly added to the API request sent to Harness. This tells Harness precisely where to find the requested resource.

## Conclusion

Scope Management is like providing a precise address for your `mcp-server` requests. It ensures that when you ask for a resource or want to perform an action, `mcp-server` knows exactly which Harness Account, Organization, and Project you're referring to. It achieves this by intelligently using:
*   Default scopes from your server's [Configuration Management](02_configuration_management_.md).
*   Scope details provided directly in your MCP requests.

Understanding scope is crucial for using `mcp-server` effectively, as it dictates the context for almost every interaction with Harness.

We've seen how tools are defined (Chapter 3) and how `mcp-server` knows *where* to act (this chapter). But tools often need other pieces of information beyond just the scope – like the ID of a specific pipeline, or the name for a new resource. In the next chapter, we'll explore [Tool Parameter Handling](05_tool_parameter_handling_.md) in more detail.