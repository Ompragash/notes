# Harness MCP Server Specification

## Overview

The Harness MCP (Model Context Protocol) Server provides AI-assisted context about Harness CI/CD pipelines, executions, and artifacts. It enables seamless integration with AI assistants and other MCP-compatible clients to deliver information about pipeline executions, failures, artifacts, and other CI/CD related data.

## Architecture

### Server Components

1. **Core MCP Server**
   - Handles MCP protocol communication
   - Manages tool registration and invocation
   - Routes requests to appropriate handlers

2. **Harness API Clients**
   - Authentication management with API keys or bearer tokens
   - Connector, pipeline, and execution API interactions
   - Rate limiting and error handling

3. **Context Mapping Services**
   - Maps Git repositories to Harness connectors
   - Associates connectors with pipelines and executions
   - Provides hierarchy awareness (account/org/project scopes)

4. **Tool Implementations**
   - Execution artifact retrieval
   - Execution failure log retrieval
   - Connector listing and management
   - Pipeline information retrieval

## Key Features

### Git Context to Pipeline Mapping

The server can intelligently map local Git repositories to Harness pipelines by:

1. Extracting Git context (remote URL, branch)
2. Finding associated Harness connectors across all scopes
3. Discovering pipelines that use these connectors
4. Retrieving execution history for relevant pipelines

### Multi-Scope Connector Discovery

Harness connectors can exist at different scopes:
- Account level
- Organization level
- Project level

The MCP server implements strategies to efficiently discover and use connectors across all scopes, with hierarchical fallbacks when needed.

### SCM Connector Type Support

The server supports all major Harness SCM connector types:
- Github
- Gitlab
- Bitbucket
- Git (generic)
- AzureRepo
- Codecommit

### Execution Data Retrieval

Provides capabilities to fetch:
- Build failure logs with step-level detail
- Pipeline execution artifacts
- Execution status and metadata
- Pipeline configuration details

## Components Specification

### ConnectorCache

Provides efficient mapping between Git repositories and Harness connectors.

```typescript
class ConnectorCache {
  // Multiple indexes for different match patterns
  private exactUrlMap: Map<string, ConnectorInfo[]>;
  private orgUrlMap: Map<string, ConnectorInfo[]>;
  private repoNameMap: Map<string, ConnectorInfo[]>;
  
  // Initialize and populate cache
  async initialize(): Promise<void>;
  
  // Refresh connector cache
  async refreshCache(): Promise<void>;
  
  // Get all SCM connectors across all scopes
  async getAllSCMConnectors(): Promise<ConnectorInfo[]>;
  
  // Index connectors by various patterns
  async indexConnectors(connectors: ConnectorInfo[]): Promise<void>;
  
  // Find connectors for a Git URL with progressive pattern matching
  async findConnectorsForGitUrl(gitUrl: string): Promise<ConnectorInfo[]>;
  
  // Extract Git URLs from connector based on type
  extractGitUrlsFromConnector(connector: ConnectorInfo): string[];
}
```

### GitUrlMatcher

Handles normalization and pattern generation for Git URLs to enable flexible matching.

```typescript
class GitUrlMatcher {
  // Normalize Git URLs for comparison
  static normalizeGitUrl(url: string): string;
  
  // Generate multiple matching patterns for a Git URL
  static generatePatterns(gitUrl: string): string[];
  
  // Check if two Git URLs might refer to the same repository
  static isLikelyMatch(url1: string, url2: string): boolean;
}
```

### PipelineService

Maps connectors to pipelines and manages execution history.

```typescript
class PipelineService {
  // Find pipelines associated with a Git repository
  async findPipelinesForGitRepo(
    gitUrl: string, 
    branch?: string
  ): Promise<PipelineInfo[]>;
  
  // Find pipelines that use a specific connector
  async findPipelinesUsingConnector(
    connector: ConnectorInfo, 
    gitUrl: string, 
    branch?: string
  ): Promise<PipelineInfo[]>;
  
  // Get recent executions for a set of pipelines
  async getRecentExecutions(
    pipelines: PipelineInfo[], 
    limit?: number
  ): Promise<ExecutionInfo[]>;
  
  // Find the latest failed execution
  async findLatestFailedExecution(
    gitUrl: string, 
    branch: string
  ): Promise<ExecutionInfo | null>;
}
```

### HarnessAPIClients

Set of clients for different Harness API endpoints.

```typescript
// Connector API client
class ConnectorClient {
  // List connectors with scope filtering
  async listConnectors(params: {
    types?: string[],
    includeScopes?: ScopeOption[]
  }): Promise<ConnectorResponse>;
}

// Pipeline API client
class PipelineClient {
  // Get pipelines by connector ID
  async getPipelinesByConnector(
    connectorId: string, 
    scope: ConnectorScope
  ): Promise<PipelineInfo[]>;
  
  // Get pipeline executions
  async getPipelineExecutions(
    pipelineId: string, 
    scope: ConnectorScope, 
    limit?: number
  ): Promise<ExecutionInfo[]>;
}

// Execution API client
class ExecutionClient {
  // Get execution details
  async getExecutionDetails(
    executionId: string, 
    scope: ConnectorScope
  ): Promise<ExecutionDetail>;
  
  // Get execution failure logs
  async getExecutionFailureLogs(
    executionId: string, 
    scope: ConnectorScope
  ): Promise<LogEntries[]>;
  
  // Get execution artifacts
  async getExecutionArtifacts(
    executionId: string, 
    scope: ConnectorScope
  ): Promise<ArtifactInfo[]>;
}
```

