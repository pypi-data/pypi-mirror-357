# Kubiya SDK

Kubiya SDK is a powerful Python library designed for creating, managing, and executing tools. It offers a flexible and intuitive interface, facilitating the integration of various tools and the efficient management of their execution.

## Table of Contents

- Kubiya SDK
  - Table of Contents
  - Installation
  - Key Concepts
  - Quick Start
    - Creating a Tool
  - Example for basic tool
  - Contributing
  - License

## Installation

To install the Kubiya SDK, use pip:

```bash
pip install kubiya-sdk
```

## Key Concepts

- **Teammates**: AI-powered virtual assistants capable of managing technical operations tasks.
- **Tools**: Reusable functions that can be integrated into workflows and teammate agents.
- **Steps**: Individual units of work within a workflow.
- **State**: The data passed between steps in a workflow.

For setting up an API server for the SDK, you may install with additional server support:

```bash
pip install kubiya-sdk[server]
```

## Quick Start

### Creating a Tool

Here’s a basic example of how to create a new tool.

Use the Kubiya CLI `init` command to generate a foundational template:

```bash
kubiya init
```

This creates a new folder with the following structure for the tool:

```bash
/my-new-amazing-tool
│
├── /tools
│   ├── /function_tool
│   │   ├── main.py       # example for function tool
│   │
│   ├── /hello_world_tool # example for basic tool
│   │   ├── main.py
│   │   └── tool_def
│   └──
│
```

After editing your tools, you need to use the bundle command to scan and package your Kubiya tools within the project:

```bash
kubiya bundle
```

The command scans for tools in the project, verifies for any errors, and generates a `kubiya_bundle.json` file in the
root folder. An example output:

```bash
Python Version: 3.11.10
Tools Discovered: 2
                            Tools Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Tool Name                      ┃ Args ┃ Env Vars ┃ Secrets ┃ Files ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ test_123                       │  3   │    0     │    0    │   1   │
│ say_hello                      │  1   │    0     │    0    │   1   │
└────────────────────────────────┴──────┴──────────┴─────────┴───────┘
No Errors
```

You can now create a new resource via https://kubiya.ai and integrate it with your teammate agent.

## Examples

### Example for basic tool

Simple main.py file for a tool that prints hello {name}!

```python main.py
def hello_world(name: str):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print hello {name}!")
    parser.add_argument("name", help="Name to say hello to")

    # Parse command-line arguments
    args = parser.parse_args()

    # Get coordinates for the given city
    name = args.name

    hello_world(name)
```

```python main.py
import inspect

from kubiya_sdk.tools.models import Arg, Tool, FileSpec
from kubiya_sdk.tools.registry import tool_registry

from . import main

hello_tool = Tool(
    name="say_hello",
    type="docker",
    image="python:3.12",
    description="Prints hello {name}!",
    args=[Arg(name="name", description="name to say hello to", required=True)],
    on_build="""  # Optimizes build by cache to reduce execution time
curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null 2>&1
. $HOME/.cargo/env

uv venv > /dev/null 2>&1
. .venv/bin/activate > /dev/null 2>&1

if [ -f /tmp/requirements.txt ]; then
    uv pip install -r /tmp/requirements.txt > /dev/null 2>&1
fi
""",
    content="""
python /tmp/main.py "{{ .name }}"
""",
    with_files=[
        FileSpec(
            destination="/tmp/main.py",
            content=inspect.getsource(main),
        ),
        # Add any requirements here if needed
        # FileSpec(
        #     destination="/tmp/requirements.txt",
        #     content="",
        # ),
    ],
)
```

## Contributing

We welcome contributions to the Kubiya SDK! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more
information on how to get started.

## License

Kubiya SDK is released under the [MIT License](LICENSE).

