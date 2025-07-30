"""Main MCP server using FastMCP to expose random number utilities."""

from typing import Any

from fastmcp import FastMCP

from . import tools

# Create the FastMCP server instance
app: FastMCP = FastMCP("Random Number Utilities")


@app.tool()
def random_int(low: int, high: int) -> int:
    """Generate a random integer between low and high (inclusive).

    Args:
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)

    Returns:
        Random integer between low and high
    """
    return tools.random_int(low, high)


@app.tool()
def random_float(low: float = 0.0, high: float = 1.0) -> float:
    """Generate a random float between low and high.

    Args:
        low: Lower bound (default 0.0)
        high: Upper bound (default 1.0)

    Returns:
        Random float between low and high
    """
    return tools.random_float(low, high)


@app.tool()
def random_choices(
    population: list[Any], k: int = 1, weights: list[int | float] | None = None
) -> list[Any]:
    """Choose k items from population with replacement, optionally weighted.

    Args:
        population: List of items to choose from
        k: Number of items to choose (default 1)
        weights: Optional weights for each item (default None for equal weights)

    Returns:
        List of k chosen items
    """
    return tools.random_choices(population, k, weights)


@app.tool()
def random_shuffle(items: list[Any]) -> list[Any]:
    """Return a new list with items in random order.

    Args:
        items: List of items to shuffle

    Returns:
        New list with items in random order
    """
    return tools.random_shuffle(items)


@app.tool()
def secure_token_hex(nbytes: int = 32) -> str:
    """Generate a secure random hex token.

    Args:
        nbytes: Number of random bytes to generate (default 32)

    Returns:
        Hex string containing 2*nbytes characters
    """
    return tools.secure_token_hex(nbytes)


@app.tool()
def secure_random_int(upper_bound: int) -> int:
    """Generate a secure random integer below upper_bound.

    Args:
        upper_bound: Upper bound (exclusive)

    Returns:
        Random integer in range [0, upper_bound)
    """
    return tools.secure_random_int(upper_bound)


def main() -> None:
    """Main entry point for the MCP server."""
    app.run()


if __name__ == "__main__":
    main()
