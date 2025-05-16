# Chapter 6: Harness API Client

Welcome to Chapter 6! In [Chapter 5: Tool Parameter Handling](05_tool_parameter_handling_.md), we learned how tools in `mcp-server` receive the specific instructions they need, like a `pipeline_id`. Once a tool has its instructions and knows the [Scope (Account, Org, Project)](04_scope_management__account__org__project_.md), it often needs to communicate with the external Harness platform to get data or perform actions. How does `mcp-server` actually "talk" to Harness? That's the job of the **Harness API Client**.

## What's the Big Idea? The Server's Official Messenger

Imagine our `mcp-server` has a special department, a highly skilled messenger service, whose only job is to communicate with the "Harness Headquarters" (the Harness API platform).

*   When a tool (like `get_pipeline`) needs information from Harness, it writes down its request in a very specific way.
*   It hands this request to the **Harness API Client** (our messenger).
*   The messenger knows the exact address of Harness HQ, speaks its language perfectly (HTTP requests), and carries the official credentials (your API key) to prove it's allowed to ask for things.
*   The messenger travels to Harness HQ, delivers the request, waits for the reply, and brings it back.
*   Finally, the messenger translates Harness HQ's reply into a format the tool can understand.

The **Harness API Client** is this dedicated messenger service. It handles all the nitty-gritty details of making requests to the Harness API and understanding the responses.

**Use Case: Fetching Pipeline Details from Harness**

Let's say our `get_pipeline` tool has determined it needs to fetch details for pipeline `P123` in `org_A` and `project_X`.
1.  The `get_pipeline` tool doesn't know how to directly make an internet call to Harness.
2.  Instead, it tells the Harness API Client: "Please get me the details for pipeline `P123` from `org_A`/`project_X`."
3.  The Harness API Client takes this, forms a proper HTTP request that the Harness platform understands, sends it, and brings back the pipeline's information.

This component ensures that tools don't need to worry about the complexities of HTTP, authentication, or JSON parsing. They just delegate the communication task.

## Key Responsibilities of the Messenger (Harness API Client)

The Harness API Client is responsible for several critical tasks:

1.  **Formatting Requests:** It takes instructions from the `mcp-server`'s [Tools](03_tools_and_toolsets_.md) (e.g., "get pipeline 'my-pipe'") and translates them into precise HTTP requests that the Harness API understands. This includes setting the correct URL, HTTP method (GET, POST, etc.), and any necessary query parameters (like `accountIdentifier`, `orgIdentifier`, `projectIdentifier` from [Scope Management](04_scope_management__account__org__project_.md)).

2.  **Sending Requests:** It actually makes the network call over the internet to the Harness API endpoints.

3.  **Authentication:** For every request it sends, it includes your Harness API key. This key, provided via [Configuration Management](02_configuration_management_.md), tells the Harness platform that `mcp-server` is authorized to act on your behalf.

4.  **Parsing Responses:** When Harness sends back a reply (usually in JSON format), the API Client reads this reply and converts it into Go data structures that the tools can easily work with. These structures are often [Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos_.md).

5.  **Handling Errors:** If something goes wrong during communication (e.g., network issue, Harness API returns an error like "Not Found" or "Unauthorized"), the API Client detects this and reports the error back to the tool in a structured way.

## How the Harness API Client Solves Our Use Case

Let's see how the `get_pipeline` tool uses the Harness API Client to fetch pipeline `P123`:

1.  **Tool Prepares:** The `get_pipeline` tool has:
    *   The `pipeline_id`: "P123" (from [Tool Parameter Handling](05_tool_parameter_handling_.md)).
    *   The `scope`: Account ID "acc_xyz", Org ID "org_A", Project ID "project_X" (from [Scope Management (Account, Org, Project)](04_scope_management__account__org__project_.md)).
    *   Access to an instance of the Harness API Client (which was initialized with the API key when `mcp-server` started).

