# Chapter 2: Configuration Management

In [Chapter 1: MCP Server Core](01_mcp_server_core_.md), we learned that the `mcp-server` acts like a central switchboard, taking requests and routing them to the correct "Tool." But before this switchboard operator can do their job effectively, they need some initial instructions and settings. How does the server know which Harness account to connect to? What features should it enable? This is where Configuration Management comes in.

## What's the Big Idea? The Server's Settings Panel

Imagine you've just installed a new app on your phone. Before you start using it, you might go to its settings panel. Here, you'd enter your account details, set notification preferences, grant permissions, and so on. These settings customize the app to work just the way you need it to.

**Configuration Management** in `mcp-server` is exactly like that settings panel. It's the system that handles how the server is set up and customized when it starts. It needs to know things like:

*   Your Harness API key (to talk to Harness on your behalf).
*   Default Harness Organization and Project IDs (so you don't have to specify them every time).
*   Logging preferences (how detailed should its internal notes be, and where should it write them?).
*   Which "Toolsets" (groups of features) should be active.

Without these settings, the `mcp-server` wouldn't know how to connect to your Harness account or what tasks it's allowed to perform.

**Use Case: Connecting to Your Harness Account**

Let's say you want `mcp-server` to list all the pipelines in your specific Harness project. For this to happen:
1.  The server needs your **Harness API key** to authenticate with Harness.
2.  It needs to know your **Harness Account ID**.
3.  It probably needs a default **Organization ID** and **Project ID** to know where to look for those pipelines.

Configuration Management is how you provide this vital information to the `mcp-server` *before* it starts processing any requests.

## Key Ways to Configure `mcp-server`

There are two main ways you tell `mcp-server` its settings:

1.  **Environment Variables:** These are like little sticky notes you can set in your computer's environment. The server can read these notes when it starts up. For `mcp-server`, these usually start with `HARNESS_`.
    *   Example: `HARNESS_API_KEY="your_secret_api_key"`
2.  **Command-Line Arguments (Flags):** When you start the server from your terminal, you can add extra instructions directly in the command. These are often called "flags" and usually start with `--`.
    *   Example: `./harness-mcp-server stdio --api-key="your_secret_api_key"`

The `mcp-server` is designed to pick up settings from both these sources. Generally, command-line arguments will take precedence if a setting is provided in both places.

## Essential Settings You'll Encounter

Here are some of the common settings `mcp-server` uses:

*   `HARNESS_API_KEY` (or `--api-key`): Your Harness API key. This is crucial for the server to authenticate with Harness. The server can also cleverly extract your Account ID from this key!
*   `HARNESS_DEFAULT_ORG_ID` (or `--default-org-id`): The default Harness Organization ID you want the server to use if an organization isn't specified in a request.
*   `HARNESS_DEFAULT_PROJECT_ID` (or `--default-project-id`): The default Harness Project ID. Similar to the organization ID, this is used as a fallback.
*   `HARNESS_TOOLSETS` (or `--toolsets`): A comma-separated list of which groups of tools to enable (e.g., "Pipelines,Repositories"). By default, it enables "all". This helps you control what the server can do.
*   `HARNESS_LOG_LEVEL` (or implicitly via `--debug`): Controls how much detail the server logs about its operations. Useful for troubleshooting.
*   `HARNESS_BASE_URL` (or `--base-url`): The web address of the Harness platform. Usually, you don't need to change this unless you're using a self-managed Harness instance.

You can find a more comprehensive list in the project's `README.md` file.

## How `mcp-server` Gets Its Settings: Solving the Use Case

Let's revisit our use case: making the server aware of your Harness account details so it can list pipelines.

You could start the server using **environment variables**:

```bash
# Set these in your terminal before running the server
export HARNESS_API_KEY="pat.your_account_id.xxxxxxxxxxxxxxxxxxxx"
export HARNESS_DEFAULT_ORG_ID="your_org_identifier"
export HARNESS_DEFAULT_PROJECT_ID="your_project_identifier"

# Now run the server
./cmd/harness-mcp-server/harness-mcp-server stdio
```
When `mcp-server` starts, it will automatically read these `HARNESS_...` variables from the environment.

Alternatively, you could use **command-line arguments**:

```bash
./cmd/harness-mcp-server/harness-mcp-server stdio \
  --api-key="pat.your_account_id.xxxxxxxxxxxxxxxxxxxx" \
  --default-org-id="your_org_identifier" \
  --default-project-id="your_project_identifier"
```
In this case, the server parses the arguments you provided directly when you started it.

**What happens next?**
Once the server has these settings, it stores them internally. When a request comes in (e.g., "list pipelines"), the server already knows:
*   Which API key to use (thanks to `HARNESS_API_KEY`).
*   Which Harness account it's dealing with (extracted from the API key).
*   Which organization and project to look in by default (thanks to `HARNESS_DEFAULT_ORG_ID` and `HARNESS_DEFAULT_PROJECT_ID`).

This allows the [MCP Server Core](01_mcp_server_core_.md) to correctly prepare and dispatch the request to the appropriate [Tool](03_tools_and_toolsets_.md), which will then use the [Harness API Client](06_harness_api_client_.md) armed with these configurations.

## Under the Hood: How Settings Are Loaded

When `mcp-server` starts, it goes through a process to gather all its configuration. It uses a popular Go library called "Viper" to help with this.

**Step-by-Step Configuration Loading:**

1.  **Server Starts:** You run the `./harness-mcp-server stdio` command, possibly with flags or after setting environment variables.
2.  **Define Expected Settings:** The code defines what command-line flags it expects (e.g., `--api-key`, `--toolsets`).
3.  **Read Environment Variables:** The server (using Viper) automatically looks for environment variables that match a certain pattern (e.g., prefixed with `HARNESS_`).
4.  **Read Command-Line Flags:** The server (using Cobra and Viper) parses any flags you provided in the command.
5.  **Prioritize and Store:** Viper intelligently combines these sources. Command-line flags usually override environment variables, which in turn override any built-in default values.
6.  **Populate Config Object:** The collected settings are then used to fill a special data structure (a `struct` in Go) that holds all the configuration values.
7.  **Ready for Use:** Other parts of the `mcp-server`, like the [Harness API Client](06_harness_api_client_.md) or the [Tools and Toolsets](03_tools_and_toolsets_.md) system, can now access these settings from the config object.

Here's a simplified diagram of this flow:

```mermaid
sequenceDiagram
    participant User as User/Terminal
    participant ServerProcess as MCP Server Process
    participant ViperLib as Viper (Config Library)
    participant ConfigStruct as Internal Config Object
    participant APIClient as Harness API Client

    User->>ServerProcess: Starts server (e.g., ./harness-mcp-server stdio --api-key=XYZ)
    ServerProcess->>ViperLib: Initialize & configure (flags, env vars)
    ViperLib-->>ViperLib: Reads HARNESS_API_KEY from env
    ViperLib-->>ViperLib: Reads --api-key flag from command line
    ViperLib-->>ViperLib: Prioritizes flag over env var
    ViperLib->>ConfigStruct: Populates APIKey field with "XYZ"
    ServerProcess->>APIClient: Needs to make a call
    APIClient->>ConfigStruct: Reads APIKey ("XYZ")
    APIClient-->>ServerProcess: Uses APIKey for its operations
end
```

### Diving into the Code (Simplified)

Let's look at `cmd/harness-mcp-server/main.go`. This is where much of the configuration setup happens.

**1. Defining Flags and Linking to Viper:**
The `init()` function in `main.go` is where command-line flags are defined.

```go
// From cmd/harness-mcp-server/main.go (simplified)
func init() {
	// ...
	// Define a persistent flag (available to the command and its subcommands)
	rootCmd.PersistentFlags().String("api-key", "", "API key for authentication")
	rootCmd.PersistentFlags().String("default-org-id", "", "Default org ID")
	// ... other flags ...

	// Tell Viper to also look for a flag named "api_key"
	_ = viper.BindPFlag("api_key", rootCmd.PersistentFlags().Lookup("api-key"))
	_ = viper.BindPFlag("default_org_id", rootCmd.PersistentFlags().Lookup("default-org-id"))
	// ... binding other flags ...
}
```
This code uses the `cobra` library to define flags like `--api-key`. Then, `viper.BindPFlag` tells Viper: "Hey, if you see a command-line flag named `api-key`, its value should be stored under the name `api_key` in your configuration settings."

**2. Setting up Environment Variable Reading:**
The `initConfig()` function tells Viper to look for environment variables.

```go
// From cmd/harness-mcp-server/main.go (simplified)
func initConfig() {
	viper.SetEnvPrefix("harness") // Look for env vars starting with HARNESS_
	viper.AutomaticEnv()        // Automatically read matching env variables
}
```
`viper.SetEnvPrefix("harness")` means Viper will look for variables like `HARNESS_API_KEY`, `HARNESS_DEFAULT_ORG_ID`, etc. `viper.AutomaticEnv()` tells it to go ahead and read them if they exist.

**3. Using the Configuration:**
When the `stdioCmd` is run, it retrieves the settings from Viper and populates a `Config` struct.

```go
// From cmd/harness-mcp-server/main.go (simplified)
// Inside stdioCmd's RunE function:
RunE: func(_ *cobra.Command, _ []string) error {
    apiKey := viper.GetString("api_key") // Get "api_key" value from Viper
    if apiKey == "" {
        return fmt.Errorf("API key not provided")
    }
    // ... extract accountID from apiKey ...

    cfg := config.Config{ // This is our custom config struct
        BaseURL:          viper.GetString("base_url"),
        AccountID:        accountID,
        DefaultOrgID:     viper.GetString("default_org_id"),
        DefaultProjectID: viper.GetString("default_project_id"),
        APIKey:           apiKey,
        // ... other settings ...
    }

    // The 'cfg' object is now passed to functions that start the server
    if err := runStdioServer(cfg); err != nil {
        // ... handle error ...
    }
    return nil
}
```
Here, `viper.GetString("api_key")` fetches the API key. Viper has already figured out whether this value came from a flag, an environment variable, or a default. This value, along with others, is then used to create an instance of `config.Config`.

**4. The `Config` Struct:**
This `config.Config` struct is defined in `cmd/harness-mcp-server/config/config.go`. It's simply a container to hold all the configuration values in an organized way.

```go
// From cmd/harness-mcp-server/config/config.go (simplified)
package config

type Config struct {
	Version          string
	BaseURL          string
	AccountID        string
	DefaultOrgID     string
	DefaultProjectID string
	APIKey           string
	ReadOnly         bool
	Toolsets         []string // A list of toolset names
	LogFilePath      string
	Debug            bool
}
```
This struct acts as that "settings panel" we talked about, but in code form. Once populated, it's passed around within the `mcp-server` so different parts can access the settings they need. For instance, the code that initializes [Tools and Toolsets](03_tools_and_toolsets_.md) will receive this `Config` object.

## Conclusion

Configuration Management is the backbone of `mcp-server`'s adaptability. It allows you to tailor the server's behavior to your specific Harness environment and needs, primarily through environment variables and command-line arguments. By providing settings like your API key and default project IDs, you empower the server to act as your efficient assistant for interacting with Harness.

Now that we understand how the server gets its initial setup instructions, we're ready to explore what it can actually *do*. In the next chapter, we'll dive into the specific functionalities the server offers through [Tools and Toolsets](03_tools_and_toolsets_.md).