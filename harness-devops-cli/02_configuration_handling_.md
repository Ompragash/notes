# Chapter 2: Configuration Handling

In [Chapter 1: CLI Command Framework](01_cli_command_framework_.md), we learned how to tell the `harness-devops-cli` tool what to do using commands like `harness-devops bme github-actions`. But for the tool to actually *do* anything useful, like fetching data from GitHub or Jenkins, it needs some important information:

*   **Credentials:** API keys or tokens to securely access platforms like GitHub or Jenkins.
*   **Parameters:** Settings used in calculations, like how much more efficient Harness might be (`HARNESS_EFFICIENCY_FACTOR`) or how much your build workload might grow (`YEARLY_GROWTH_RATE`).

Imagine installing new software on your computer. Often, the first time you run it, a setup wizard pops up asking for your preferences, maybe a license key, or login details. **Configuration Handling** in our tool is like that setup wizard. It's how we get these necessary details from you *once* and store them securely so you don't have to type them in every single time you run a command.

## What Problem Does Configuration Handling Solve?

The main goals are:

1.  **Convenience:** You only need to provide sensitive information (like API keys) and specific calculation parameters once. The tool remembers them for future use.
2.  **Security:** API keys are like passwords! We need to store them securely and avoid displaying them on the screen when you type them.
3.  **Organization:** Keep all settings in one predictable place.

Without configuration handling, you'd have to type your GitHub token or Jenkins API key every time you wanted to run a forecast, which would be tedious and insecure.

## Key Concepts

*   **Configuration Settings:** These are the pieces of information the tool needs. They fall into two main categories:
    *   **Secrets:** Sensitive data like `GITHUB_TOKEN` or `JENKINS_ACCESS_TOKEN`.
    *   **Parameters:** Non-secret values used for calculations, like `HARNESS_EFFICIENCY_FACTOR` or `COST_PER_MINUTE`.
*   **The `configure` Command:** This is the primary way you interact with the configuration system. Running `harness-devops configure` starts the "setup wizard" process.
*   **The `.env.local` File:** This is a special file created in the same directory where you run the tool. The `configure` command saves all your settings here. Think of it as the tool's private notebook where it keeps the information you gave it. Files starting with a dot (`.`) are often hidden by default in file explorers, adding a slight layer of obscurity. Crucially, you should **never** commit this file to version control (like Git) because it contains secrets! We automatically include `.env.local` in the project's `.gitignore` file to help prevent this.
*   **Loading Settings:** When you run other commands (like `bme github-actions`), the tool automatically looks for the `.env.local` file, reads the settings from it, and uses them to perform its tasks.

## How to Use It: Running the `configure` Command

Let's set up the tool to work with GitHub Actions.

1.  **Open your terminal** in the project directory.
2.  **Run the command:**
    ```bash
    harness-devops configure
    ```
3.  **Follow the prompts:** The tool will ask you which platform you want to configure and then guide you through entering the necessary information.

**Example Interaction:**

```text
$ harness-devops configure
Select platform to configure:
1. Jenkins
2. GitHub Actions
Enter your choice (1 or 2): 2  # You type '2' and press Enter

📝 Configuring GitHub Actions...
Enter GitHub Personal Access Token: ****************************************  # You paste your token; it shows as asterisks

📊 Configuring Common Parameters...
Enter Harness Efficiency Factor (defaults to 0.5):  # You press Enter to accept the default
Enter Yearly Growth Rate (defaults to 1.2): 1.1  # You type '1.1' and press Enter
Enter Cost per Minute (defaults to 0.08): # You press Enter to accept the default

✅ Configuration saved to /path/to/your/project/.env.local
```

**What Happens:**

*   The tool asks which platform you're setting up (Jenkins or GitHub Actions).
*   For GitHub, it asks for your **Personal Access Token (PAT)**. Notice how it hides your input with asterisks (`*`) for security.
*   It then asks for common parameters used in forecasting calculations, showing default values you can accept by just pressing Enter.
*   Finally, it confirms that the settings have been saved to the `.env.local` file.

**Inside `.env.local`:**

After the configuration, the `.env.local` file might look something like this (the actual token will be much longer):

```dotenv
# File: .env.local
# (This file should NOT be committed to Git)

# GitHub Actions Configuration
GITHUB_TOKEN=ghp_YourVeryLongSecretTokenValueHere

# Common Parameters
HARNESS_EFFICIENCY_FACTOR=0.5
YEARLY_GROWTH_RATE=1.1
COST_PER_MINUTE=0.08
CREDITS_FOR_CLOUD=2
```

