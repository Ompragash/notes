# Chapter 1: MCP Server Core

Welcome to the `mcp-server` tutorial! We're excited to help you understand how this powerful tool works. In this very first chapter, we'll dive into the absolute heart of the `mcp-server`: the **MCP Server Core**.

## What's the Big Idea? The Switchboard Operator

Imagine you're trying to get information from a very large, very busy company. You can't just wander around opening doors! You need to talk to a central operator. This operator has a specific way they need you to ask for things. If you ask correctly, they'll connect you to the right department or person who can help.

The **MCP Server Core** is exactly like that specialized switchboard operator for the `mcp-server`.

*   **It listens for requests:** Just like an operator waits for a phone call.
*   **Requests must be in a special format:** This format is called the **Model Context Protocol (MCP)**. If you don't "speak MCP," the server core won't understand you.
*   **It finds the right "Tool":** If your request is valid, the server core figures out what you want to do (e.g., "get details about a pipeline") and passes your request to the specific "Tool" designed for that job. A Tool is just a specific function within `mcp-server`.
*   **It sends back a response:** Once the Tool has done its work, the server core takes the result and sends it back to you, again in the MCP format.

**Use Case: Getting Pipeline Details**

Let's say you, or another program you're using (like an AI assistant), wants to get details for a specific pipeline in your Harness account. You can't ask the `mcp-server` in plain English. You need to send a structured MCP request. The MCP Server Core will receive this, understand you want pipeline details, call the "get_pipeline" Tool, and then return the pipeline's information to you.

This chapter will help you understand this central "operator" so you can see how `mcp-server` processes your requests.

## Key Ideas to Grasp

1.  **Model Context Protocol (MCP):** This is the language or set of rules for how to make requests and how responses are structured. Think of it as the specific phrases the switchboard operator understands, like "Connect me to extension 123 for sales."
2.  **Requests:** A message sent *to* the `mcp-server` asking it to do something. It will specify which Tool to use and any necessary information (parameters) for that Tool.
3.  **Tools:** These are the individual functions within `mcp-server` that perform specific actions, like `get_pipeline` or `list_repositories`. We'll cover these in more detail in [Tools and Toolsets](03_tools_and_toolsets_.md). For now, just know they are the "departments" our operator connects you to.
4.  **Responses:** A message sent *from* the `mcp-server` back to the requester, containing the results of the action or any errors.

## How the Server Core Solves Our Use Case (Getting Pipeline Details)

Let's walk through our "get pipeline details" example:

1.  **You (or a client application) send a request:** This request is formatted according to MCP. It might conceptually look like this:
    *   "Hey `mcp-server`! I want to use the `get_pipeline` Tool."
    *   "The `pipeline_id` I care about is `my_awesome_pipeline`."
    *   "My `HARNESS_ACCOUNT_ID` is `your_account_id`" (This might be known from [Configuration Management](02_configuration_management_.md) or passed in the request).

2.  **The MCP Server Core receives this request.** It's always listening.

3.  **It checks the language (MCP):** "Is this a valid MCP request? Yes."

4.  **It identifies the Tool:** "Aha! The user wants the `get_pipeline` Tool."

5.  **It calls the Tool:** The Server Core invokes the `get_pipeline` Tool, passing along the `pipeline_id` (`my_awesome_pipeline`) and any other necessary context like account or organization IDs.

6.  **The Tool does its job:** The `get_pipeline` Tool (which might use the [Harness API Client](06_harness_api_client_.md) under the hood) communicates with Harness to fetch the details for `my_awesome_pipeline`.

7.  **The Tool returns the result:** The Tool gives the pipeline details (or an error if something went wrong) back to the Server Core.

8.  **The Server Core formats and sends the response:** The Server Core packages these details into an MCP-formatted response and sends it back to you. The response might look like:
    *   "Okay, here are the details for `my_awesome_pipeline`: Name: My Awesome Pipeline, Status: Succeeded, ..." (This data is often structured using [Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos_.md)).