2.  **Tool Delegates to API Client:** The tool calls a specific function on the API Client, something like:
    ```go
    // Conceptual call within the get_pipeline tool's handler
    // 'apiClient' is the Harness API Client instance
    // 'currentScope' contains Account, Org, Project IDs
    // 'pipelineID' is "P123"
    pipelineData, err := apiClient.Pipelines.Get(ctx, currentScope, pipelineID)
    ```

3.  **API Client Takes Over:**
    *   The `apiClient.Pipelines.Get(...)` function knows it needs to make an HTTP `GET` request.
    *   It constructs the correct URL, like `https://app.harness.io/pipeline/api/pipelines/P123?accountIdentifier=acc_xyz&orgIdentifier=org_A&projectIdentifier=project_X`.
    *   It adds the `x-api-key` header with your API key.
    *   It sends the request to Harness.
    *   Harness processes the request and sends back a JSON response containing the pipeline details.
    *   The API Client receives this JSON and converts it into a `dto.PipelineData` struct.

4.  **API Client Returns to Tool:** The `pipelineData` (now a Go struct) and any `err` are returned to the `get_pipeline` tool. The tool can now use this structured data.

The `get_pipeline` tool didn't need to know anything about HTTP, JSON, or API keys directly!

## Under the Hood: The Messenger's Operations

Let's look at how the Harness API Client is structured and operates internally.

### The Big Picture: Step-by-Step Communication

1.  **Initialization:** When `mcp-server` starts, the Harness API Client is created using your API key and the Harness base URL from the [Configuration Management](02_configuration_management_.md). This usually happens in `cmd/harness-mcp-server/main.go`'s `runStdioServer` function.
    ```go
    // Simplified from cmd/harness-mcp-server/main.go
    // cfg is the server's configuration
    apiClient, _ := client.NewWithToken(cfg.BaseURL, cfg.APIKey)
    // This 'apiClient' is then passed to tools when they are initialized.
    ```

2.  **Tool Calls a Service Method:** A tool needs to get pipeline data, so it calls a method like `apiClient.Pipelines.Get(...)`. The `apiClient` has sub-clients or "services" for different Harness modules (Pipelines, Repositories, etc.).

3.  **Service Method Prepares:** The specific service method (e.g., `Pipelines.Get` in `client/pipelines.go`) knows the specific API path for that operation. It formats this path and gathers any necessary query parameters, including scope identifiers.

4.  **Core Client Executes:** The service method then calls a more generic method on the core client (e.g., `client.Client.Get(...)` in `client/client.go`). This core method:
    *   Builds the complete URL.
    *   Creates a standard Go `http.Request` object.
    *   Adds the crucial `x-api-key` header for authentication.
    *   Uses Go's built-in `http.Client` to actually send the request over the network.

5.  **Response Handling:**
    *   The core client receives the `http.Response` from Harness.
    *   It checks the HTTP status code. If it's an error code (like 404 Not Found, 500 Internal Server Error), it translates this into a Go error.
    *   If successful, it reads the response body (which is JSON).
    *   It "unmarshals" (parses) the JSON into a pre-defined Go struct (a [Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos_.md) like `dto.PipelineData`).

6.  **Result Returned:** The parsed data (or an error) is passed back up the chain, from the core client to the service method, and finally to the tool that made the initial call.

### Sequence Diagram: `get_pipeline` using the API Client

