# Random Number MCP

Production-ready MCP server that provides LLMs with essential random generation abilities --- built entirely on Python's standard library.

## 🎲 Tools


| Tool                | Purpose                                      | Python function   |
| ------------------- | -------------------------------------------- | --------------------- |
| `random_int`        | Generate random integers                     | `random.randint()`    |
| `random_float`      | Generate random floats                       | `random.uniform()`    |
| `random_choices`    | Choose items from a list (optional weights)  | `random.choices()`    |
| `random_shuffle`    | Return a new list with items shuffled        | `random.sample()`     |
| `secure_token_hex`  | Generate cryptographically secure hex tokens | `secrets.token_hex()` |
| `secure_random_int` | Generate cryptographically secure integers   | `secrets.randbelow()` |


## 🔧 Setup

### Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "random-number": {
      "command": "uvx",
      "args": ["random-number-mcp"]
    }
  }
}
```

## 📋 Tool Reference

### `random_int`

Generate a random integer between low and high (inclusive).

**Parameters:**
- `low` (int): Lower bound (inclusive)
- `high` (int): Upper bound (inclusive)

**Example:**
```json
{
  "name": "random_int",
  "arguments": {
    "low": 1,
    "high": 100
  }
}
```

### `random_float`

Generate a random float between low and high.

**Parameters:**
- `low` (float, optional): Lower bound (default: 0.0)
- `high` (float, optional): Upper bound (default: 1.0)

**Example:**
```json
{
  "name": "random_float",
  "arguments": {
    "low": 0.5,
    "high": 2.5
  }
}
```

### `random_choices`

Choose k items from a population with replacement, optionally weighted.

**Parameters:**
- `population` (list): List of items to choose from
- `k` (int, optional): Number of items to choose (default: 1)
- `weights` (list, optional): Weights for each item (default: equal weights)

**Example:**
```json
{
  "name": "random_choices",
  "arguments": {
    "population": ["red", "blue", "green", "yellow"],
    "k": 2,
    "weights": [0.4, 0.3, 0.2, 0.1]
  }
}
```

### `random_shuffle`

Return a new list with items in random order.

**Parameters:**
- `items` (list): List of items to shuffle

**Example:**
```json
{
  "name": "random_shuffle",
  "arguments": {
    "items": [1, 2, 3, 4, 5]
  }
}
```

### `secure_token_hex`

Generate a cryptographically secure random hex token.

**Parameters:**
- `nbytes` (int, optional): Number of random bytes (default: 32)

**Example:**
```json
{
  "name": "secure_token_hex",
  "arguments": {
    "nbytes": 16
  }
}
```

### `secure_random_int`

Generate a cryptographically secure random integer below upper_bound.

**Parameters:**
- `upper_bound` (int): Upper bound (exclusive)

**Example:**
```json
{
  "name": "secure_random_int",
  "arguments": {
    "upper_bound": 1000
  }
}
```

## 🔒 Security Considerations

This package provides both standard pseudorandom functions (suitable for simulations, games, etc.) and cryptographically secure functions (suitable for tokens, keys, etc.):

- **Standard functions** (`random_int`, `random_float`, `random_choices`, `random_shuffle`): Use Python's `random` module - fast but not cryptographically secure
- **Secure functions** (`secure_token_hex`, `secure_random_int`): Use Python's `secrets` module - slower but cryptographically secure

## 🛠️ Development

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/example/random-number-mcp
cd random-number-mcp

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run ruff format

# Type checking
uv run mypy src/
```

### Building

```bash
# Build package
uv build

# Test installation
uv run --with dist/*.whl random-number-mcp
```

### Notes

- The server communicates via STDIO using JSON-RPC 2.0 protocol.

## Testing with MCP Inspector

For exploring and/or developing this server, use the MCP Inspector npm utility:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run local development server with the inspector
npx @modelcontextprotocol/inspector uv run random-number-mcp

# Run PyPI production server with the inspector
npx @modelcontextprotocol/inspector uvx random-number-mcp
```


## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Python random module](https://docs.python.org/3/library/random.html)
- [Python secrets module](https://docs.python.org/3/library/secrets.html)
