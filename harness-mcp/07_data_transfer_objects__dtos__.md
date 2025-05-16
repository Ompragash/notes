# Chapter 7: Data Transfer Objects (DTOs)

Welcome to Chapter 7! In the [previous chapter on the Harness API Client](06_harness_api_client_.md), we saw how `mcp-server` communicates with the Harness API to send requests and receive responses. But when the Harness API sends back data, like the details of a pull request, it's typically in a format called JSON. How does our Go-based `mcp-server` make sense of this JSON and use it easily? And when `mcp-server` wants to send data to Harness, how does it ensure the data is in the exact format Harness expects? This is where **Data Transfer Objects (DTOs)** come into play.

## What's the Big Idea? Standardized Shipping Forms for Data

Imagine you're ordering something online. The online store needs specific information from you: your name, shipping address (street, city, zip code), and what items you want. You fill out a form with clearly labeled fields. This form is a standardized way to transfer your order information to the store.

**Data Transfer Objects (DTOs)** in `mcp-server` are like these standardized forms, but for data. They are Go structures (`structs`) that precisely define the format of data being sent to or received from the Harness API.

For example, when `mcp-server` asks Harness for details about a pull request, Harness sends back a JSON object. There's a `PullRequest` DTO in `mcp-server` that exactly matches the structure of this JSON object. This ensures that `mcp-server` and the Harness API are "speaking the same data language."

Think of DTOs as:
*   **Standardized shipping forms:** When sending data (a package) to Harness, you fill out a specific DTO (form) so Harness knows exactly what's inside and how it's organized.
*   **Blueprints for data:** When receiving data from Harness, a DTO acts as a blueprint, telling `mcp-server` how the data is structured and what to expect.

**Use Case: Getting Pull Request Details**

Let's say the `get_pull_request` [Tool](03_tools_and_toolsets_.md) wants to fetch details for pull request number 5.
1.  The [Harness API Client](06_harness_api_client_.md) makes a request to the Harness API.
2.  Harness API responds with JSON data representing the pull request, including its title, author, state, creation date, etc.
3.  How does the `mcp-server` take this chunk of JSON text and turn it into something its Go code can easily use, like accessing `pullRequest.Title` or `pullRequest.Author.DisplayName`?

DTOs solve this by providing a clear, structured Go representation of that JSON data.

## Key Concepts: DTOs Unpacked

### 1. What are DTOs?
DTOs are Go `struct` types. A `struct` in Go is a way to group together different pieces of data (called fields) under a single name.
*   Each field in a DTO struct corresponds to a piece of data in the JSON (e.g., a `Title` field in the DTO for the "title" in the JSON).
*   They live in the `client/dto/` directory in `mcp-server` (e.g., `client/dto/pullrequest.go`, `client/dto/pipeline.go`).

### 2. Why use DTOs?
*   **Clarity and Structure:** They make it very clear what data is being exchanged. You can look at a DTO definition and know exactly what fields to expect.
*   **Type Safety:** Go is a statically-typed language. DTOs ensure that when you access a field, like `pullRequest.Number`, you know it's an integer, not text. This helps catch errors early.
*   **Easy JSON Conversion:** Go has built-in support for converting JSON to Go structs (and vice-versa) if the structs are defined correctly with special "tags". DTOs are designed for this.
*   **Consistency:** Ensures that both the `mcp-server` and the Harness API agree on the "shape" of the data.

### 3. `json` Tags: The Magic Link
You'll see things like `json:"title"` next to fields in a DTO struct. These are called "tags". They tell Go's JSON library:
*   "When you see a JSON key named `title`, put its value into this Go struct field."
*   "When you're turning this Go struct into JSON, use `title` as the JSON key for this field."
The `omitempty` part (e.g., `json:"description,omitempty"`) means that if the Go field has its default empty value (like an empty string or zero), it shouldn't be included in the JSON when sending data.

## Solving Our Use Case: DTOs for Pull Request Details

Let's see how DTOs help when the `get_pull_request` tool fetches details for PR #5.

1.  **Harness API Sends JSON:**
    The Harness API might send back JSON looking something like this (simplified):
    ```json
    {
        "number": 5,
        "title": "Add new feature",
        "state": "OPEN",
        "author": {
            "display_name": "Jane Doe",
            "email": "jane@example.com"
        },
        "created": 1678886400
    }
    ```