## Harness Context Hierarchy

The server understands and navigates the Harness hierarchical structure:

```
Account
  ├── Organization 1
  │     ├── Project A
  │     │     ├── Pipeline X (with connector references)
  │     │     └── Pipeline Y
  │     └── Project B
  └── Organization 2
        └── Project C
```

Connectors and pipelines can exist at any level in this hierarchy. The server implements strategies to:

1. Search efficiently across all levels
2. Prioritize most specific matches (project level) over general ones (account level)
3. Handle scope-specific configuration and permissions
4. Provide appropriate context in responses

## MCP Tool Specifications

### 1. get_harness_execution_artifacts

Retrieves artifacts produced by a specific pipeline execution.

**Input Parameters:**
- `executionUrl`: URL to a Harness pipeline execution (optional)
- `workspaceRoot`: Local Git repository path (optional)
- `gitRemoteURL`: Git remote URL (optional)
- `branch`: Git branch (optional)

Either `executionUrl` OR the set of (`workspaceRoot`, `gitRemoteURL`, `branch`) must be provided.

**Output:**
- List of artifacts with name, type, and download URL
- Organized by pipeline stage and step

### 2. get_harness_execution_failure_logs

Retrieves failure logs from a pipeline execution, with focus on failed steps.

**Input Parameters:**
- `executionUrl`: URL to a Harness pipeline execution (optional)
- `workspaceRoot`: Local Git repository path (optional)
- `gitRemoteURL`: Git remote URL (optional)
- `branch`: Git branch (optional)

Either `executionUrl` OR the set of (`workspaceRoot`, `gitRemoteURL`, `branch`) must be provided.

**Output:**
- Formatted logs from failed steps
- Contextual information about the failure
- Summary of execution status

### 3. list_harness_connectors

Lists Harness connectors with advanced scope filtering.

**Input Parameters:**
- `connectorType`: Type of connector to filter by (optional)
- `connectorNames`: List of connector names to filter by (optional)
- `connectorIds`: List of connector IDs to filter by (optional)
- `categories`: List of connector categories to filter by (optional)
- `includeScopes`: Which scopes to include (account, organization, project) (optional)

**Output:**
- List of connectors matching criteria
- Details including name, ID, type, scope, and description

## Implementation Strategy

### Phase 1: Core Framework
- Implement base MCP server
- Establish Harness API clients with auth management
- Build connector discovery and caching

### Phase 2: Context Mapping
- Implement Git URL to connector mapping
- Create pipeline discovery from connectors
- Develop execution history retrieval

### Phase 3: Tool Implementation
- Enhance execution artifact tool with Git context
- Update failure logs tool with Git context
- Add connector management tools

### Phase 4: Optimization and Robustness
- Implement caching strategies
- Add smart retries and fallbacks
- Optimize performance for large installations

## Configuration

The server supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `HARNESS_API_KEY` | Harness API key for authentication | - |
| `HARNESS_BEARER_TOKEN` | Bearer token for authentication (alternative to API key) | - |
| `HARNESS_ACCOUNT_ID` | Default Harness account ID | - |
| `HARNESS_ORG_ID` | Default Harness organization ID | - |
| `HARNESS_PROJECT_ID` | Default Harness project ID | - |
| `HARNESS_BASE_URL` | Base URL for Harness API | https://app.harness.io |

## Security Considerations

1. **Authentication**
   - Support for both API key and bearer token authentication
   - No hardcoded credentials in configuration
   - Token permissions determine visible resources

2. **Scope Boundaries**
   - Respects permission boundaries of provided token
   - Does not expose resources outside authorized scopes
   - Provides clear error messages for unauthorized access

3. **Data Handling**
   - Avoids caching sensitive information
   - Only retrieves necessary data
   - Implements secure connection handling

## Performance Considerations

1. **Caching Strategy**
   - Cache connectors with 15-minute refresh period
   - Store mappings in-memory with fallback persistence
   - Implement LRU cache for recent queries

2. **Batch Processing**
   - Group related API calls when possible
   - Implement parallel requests for independent data
   - Rate limit to avoid API throttling

3. **Progressive Matching**
   - Try exact matches before fuzzy matches
   - Prioritize lower-cost API calls
   - Implement timeouts for expensive operations

## MCP Server Integration

The server implements the Model Context Protocol specification, allowing seamless integration with:

1. **AI Assistants**
   - Claude in VSCode/Windsurf
   - GitHub Copilot
   - Other MCP-compatible assistants

2. **MCP Clients**
   - MCP Inspector for testing
   - Custom MCP client implementations
   - CI/CD system integrations