```mermaid
sequenceDiagram
    participant Tool as Tool (e.g., get_pipeline)
    participant PipelineSvc as client.PipelineService
    participant CoreClient as client.Client (core methods)
    participant GoHTTP as Go http.Client
    participant HarnessAPI as Harness Platform API

    Tool->>PipelineSvc: Get(ctx, scope, pipelineID)
    PipelineSvc-->>PipelineSvc: Format API path & query params (e.g., /pipelines/ID?org=X)
    PipelineSvc->>CoreClient: Get(ctx, path, params, &responseDataStruct)
    CoreClient-->>CoreClient: Build full HTTP request, add API key to headers
    CoreClient->>GoHTTP: Do(httpRequest)
    GoHTTP->>HarnessAPI: HTTP GET request to Harness
    HarnessAPI-->>GoHTTP: HTTP Response (JSON data for pipeline)
    GoHTTP-->>CoreClient: http.Response object
    CoreClient-->>CoreClient: Check status, parse JSON into responseDataStruct
    CoreClient-->>PipelineSvc: responseDataStruct (or error)
    PipelineSvc-->>Tool: pipelineData (or error)
end
```

### Diving into the Code (Simplified)

The Harness API Client code primarily lives in the `client/` directory of the `mcp-server` project.

**1. Client Initialization (`client/client.go`)**

The main `Client` struct holds the HTTP client, base URL, API key, and instances of specific services.

```go
// Simplified from client/client.go
import (
	"net/http"
	"net/url"
	"time"
	// ... other imports ...
)

type Client struct {
	client  *http.Client // Go's standard HTTP client
	BaseURL *url.URL
	APIKey  string

	// Services for different Harness modules
	Pipelines    *PipelineService
	PullRequests *PullRequestService
	// ... and others ...
}

// NewWithToken creates a new client
func NewWithToken(uri, apiKey string) (*Client, error) {
	parsedURL, _ := url.Parse(uri) // Ensure uri is a valid URL
	c := &Client{
		client:  &http.Client{Timeout: 10 * time.Second}, // Basic HTTP client with a timeout
		BaseURL: parsedURL,
		APIKey:  apiKey,
	}
	// Initialize specific services, passing a reference to this core client
	c.Pipelines = &PipelineService{client: c}
	c.PullRequests = &PullRequestService{client: c}
	// ... initialize other services ...
	return c, nil
}
```
When `client.NewWithToken(config.BaseURL, config.APIKey)` is called during server startup, it sets up this main client. Each "service" (like `PipelineService`) gets a reference back to this main client so it can use its core communication methods.

**2. Service-Specific Method (e.g., `client/pipelines.go`)**

Each service provides methods for specific API operations. For example, `PipelineService` has a `Get` method.

```go
// Simplified from client/pipelines.go
// 'p.client' refers to the main client.Client instance.
// 'scope' is a dto.Scope struct with AccountID, OrgID, ProjectID.
func (p *PipelineService) Get(ctx context.Context, scope dto.Scope, pipelineID string) (*dto.Entity[dto.PipelineData], error) {
	// 1. Construct the specific API path for getting a pipeline
	path := fmt.Sprintf("pipeline/api/pipelines/%s", pipelineID)

	params := make(map[string]string)
	addScope(scope, params) // Helper to add account, org, project identifiers to params

	// 2. Prepare a Go struct to hold the expected JSON response
	response := &dto.Entity[dto.PipelineData]{} // This is a DTO

	// 3. Call the core client's generic Get method to do the actual HTTP work
	err := p.client.Get(ctx, path, params, nil /* headers */, response)
	if err != nil {
		return nil, fmt.Errorf("failed to get pipeline: %w", err)
	}
	return response, nil
}
```
This method knows the *specifics* for fetching a pipeline: the path format and the expected response structure (`dto.Entity[dto.PipelineData]`). It then delegates the *general* HTTP work to `p.client.Get`. The `addScope` helper function (from `client/client.go`) is used to add `accountIdentifier`, `orgIdentifier`, and `projectIdentifier` to the request parameters based on the [Scope Management (Account, Org, Project)](04_scope_management__account__org__project_.md).

**3. Core HTTP `Get` Method (`client/client.go`)**

This is a generic method for making HTTP GET requests.