2.  **The `PullRequest` DTO in `mcp-server`:**
    In `client/dto/pullrequest.go`, there's a Go struct that mirrors this structure:
    ```go
    // Simplified from client/dto/pullrequest.go
    package dto

    // PullRequest represents a pull request in the system
    type PullRequest struct {
        Number            int               `json:"number,omitempty"`
        Title             string            `json:"title,omitempty"`
        State             string            `json:"state,omitempty"`
        Author            PullRequestAuthor `json:"author,omitempty"` // Another DTO!
        Created           int64             `json:"created,omitempty"`
        // ... many other fields ...
    }

    // PullRequestAuthor represents a user in the pull request system
    type PullRequestAuthor struct {
        DisplayName string `json:"display_name,omitempty"`
        Email       string `json:"email,omitempty"`
        // ... other fields ...
    }
    ```
    *   Notice how `PullRequest` has fields like `Number`, `Title`, and `State`.
    *   The `json:"..."` tags match the keys in the JSON (`"number"`, `"title"`).
    *   The `Author` field is itself another DTO, `PullRequestAuthor`, because the author information is a nested JSON object.

3.  **[Harness API Client](06_harness_api_client_.md) Uses the DTO:**
    As we saw in Chapter 6, the [Harness API Client](06_harness_api_client_.md)'s `unmarshalResponse` function takes the JSON data and the DTO type:
    ```go
    // Conceptual: inside the API client when it gets a PR
    var prData dto.PullRequest // Create an empty PullRequest DTO
    // jsonData is the raw JSON bytes from Harness API
    // json.Unmarshal will fill prData based on jsonData and the json tags
    err := json.Unmarshal(jsonData, &prData)
    if err != nil {
        // Handle error
    }
    // Now, prData is a Go struct filled with data from the JSON!
    ```

4.  **Tool Uses the Populated DTO:**
    The `get_pull_request` tool receives this `prData` (a populated `dto.PullRequest` struct) from the API Client. Now it can access the information in a type-safe Go way:
    ```go
    // Inside the get_pull_request tool's handler
    // prData is the dto.PullRequest struct returned by the API client
    fmt.Printf("PR Number: %d\n", prData.Number)       // Accesses the integer PR number
    fmt.Printf("PR Title: %s\n", prData.Title)         // Accesses the string title
    fmt.Printf("Author Name: %s\n", prData.Author.DisplayName) // Accesses nested data
    ```
    No more dealing with raw JSON strings! The DTO has made the data structured and easy to use.

## Under the Hood: How DTOs Work with JSON

The process of turning JSON into Go structs (called "unmarshaling") or Go structs into JSON (called "marshaling") is handled by Go's standard `encoding/json` package. DTOs are designed to work seamlessly with this package.

### Step-by-Step: JSON to DTO (Unmarshaling)

1.  **Receive JSON:** The [Harness API Client](06_harness_api_client_.md) receives JSON data as a stream of bytes from the Harness API.
2.  **Prepare DTO Instance:** The client creates an empty instance of the corresponding DTO struct (e.g., `var pr dto.PullRequest`).
3.  **Call `json.Unmarshal`:** The client calls `json.Unmarshal(jsonDataBytes, &pr)`.
4.  **Go's JSON Magic:** The `json.Unmarshal` function:
    *   Reads the JSON data.
    *   Looks at the fields of the `dto.PullRequest` struct.
    *   For each field, it checks its `json:"..."` tag to find the matching JSON key.
    *   It takes the value from the JSON for that key and puts it into the Go struct field, converting the type if necessary (e.g., JSON number to Go `int`).
    *   If there are nested DTOs (like `PullRequestAuthor`), it does this process recursively.
5.  **Populated DTO:** If successful, the `pr` variable now holds all the data from the JSON, neatly organized.

### Sequence Diagram: JSON to DTO

```mermaid
sequenceDiagram
    participant HarnessAPI as Harness API
    participant APIClient as Harness API Client
    participant GoJSONLib as Go encoding/json lib
    participant PR_DTO as dto.PullRequest Struct Instance
    participant Tool as mcp-server Tool

    HarnessAPI->>APIClient: Sends Pull Request JSON (e.g., {"title": "Fix bug", "number": 101})
    APIClient->>GoJSONLib: json.Unmarshal(jsonBytes, &empty_pr_dto_instance)
    Note over GoJSONLib: Reads "title" from JSON, matches to PR_DTO.Title via json tag.
    GoJSONLib-->>PR_DTO: Populates PR_DTO.Title = "Fix bug"
    Note over GoJSONLib: Reads "number" from JSON, matches to PR_DTO.Number.
    GoJSONLib-->>PR_DTO: Populates PR_DTO.Number = 101
    GoJSONLib-->>APIClient: Returns (nil error if successful)
    APIClient-->>Tool: Provides populated PR_DTO instance
end
```

### DTOs for Sending Data (Marshaling)

