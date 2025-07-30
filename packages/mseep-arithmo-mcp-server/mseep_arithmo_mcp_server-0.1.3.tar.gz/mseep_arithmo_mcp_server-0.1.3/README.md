[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/varunidealabs-simple-calculator-mcp-server-badge.png)](https://mseep.ai/app/varunidealabs-simple-calculator-mcp-server)

# Create a Custom Server

> Get started building your own server to use in Claude for Desktop and other clients.

In this tutorial, we'll build a simple MCP calculator server and connect it to a host, Claude for Desktop.

## What is MCP?

**MCP** stands for **Model Context Protocol** — it’s a protocol that allows developers to extend AI assistants (like Claude) with custom tools and servers.

- Think of it like giving your AI assistant **extra powers**.
- These servers expose tools or functionalities that the assistant can use during a conversation.
- For example: you can build weather servers, calculators, finance assistants, or anything you imagine.

### What We'll Be Building

We'll build a server that exposes four tools: `add`, `subtract`, `multiply`, and `divide`. Then we'll connect the server to an MCP host (in this case, Claude for Desktop):

> **Note**: Servers can connect to any client. We've chosen Claude for Desktop here for demonstration purposes.

<details>
<summary>Why Claude for Desktop and not Claude.ai?</summary>
Because servers are locally run, MCP currently only supports desktop hosts.
</details>

### Core MCP Concepts

MCP servers can provide three main types of capabilities:

1. **Resources**: File-like data that can be read by clients (like API responses or file contents).
2. **Tools**: Functions that can be called by the LLM (with user approval).
3. **Prompts**: Pre-written templates that help users accomplish specific tasks.

This tutorial will primarily focus on tools.

Let's get started with building our calculator server! [You can find the complete code for what we'll be building here.](https://github.com/varunidealabs/simple-calculator-mcp-server.git)

---

### Prerequisite Knowledge

This quickstart assumes you have familiarity with:

- Python
- LLMs like Claude

### System Requirements

- Python 3.10 or higher installed.
- You must use the Python MCP SDK 1.2.0 or higher.

---

### Set Up Your Environment

First, let's install `uv` and set up our Python project and environment:

#### MacOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Make sure to restart your terminal afterwards to ensure that the `uv` command gets picked up.

Now, let's create and set up our project:

#### MacOS/Linux
```bash
# Create a new directory for our project
uv init calculator
cd calculator

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]"

# Create our server file
touch calculator.py
```

#### Windows
```powershell
# Create a new directory for our project
uv init calculator
cd calculator

# Create virtual environment and activate it
uv venv
.venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"

# Create our server file
new-item calculator.py
```

Now let's dive into building your server.

---

## Building Your Server

### Importing Packages and Setting Up the Instance

Add these to the top of your `calculator.py`:

```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("calculator")
```

### Implementing Tool Execution

The tool execution handler is responsible for actually executing the logic of each tool. Let's add it:

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b
```

### Running the Server

Finally, let's initialize and run the server:

```python
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
```

Your server is complete! Run `uv run calculator.py` to confirm that everything's working.

---

## Testing Your Server with Claude for Desktop

> **Note**: Claude for Desktop is not yet available on Linux.

We'll need to configure Claude for Desktop for whichever MCP servers you want to use. To do this, open your Claude for Desktop App configuration at `~/Library/Application Support/Claude/claude_desktop_config.json` in a text editor. Make sure to create the file if it doesn't exist.

#### MacOS/Linux
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Windows
```powershell
code $env:AppData\Claude\claude_desktop_config.json
```

You'll then add your servers in the `mcpServers` key. The MCP UI elements will only show up in Claude for Desktop if at least one server is properly configured.

In this case, we'll add our single calculator server like so:

#### MacOS/Linux
```json
{
    "mcpServers": {
        "calculator": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/calculator",
                "run",
                "calculator.py"
            ]
        }
    }
}
```

#### Windows
```json
{
    "mcpServers": {
        "calculator": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\calculator",
                "run",
                "calculator.py"
            ]
        }
    }
}
```

> **Warning**: You may need to put the full path to the `uv` executable in the `command` field. You can get this by running `which uv` on MacOS/Linux or `where uv` on Windows.

Make sure you pass in the absolute path to your server.

This tells Claude for Desktop:

1. There's an MCP server named "calculator".
2. To launch it by running `uv --directory /ABSOLUTE/PATH/TO/PARENT/FOLDER/calculator run calculator.py`.

Save the file, and restart **Claude for Desktop**.

---

Since this calculator supports basic arithmetic operations, it can be used for addition, subtraction, multiplication, and division.

For more info: [MCP Official Docs](https://modelcontextprotocol.io/introduction)