And that's it! The MCP Server Core has successfully acted as the intermediary.

## Under the Hood: A Peek Inside

Let's see what happens internally when a request comes in.

### The Big Picture: Step-by-Step

Imagine the `mcp-server` is running.

1.  A **Client** (like your terminal, an AI assistant, or a tool like MCP Inspector) sends a request. Since `mcp-server` often runs in `stdio` mode, this request usually comes in through "standard input" (like typing into a terminal).
2.  The **MCP Server Core** is listening. It reads the request.
3.  It **parses** the request. Is it valid JSON-RPC (the transport layer for MCP)? Does it specify a tool name?
4.  It **identifies the Tool** name (e.g., `get_pipeline`) from the parsed request.
5.  It **looks up** this tool from a list of registered [Tools and Toolsets](03_tools_and_toolsets_.md).
6.  If found, it **calls (executes)** the Tool's specific function, passing along any parameters (e.g., `pipeline_id`) from the request.
7.  The **Tool** does its work. This often involves talking to the Harness platform using your API key via the [Harness API Client](06_harness_api_client_.md).
8.  The Tool **returns a result** (e.g., pipeline data) or an error to the Server Core.
9.  The Server Core **formats this result** (or error) into a proper MCP response (again, as JSON-RPC).
10. The Server Core **sends this response back** to the Client, usually via "standard output."

Here's a simplified diagram of this flow:

```mermaid
sequenceDiagram
    participant C as Client
    participant MSC as MCP Server Core
    participant T as Tool (e.g., get_pipeline)
    participant HAPI as Harness API

    C->>MSC: MCP Request (tool: "get_pipeline", params: {pipelineId: "X"})
    MSC-->>MSC: Parse Request
    MSC-->>MSC: Identify Tool ("get_pipeline")
    MSC->>T: Execute Tool with params (pipelineId: "X")
    T->>HAPI: API call to fetch pipeline "X"
    HAPI-->>T: Pipeline Data for "X"
    T-->>MSC: Result (Pipeline Data)
    MSC-->>MSC: Format Response
    MSC-->>C: MCP Response (result: {pipeline data for "X"})
end
```

### Diving into the Code (Simplified)

The main entry point for running the server is in `cmd/harness-mcp-server/main.go`. When you run `./harness-mcp-server stdio`, the `stdioCmd`'s `RunE` function is executed.

```go
// From cmd/harness-mcp-server/main.go (simplified)

// stdioCmd is the command to start the server listening on standard input/output.
var stdioCmd = &cobra.Command{
    Use:   "stdio",
    Short: "Start stdio server",
    RunE: func(_ *cobra.Command, _ []string) error {
        // ... (load configuration, API key, etc.) ...
        // The config includes API_KEY, ORG_ID, PROJECT_ID, etc.
        // This is handled by [Configuration Management](02_configuration_management_.md).
        cfg := config.Config{ /* ... populated from flags/env ... */ }

        // This function sets up and runs the actual server logic.
        if err := runStdioServer(cfg); err != nil {
            return fmt.Errorf("failed to run stdio server: %w", err)
        }
        return nil
    },
}
```
This snippet shows how the `stdio` command is defined. When executed, it calls `runStdioServer`.

The `runStdioServer` function is where the core server components are initialized and started.