```go
// Simplified from client/client.go
func (c *Client) Get(
	ctx context.Context,
	path string,
	params map[string]string,
	headers map[string]string,
	responseBodyTarget interface{}, // Where to unmarshal the JSON response
) error {
	// Build the full URL: BaseURL + path
	fullURL := appendPath(c.BaseURL.String(), path)
	httpReq, _ := http.NewRequestWithContext(ctx, http.MethodGet, fullURL, nil)

	addQueryParams(httpReq, params) // Add parameters like ?orgIdentifier=...
	for key, value := range headers {
		httpReq.Header.Add(key, value)
	}

	// Call the Do method, which adds auth and sends the request
	httpResp, err := c.Do(httpReq)
	// ... error checking & ensure body is closed (defer httpResp.Body.Close()) ...

	// If responseBodyTarget is provided, try to parse JSON into it
	if responseBodyTarget != nil && httpResp != nil && httpResp.Body != nil {
		if err := unmarshalResponse(httpResp, responseBodyTarget); err != nil {
			// ... handle unmarshalling error ...
			return err
		}
	}
	// ... map status code to error if needed ...
	return nil // Or an error if one occurred
}
```
This method handles creating the request, adding query parameters, and then passes it to `c.Do()`. After getting a response, it calls `unmarshalResponse` to parse the JSON.

**4. The `Do` Method: Adding Authentication (`client/client.go`)**

This is where the API key is added before the request is actually sent.

```go
// Simplified from client/client.go
const apiKeyHeader = "x-api-key"

func (c *Client) Do(r *http.Request) (*http.Response, error) {
	slog.Debug("Request", "method", r.Method, "url", r.URL.String())
	// Crucial step: Add the API key to the request headers!
	r.Header.Add(apiKeyHeader, c.APIKey)

	// Use the underlying standard Go http.Client to send the request
	return c.client.Do(r)
}
```
The `r.Header.Add(apiKeyHeader, c.APIKey)` line is vital for authentication with the Harness API.

**5. Response Parsing and Error Handling (`client/client.go`)**

Helper functions deal with the response:

```go
// Simplified from client/client.go
// mapStatusCodeToError converts HTTP status codes to Go errors
func mapStatusCodeToError(statusCode int) error {
	switch {
	case statusCode == http.StatusNotFound:
		return ErrNotFound // A pre-defined error
	case statusCode >= http.StatusInternalServerError:
		return ErrInternal // Another pre-defined error
	// ... other status codes ...
	}
	return nil
}

// unmarshalResponse reads the HTTP response body and parses it as JSON
func unmarshalResponse(resp *http.Response, data interface{}) error {
	if resp == nil || resp.Body == nil { /* ... handle ... */ }
	bodyBytes, _ := io.ReadAll(resp.Body) // Read all bytes from response

	// Attempt to parse the JSON body into the 'data' struct (e.g., a DTO)
	if err := json.Unmarshal(bodyBytes, data); err != nil {
		return fmt.Errorf("error deserializing response: %w, body: %s", err, string(bodyBytes))
	}
	return nil
}
```
`mapStatusCodeToError` helps turn HTTP errors (like 404) into meaningful Go errors. `unmarshalResponse` uses `json.Unmarshal` to convert the JSON text from Harness into the Go structs (the `data` argument) that the rest of the `mcp-server` can use. These `data` structs are typically [Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos_.md).

## Conclusion

The Harness API Client is a vital component of `mcp-server`. It acts as a specialized "messenger" that handles all the complexities of communicating with the Harness platform. It takes simple instructions from tools, formats them into proper HTTP requests, adds authentication, sends them, and then parses the responses back into usable Go data structures.

This abstraction allows the tools within `mcp-server` to focus on their specific logic without worrying about the low-level details of API communication. They can simply ask the client to "get this" or "do that" with Harness.

The data structures that the Harness API Client uses to send and receive information (like `dto.PipelineData`) are very important. In the next chapter, we'll take a closer look at these [Data Transfer Objects (DTOs)](07_data_transfer_objects__dtos_.md).