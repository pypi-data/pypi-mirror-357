# MCP Screen Operation Server

A modern Model Context Protocol (MCP) server for cross-platform screen and window operations, built with FastMCP and supporting multiple transport protocols.

## Features

### Screen Operations
- Get information about connected displays
- Capture screenshots of specific monitors
- Capture stitched screenshots of all monitors

### Window Operations
- Get a list of all open windows
- Capture screenshots of specific windows

### Automation Operations
- Mouse movement, clicking, dragging, and scrolling
- Keyboard typing, key presses, and hotkey combinations
- Get current mouse position and screen information

### Transport Protocols
- **STDIO** (default) - For local tools and Claude Desktop integration
- **SSE** (Server-Sent Events) - For web-based deployments
- **Streamable HTTP** (recommended) - Modern HTTP-based protocol

### Platform Support
- **Linux** (X11 via python-xlib)
- **Windows** (Win32 API via pywin32)
- **macOS** (Quartz via PyObjC)

## Architecture

The server uses a clean, platform-agnostic architecture:

- **FastMCP Integration**: Modern MCP server framework with multi-transport support
- **Platform Abstraction**: `WindowManager` interface with platform-specific implementations
- **Dependency Management**: Automatic platform-specific dependency checking
- **Clean Separation**: Operations layer independent of platform details

## Installation

### Quick Install from PyPI

Once published to PyPI, you can install and run easily:

```bash
# Install with uv (recommended)
uvx mcp-screen-operation  # Run directly without installation

# Or install with pip
pip install mcp-screen-operation[windows]  # Replace 'windows' with your platform
```

### Install from Source

#### Prerequisites

Create and activate a virtual environment:

```bash
python -m venv venv

# On Windows
.\venv\Scripts\Activate.ps1

# On Linux/macOS
source venv/bin/activate
```

### Basic Installation

Install the project in editable mode with platform-specific dependencies:

#### For Production Use

```bash
# Linux
pip install -e ".[linux]"

# Windows
pip install -e ".[windows]"

# macOS
pip install -e ".[macos]"
```

#### For Development

Install with development tools included:

```bash
# Linux development environment
pip install -e ".[dev,linux]"

# Windows development environment
pip install -e ".[dev,windows]"

# macOS development environment
pip install -e ".[dev,macos]"
```

### Dependencies

**Core dependencies** (automatically installed):
- `fastmcp>=2.3.0` - Modern MCP server framework
- `mcp>=1.9.4` - Model Context Protocol library
- `mss` - Cross-platform screenshot library
- `Pillow` - Image processing
- `pyautogui` - Cross-platform automation library

**Platform-specific dependencies**:
- **Linux**: `python-xlib` - X11 window management
- **Windows**: `pywin32` - Windows API access
- **macOS**: `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa` - macOS window management

**Development dependencies** (installed with `[dev]`):
- `pylint` - Code linting
- `pylint-plugin-utils` - Pylint utilities
- `pylint-mcp` - MCP-specific linting rules
- `black` - Code formatting

### Installation Examples

#### Quick Start (Production)
```bash
# Clone and install for your platform
git clone <repository-url>
cd mcp-screen-operation
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e ".[windows]"
```

#### Developer Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd mcp-screen-operation
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e ".[dev,windows]"

# Run development tools
black src/
pylint src/
```

## Usage

### Command Line Options

```bash
mcp-screen-operation --help
```

```
usage: mcp-screen-operation [-h] [--transport {stdio,sse,streamable-http}]
                            [--port PORT] [--host HOST]

MCP Screen Operation Server

options:
  -h, --help            show this help message and exit
  --transport {stdio,sse,streamable-http}
                        Transport protocol to use (default: stdio)
  --port PORT           Port for HTTP-based transports (default: 8205)
  --host HOST           Host for HTTP-based transports (default: 127.0.0.1)
```

### Command Examples

```bash
# Check version
mcp-screen-operation --version
```

### Running with Different Transports

#### STDIO (Default)
Perfect for local tools and Claude Desktop integration:
```bash
mcp-screen-operation
# or explicitly
mcp-screen-operation --transport stdio
```

#### Streamable HTTP (Recommended for Web)
Modern HTTP-based protocol for web deployments:
```bash
mcp-screen-operation --transport streamable-http --port 8205
```
Access at: `http://localhost:8205/mcp`

#### SSE (Legacy Web Support)
Server-Sent Events for legacy web deployments:
```bash
mcp-screen-operation --transport sse --port 8205
```
Access at: `http://localhost:8205/sse`

### Development Mode

Use FastMCP's development mode with inspector:
```bash
# After installing with: pip install -e ".[dev,windows]"
fastmcp dev src/screen_operation_server/main.py
```