```go
// From cmd/harness-mcp-server/main.go (simplified)

func runStdioServer(config config.Config) error {
    // ... (setup logging, application context) ...

    slog.Info("Starting server")

    // Create the main MCP server object.
    // `harness.NewServer` comes from `pkg/harness/server.go`.
    harnessServer := harness.NewServer(version /*, ... other options ... */)

    // Initialize all the available Toolsets (like Pipelines, Pull Requests, etc.)
    // This is where [Tools and Toolsets](03_tools_and_toolsets_.md) are prepared.
    // It requires the Harness API client, created using details from the config.
    apiClient, _ := client.NewWithToken(config.BaseURL, config.APIKey)
    toolsets, _ := harness.InitToolsets(apiClient, &config)

    // Register the prepared tools with the server core.
    // Now the server core knows what tools it can offer.
    toolsets.RegisterTools(harnessServer)

    // Create an stdioServer. This is a specific type of server from the
    // mcp-go library that knows how to communicate over stdio (standard input/output).
    stdioServer := server.NewStdioServer(harnessServer)

    // Start listening! os.Stdin is where requests come from,
    // os.Stdout is where responses are sent.
    go func() {
        // This Listen method blocks until the server is stopped or an error occurs.
        stdioServer.Listen(context.Background(), os.Stdin, os.Stdout)
    }()

    slog.Info("Harness MCP Server running on stdio")
    // ... (wait for shutdown signal or error) ...
    return nil
}
```
In `runStdioServer`:
1.  `harness.NewServer()` creates our specific MCP server instance. This function is defined in `pkg/harness/server.go`.
2.  `harness.InitToolsets()` prepares all the individual tools (like `get_pipeline`). These tools often need access to the [Harness API Client](06_harness_api_client_.md) to interact with Harness.
3.  `toolsets.RegisterTools(harnessServer)` tells the server core about all the available tools.
4.  `server.NewStdioServer(harnessServer)` wraps our `harnessServer` with logic to handle communication over standard input/output. This comes from the `mcp-go` library, which provides the foundational MCP handling.
5.  `stdioServer.Listen(...)` starts the main loop, reading from `os.Stdin` for requests and writing to `os.Stdout` for responses.

The actual creation of the MCP server instance happens in `pkg/harness/server.go`:

```go
// From pkg/harness/server.go (simplified)

import (
	"github.com/mark3labs/mcp-go/mcp"      // Core MCP types
	"github.com/mark3labs/mcp-go/server" // MCP server library
)

// NewServer creates a new Harness MCP server.
func NewServer(version string, opts ...server.ServerOption) *server.MCPServer {
    // These are default settings for our Harness MCP server.
    defaultOpts := []server.ServerOption{
        server.WithToolCapabilities(true), // Tell clients what tools are available.
        server.WithLogging(),              // Enable basic logging of requests/responses.
    }
    opts = append(defaultOpts, opts...)

    // `server.NewMCPServer` comes from the mcp-go library.
    // It creates the generic MCP server brain.
    s := server.NewMCPServer(
        "harness-mcp-server", // A name for our server.
        version,              // The version of our server.
        opts...,              // Any additional options.
    )
    return s
}
```
This `NewServer` function from `pkg/harness/server.go` uses `server.NewMCPServer` from the `mcp-go` library. This library component handles much of the generic MCP protocol work: parsing incoming JSON-RPC messages, matching them to registered tools, calling the tool functions, and formatting responses. Our `harness-mcp-server` builds on top of this by providing the specific Harness tools and configuration.

So, the **MCP Server Core** is a combination of:
*   The generic MCP handling provided by the `mcp-go` library.
*   Our specific `harness-mcp-server` setup that initializes this library, registers Harness-specific [Tools and Toolsets](03_tools_and_toolsets_.md), and manages [Configuration Management](02_configuration_management_.md).

## Conclusion

You've now taken your first look at the MCP Server Core, the central nervous system of the `mcp-server`. It's like a diligent switchboard operator, understanding specially formatted requests (MCP), routing them to the correct "Tool" or department, and ensuring a response gets back to the caller. It relies on the `mcp-go` library for the fundamental MCP communication mechanics and our custom code to integrate Harness-specific functionalities.

Understanding the Server Core is crucial because everything else in `mcp-server` revolves around how it processes requests and invokes tools.

Now that we have a basic idea of what the server *is*, let's explore how it gets its necessary settings and secrets. In the next chapter, we'll dive into [Configuration Management](02_configuration_management_.md).