DTOs are also used when `mcp-server` needs to *send* structured data to the Harness API, for example, when creating a new pull request.

1.  **Tool Prepares DTO:** The `create_pull_request` tool would populate a DTO, like `dto.CreatePullRequest`, with the necessary information (title, source branch, target branch).
    ```go
    // Simplified from client/dto/pullrequest.go
    // CreatePullRequest represents the request body for creating a new pull request
    type CreatePullRequest struct {
        Title        string `json:"title"` // Note: no omitempty, title is usually required
        Description  string `json:"description,omitempty"`
        SourceBranch string `json:"source_branch"`
        TargetBranch string `json:"target_branch,omitempty"`
        IsDraft      bool   `json:"is_draft,omitempty"`
    }

    // In the create_pull_request tool:
    newPRInfo := dto.CreatePullRequest{
        Title:        "My New Feature",
        SourceBranch: "feature/new-thing",
        TargetBranch: "main",
    }
    ```

2.  **API Client Converts DTO to JSON:** The [Harness API Client](06_harness_api_client_.md) would then use `json.Marshal(newPRInfo)` to convert this Go struct into a JSON byte stream.
    ```go
    // Conceptual: inside the API client before sending a create PR request
    // jsonDataBytes will be something like:
    // {"title":"My New Feature","source_branch":"feature/new-thing","target_branch":"main"}
    jsonDataBytes, err := json.Marshal(newPRInfo)
    // ... then send jsonDataBytes in the HTTP request body
    ```

3.  **Send JSON to Harness:** The API client sends this JSON data in the body of an HTTP POST request to the Harness API.

This ensures the data sent to Harness is always in the correct format that the API expects.

### Where to Find DTOs

All DTOs used for communicating with the Harness API are located in the `client/dto/` directory. You'll find files like:
*   `client/dto/pipeline.go`: For pipelines, executions, etc.
    ```go
    // Snippet from client/dto/pipeline.go
    package dto

    // PipelineListItem represents an item in the pipeline list
    type PipelineListItem struct {
        Name                 string                 `json:"name,omitempty"`
        Identifier           string                 `json:"identifier,omitempty"`
        Description          string                 `json:"description,omitempty"`
        // ... many other fields ...
        ExecutionSummaryInfo ExecutionSummaryInfo   `json:"executionSummaryInfo,omitempty"`
    }
    ```
    This `PipelineListItem` DTO is used when the `list_pipelines` tool gets a list of pipelines. Each item in the list will be parsed into this struct.

*   `client/dto/pullrequest.go`: For pull requests, their authors, checks, etc. (as seen above).
*   `client/dto/repositories.go`: For repository information.
*   `client/dto/error.go`: For a standard error response format from the API.
    ```go
    // Snippet from client/dto/error.go
    package dto

    // ErrorResponse represents the standard error response format
    type ErrorResponse struct {
        Code    string `json:"code,omitempty"`
        Message string `json:"message,omitempty"`
    }
    ```
    If the Harness API returns an error in a structured JSON format, this DTO can be used to parse it.

*   `client/dto/scope.go`: Not strictly for API data transfer, but a DTO used internally to pass [Scope](04_scope_management__account__org__project_.md) information.

By examining these files, you can understand the "shape" of the data that `mcp-server` expects from or sends to Harness for various entities.

## Conclusion

Data Transfer Objects (DTOs) are the unsung heroes that make communication between `mcp-server` and the Harness API smooth, reliable, and type-safe. They act as precise blueprints or standardized forms for data, ensuring that both systems understand the structure of the information being exchanged.

Whenever the [Harness API Client](06_harness_api_client_.md) fetches data, DTOs help parse the incoming JSON into usable Go structs. When it sends data, DTOs help construct the JSON payload in the exact format Harness expects. This structured approach is fundamental to the robustness of `mcp-server`.

This chapter concludes our journey through the core concepts of the `mcp-server`! We've covered:
*   The [MCP Server Core](01_mcp_server_core_.md) and how it processes requests.
*   [Configuration Management](02_configuration_management_.md) for setting up the server.
*   [Tools and Toolsets](03_tools_and_toolsets_.md) that define the server's capabilities.
*   [Scope Management](04_scope_management__account__org__project_.md) for targeting the right Harness resources.
*   [Tool Parameter Handling](05_tool_parameter_handling_.md) for providing specific instructions to tools.
*   The [Harness API Client](06_harness_api_client_.md) that communicates with Harness.
*   And finally, DTOs, which structure the data for those communications.

With this knowledge, you're well-equipped to understand the architecture and inner workings of the `mcp-server` project. Happy exploring!