# Tutorial: harness-mcp

The `harness-mcp` project provides a **server** that implements the *Model Context Protocol (MCP)*.
This server acts as an intermediary, allowing AI assistants or other MCP-compatible clients to interact with various **Harness platform APIs**.
It achieves this by exposing specific Harness functionalities, such as managing pipelines, pull requests, or repositories, as invokable **tools**.
This enables developers and tools to automate tasks and integrate with Harness features through a standardized communication protocol.


**Source Repository:** [None](None)

```mermaid
flowchart TD
    A0["MCP Server Core
"]
    A1["Harness API Client
"]
    A2["Tools & Toolsets
"]
    A3["Server Configuration
"]
    A4["Data Transfer Objects (DTOs)
"]
    A5["Scope Handling
"]
    A6["Command-Line Interface (CLI) & Initialization
"]
    A6 -- "Loads Configuration" --> A3
    A6 -- "Initializes Server" --> A0
    A3 -- "Configures Server" --> A0
    A3 -- "Provides Credentials & Endp..." --> A1
    A0 -- "Registers & Invokes Tools" --> A2
    A2 -- "Uses API Client" --> A1
    A2 -- "Uses Scope for Context" --> A5
    A1 -- "Uses DTOs for Data Exchange" --> A4
    A1 -- "Applies Scope to API Calls" --> A5
```

## Chapters

1. [Tools & Toolsets
](01_tools___toolsets_.md)
2. [MCP Server Core
](02_mcp_server_core_.md)
3. [Command-Line Interface (CLI) & Initialization
](03_command_line_interface__cli____initialization_.md)
4. [Server Configuration
](04_server_configuration_.md)
5. [Harness API Client
](05_harness_api_client_.md)
6. [Scope Handling
](06_scope_handling_.md)
7. [Data Transfer Objects (DTOs)
](07_data_transfer_objects__dtos__.md)