### MCP Inspector

You can use the MCP Inspector to test and debug your MCP server interactively:

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector
```

The MCP Inspector provides a web-based interface to:
- Test all available tools
- View tool schemas and documentation
- Debug server responses
- Monitor server logs

## Available Tools

### Screen Information
- **`get_screen_info()`**: Retrieves information about connected displays
  - Returns: Monitor count and details (resolution, position) for each display

### Screen Capture
- **`capture_screen_by_number(monitor_number: int)`**: Captures a screenshot of the specified monitor
  - Args: `monitor_number` - The monitor to capture (0-based index)
  - Returns: Base64-encoded PNG image

- **`capture_all_screens()`**: Captures all connected monitors and stitches them into a single image
  - Returns: Base64-encoded PNG image of all screens combined

### Window Management
- **`get_window_list()`**: Retrieves a list of currently open windows
  - Returns: List of windows with ID, title, position, and dimensions

- **`capture_window(window_id: int)`**: Captures a screenshot of the specified window
  - Args: `window_id` - The window ID to capture
  - Returns: Base64-encoded PNG image of the window

### Mouse Automation
- **`mouse_move(x: int, y: int, duration: float = 0.0)`**: Moves the mouse cursor
  - Args: `x`, `y` - Target coordinates; `duration` - Movement duration in seconds
  - Returns: New mouse position

- **`mouse_click(x: int, y: int, button: str = "left", clicks: int = 1)`**: Clicks the mouse
  - Args: `x`, `y` - Click coordinates; `button` - Mouse button ('left', 'right', 'middle'); `clicks` - Number of clicks
  - Returns: Click information

- **`mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5)`**: Drags the mouse
  - Args: Start and end coordinates; `duration` - Drag duration
  - Returns: Drag operation details

- **`mouse_scroll(clicks: int, x: int = None, y: int = None)`**: Scrolls the mouse wheel
  - Args: `clicks` - Scroll amount (positive=up, negative=down); Optional coordinates
  - Returns: Scroll information

- **`get_mouse_position()`**: Gets current mouse position
  - Returns: Current coordinates and screen size

### Keyboard Automation
- **`keyboard_type(text: str, interval: float = 0.0)`**: Types text
  - Args: `text` - Text to type; `interval` - Delay between keystrokes
  - Returns: Typing information

- **`keyboard_press(key: str)`**: Presses a single key
  - Args: `key` - Key name (e.g., 'enter', 'tab', 'space', 'a')
  - Returns: Key press information

- **`keyboard_hotkey(keys: str)`**: Presses hotkey combination
  - Args: `keys` - Keys to press together, separated by '+' (e.g., 'ctrl+c')
  - Returns: Hotkey information

## Integration Examples

### Claude Desktop Integration

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "screen-operation": {
      "command": "mcp-screen-operation",
      "args": []
    }
  }
}
```

Or after PyPI publication, use uvx for automatic installation:

```json
{
  "mcpServers": {
    "screen-operation": {
      "command": "uvx",
      "args": ["mcp-screen-operation"]
    }
  }
}
```

### Web Application Integration

For Streamable HTTP:
```javascript
// Connect to the MCP server
const response = await fetch('http://localhost:8205/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name: 'get_screen_info',
      arguments: {}
    }
  })
});
```

### FastMCP Client Integration

```python
import asyncio
from fastmcp import FastMCP

async def main():
    # Connect to HTTP server
    client = FastMCP.create_client('http://localhost:8205/mcp')

    # Get screen info
    result = await client.call_tool('get_screen_info', {})
    print(result)

asyncio.run(main())
```

## Error Handling

The server automatically checks for platform-specific dependencies on startup:

- **Linux**: Validates `python-xlib` availability
- **Windows**: Validates `pywin32` availability
- **macOS**: Validates `PyObjC` availability

If dependencies are missing, the server will display installation instructions and exit.

## Development

### Development Environment Setup

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd mcp-screen-operation
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install in development mode
pip install -e ".[dev,windows]"  # Replace 'windows' with your platform
```

2. **Code formatting and linting:**
```bash
# Format code
black src/

# Run linter
pylint src/
```

3. **Testing during development:**
```bash
# Test the server
mcp-screen-operation --help

# Test with different transports
mcp-screen-operation --transport stdio
mcp-screen-operation --transport sse --port 8205
mcp-screen-operation --transport streamable-http --port 8205
```

### Available Extras

- `linux`: Linux platform dependencies (`python-xlib`)
- `windows`: Windows platform dependencies (`pywin32`)
- `macos`: macOS platform dependencies (`PyObjC` frameworks)
- `dev`: Development tools (`pylint`, `black`)
