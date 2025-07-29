# 🧠 jupyter-server-ai-tools

[![CI](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml)

A Jupyter Server extension for discovering and aggregating callable tools from other extensions.

This project provides a structured way for extensions to declare tools using `Tool` objects, and for agents or other consumers to retrieve those tools.

______________________________________________________________________

## ✨ Features

- ✅ Simple, declarative `Toolkit` API for registering callable tools
- ✅ Toolkit registration with unique names
- ✅ Retrieve toolkits by name and capabilities
- ✅ Clean separation between tool metadata and callable execution
- ✅ Optional tool capability filtering (read, write, execute, delete)

______________________________________________________________________

## 📦 Install

```bash
pip install jupyter_server_ai_tools
```

To install for development:

```bash
git clone https://github.com/Abigayle-Mercer/jupyter-server-ai-tools.git
cd jupyter-server-ai-tools
pip install -e ".[lint,test]"
```

## Usage

#### Expose tools in your own extensions:

```python
from jupyter_server_ai_tools.models import Tool, Toolkit

def greet(name: str):
    """Say hello to someone."""
    return f"Hello, {name}!"

```

##### For configurable extension apps

```python
class MyExtensionApp(ExtensionApp)

    # Get the tookit registry from settings
    @property
    def toolkit_registry(self):
        return self.settings["toolkit_registry"]

    async def _start_jupyter_server_extension(self):
        # Create a tool
        greet_tool = Tool(callable=greet, read=True)
        
        # Create a toolkit
        greeting_toolkit = Toolkit(name="GreetingToolkit")
        greeting_toolkit.add_tool(greet_tool)
        
        # Register the toolkit
        self.toolkit_registry.register_toolkit(greeting_toolkit)

```

##### For basic extensions
```python
async def _start_jupyter_server_extension(serverapp):
    toolkit_registry = serverapp.web_app.settings["toolkit_registry"]
    
    # Create a tool
    greet_tool = Tool(callable=greet, read=True)
    
    # Create a toolkit
    greeting_toolkit = Toolkit(name="GreetingToolkit")
    greeting_toolkit.add_tool(greet_tool)
    
    # Register the toolkit
    self.toolkit_registry.register_toolkit(greeting_toolkit)

```

#### Retrieve Toolkits:

```python
# Get a specific toolkit
greeting_toolkit = registry.get_toolkit("GreetingToolkit")

# Get toolkit with specific tool capabilities
read_toolkits = registry.get_toolkit("GreetingToolkit", read=True)
```

## 🧪 Running Tests

```bash
pip install -e ".[test]"
pytest
```

## 🧼 Linting and Formatting

```bash
pip install -e ".[lint]"
bash .github/workflows/lint.sh
```

## Impact

This system enables:

- Extension authors to register tools with minimal effort
- Flexible tool discovery and retrieval
- Capability-based tool filtering

## 🧹 Uninstall

```bash
pip uninstall jupyter_server_ai_tools