**Using the Saved Configuration:**

Now, when you run a command that needs these settings, like fetching GitHub data:

```bash
harness-devops bme github-actions --owner my-org --repo my-app
```

The tool will automatically:
1. Look for the `.env.local` file.
2. Load the `GITHUB_TOKEN` from it.
3. Use that token to talk to the GitHub API.
4. Load parameters like `HARNESS_EFFICIENCY_FACTOR` to use in its calculations later.

You don't need to provide the token again!

## Under the Hood: How Configuration Works

Let's trace the steps involved when you run `configure` and then use the settings.

**Step-by-Step Flow (`configure` command):**

1.  **User runs `configure`:** You type `harness-devops configure`.
2.  **CLI Framework executes:** As we saw in [Chapter 1: CLI Command Framework](01_cli_command_framework_.md), Cobra identifies the `configure` command and runs its associated function.
3.  **Prompt User:** The code inside the `configure` command's function prints questions to your terminal (e.g., "Enter GitHub Personal Access Token:").
4.  **Read Input:** It waits for you to type your answer and press Enter. For sensitive fields like tokens, it uses special terminal functions to hide the input (`readSensitiveInput`).
5.  **Open/Create File:** It opens the `.env.local` file. If the file doesn't exist, it creates it.
6.  **Write Settings:** It writes the collected information into the file in the `KEY=VALUE` format.
7.  **Save File:** It closes the file, saving the changes.

**Sequence Diagram (`configure`):**

```mermaid
sequenceDiagram
    participant User
    participant CLI as harness-devops configure
    participant PromptInput as Input Prompter/Reader
    participant EnvFileWriter as .env.local Writer

    User->>CLI: Runs 'configure' command
    CLI->>PromptInput: Ask for Platform Choice
    PromptInput-->>User: Show platform options
    User->>PromptInput: Enters choice (e.g., "2")
    CLI->>PromptInput: Ask for GitHub Token
    PromptInput-->>User: Prompt for token (hides input)
    User->>PromptInput: Enters token
    CLI->>PromptInput: Ask for Parameters (e.g., Growth Rate)
    PromptInput-->>User: Prompt for rate (shows default)
    User->>PromptInput: Enters rate (e.g., "1.1")
    CLI->>EnvFileWriter: Prepare settings (Token, Rate, etc.)
    EnvFileWriter->>EnvFileWriter: Open/Create .env.local
    EnvFileWriter->>EnvFileWriter: Write "GITHUB_TOKEN=..."
    EnvFileWriter->>EnvFileWriter: Write "YEARLY_GROWTH_RATE=1.1"
    EnvFileWriter->>EnvFileWriter: Save and Close file
    CLI-->>User: Print "Configuration saved..."
```

**Step-by-Step Flow (Loading settings in other commands like `bme github-actions`):**

1.  **User runs command:** You type `harness-devops bme github-actions --owner my-org`.
2.  **CLI Framework executes:** Cobra identifies the command and runs its function (e.g., `handleGitHubForecast`).
3.  **Load Environment:** Early in the function, it uses a library (`godotenv`) to load the `.env.local` file. This makes the settings available as environment variables *within the running program*.
4.  **Retrieve Settings:** When the code needs the token or a parameter, it uses standard Go functions (`os.Getenv`) to read the value associated with a key (e.g., `os.Getenv("GITHUB_TOKEN")`).
5.  **Use Settings:** The retrieved values are then used for API calls, calculations, etc.

**Diving into the Code:**

Let's look at simplified snippets.

1.  **Defining the `configure` Command (`cmd/configure.go`)**
    This sets up the `configure` command itself.

    ```go
    // File: cmd/configure.go
    package cmd

    import (
    	"fmt"
    	"os"
    	"github.com/spf13/cobra"
    	// ... other imports
    )

    // configureCmd represents the "configure" command
    var configureCmd = &cobra.Command{
    	Use:   "configure",
    	Short: "Set up credentials and parameters...",
    	// This function runs when 'harness-devops configure' is executed
    	Run: func(cmd *cobra.Command, args []string) {
    		const envFile = ".env.local"
    		fmt.Println("Starting configuration...")

    		// 1. Ask user for platform choice (simplified)
    		fmt.Print("Enter GitHub Personal Access Token: ")
    		token := readSensitiveInput() // Reads input securely

    		// 2. Ask for common parameters (simplified)
    		fmt.Print("Enter Yearly Growth Rate (defaults to 1.2): ")
    		yearlyGrowthRate := readInputWithDefault("1.2")

    		// 3. Open/Create and write to .env.local (simplified)
    		file, err := os.OpenFile(envFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
    		// ... (error handling) ...
    		defer file.Close()

    		fmt.Fprintf(file, "GITHUB_TOKEN=%s\n", token)
    		fmt.Fprintf(file, "YEARLY_GROWTH_RATE=%s\n", yearlyGrowthRate)
    		// ... (write other settings) ...

    		fmt.Println("✅ Configuration saved to", envFile)
    	},
    }

    // This function reads input without showing it on screen
    func readSensitiveInput() string {
    	// ... special terminal handling code ...
        // Returns the string the user typed
    }

    // This function reads input, using a default if nothing is entered
    func readInputWithDefault(defaultValue string) string {
    	// ... reads input, returns default if empty ...
        return defaultValue // Simplified
    }

    // Add configureCmd to the root command
    func init() {
    	rootCmd.AddCommand(configureCmd)
    }
    ```
    This shows the basic structure: define the command with `cobra.Command`, implement the logic in the `Run` function (prompting, reading with helper functions like `readSensitiveInput`, writing to the file), and attach it to the main `rootCmd`.

2.  **Loading Settings in Another Command (`cmd/github_forecast.go`)**
    Here's how a command like `bme github-actions` loads the settings.

    ```go
    // File: cmd/github_forecast.go (simplified snippet)
    package cmd

    import (
    	"fmt"
    	"os"
    	"strconv" // To convert strings to numbers
    	"github.com/joho/godotenv" // Library to load .env files
    	"github.com/spf13/cobra"
    	// ... other imports
    )

    // This function runs when 'harness-devops bme github-actions' is executed
    func handleGitHubForecast(cmd *cobra.Command, args []string) {
    	// 1. Load the .env.local file
    	err := godotenv.Load(".env.local")
    	if err != nil {
    		// Handle error (e.g., file not found, maybe prompt user to run configure)
    		fmt.Println("❌ Error loading .env.local file. Run 'harness-devops configure' first.")
    		os.Exit(1)
    	}

    	// 2. Retrieve settings using os.Getenv
    	token := os.Getenv("GITHUB_TOKEN")
    	if token == "" {
    		fmt.Println("❌ GITHUB_TOKEN not found in configuration.")
    		os.Exit(1)
    	}

    	// Get parameters, converting from string to number as needed
    	yearlyGrowthRateStr := os.Getenv("YEARLY_GROWTH_RATE")
    	yearlyGrowthRate, _ := strconv.ParseFloat(yearlyGrowthRateStr, 64) // Convert string to float

    	fmt.Println("Starting GitHub Actions forecast...")
    	fmt.Printf("Using Growth Rate: %f\n", yearlyGrowthRate)

    	// 3. Use the token and parameters...
    	// fetchGitHubData(token, ...)
    	// calculateProjections(..., yearlyGrowthRate)
    	// (These steps call logic from other parts, like Platform Data Retrieval)
    }

    // ... (rest of the githubCmd definition and init function) ...
    ```
    The key steps are using `godotenv.Load(".env.local")` to load the file and `os.Getenv("KEY_NAME")` to retrieve specific values when needed. The rest of the command's logic then uses these loaded values.

## Connecting to Other Concepts

*   **[CLI Command Framework](01_cli_command_framework_.md):** The `configure` command is defined using the Cobra framework, just like other commands.
*   **[Platform Data Retrieval (Jenkins & GitHub)](03_platform_data_retrieval__jenkins___github__.md):** The API tokens saved via `configure` are essential for this step to authenticate with Jenkins or GitHub.
*   **[Build Data Analysis & Forecasting](04_build_data_analysis___forecasting_.md):** Parameters like `HARNESS_EFFICIENCY_FACTOR` and `YEARLY_GROWTH_RATE` saved via `configure` are used during this analysis phase.

## Conclusion

You've now learned how `harness-devops-cli` handles configuration – storing necessary credentials and parameters safely and conveniently. You know that the `configure` command acts like a setup wizard, prompting you for details and saving them to a hidden `.env.local` file. You also understand that other commands automatically load these settings from the file when they need to interact with external platforms or perform calculations. This setup means you only need to provide sensitive information once, making the tool easier and more secure to use.

With the tool configured, we're ready to start fetching real data!

**Next Up:** Let's see how the tool uses the configured credentials to connect to Jenkins and GitHub and retrieve build history data in [Chapter 3: Platform Data Retrieval (Jenkins & GitHub)](03_platform_data_retrieval__jenkins___github__.md).