# System Patterns: `pape-mcp-server-time`

## 1. System Architecture

The system is a Python-based Model Context Protocol (MCP) server. It is designed to be a lightweight, standalone package that can be run using `uv` or `pip`.

- **Package Manager:** `uv` and `pip`
- **Build System:** `pyproject.toml`
- **Language:** Python

## 2. Key Technical Decisions

- **Forking Strategy:** Instead of a full Git fork, we are downloading a specific subdirectory (`src/time`) from the source repository. This approach is chosen for its simplicity and to avoid the overhead of the larger monorepo.
- **Package Naming:** The forked package will be named `pape-mcp-server-time` to distinguish it from the original `mcp-server-time` and to reflect the user's namespace.

## 3. Component Relationships

The server is a single, self-contained package with the following key components:

- **`pyproject.toml`:** Defines the project metadata, dependencies, and entry points. This will be the primary file to modify for renaming the package.
- **`mcp_server_time/` (or `pape_mcp_server_time/` after rename):** The main source directory containing the server's logic.
    - **`main.py` (or equivalent):** The entry point for the server application.
    - **Tool Implementations:** Python modules that define the `get_current_time` and `convert_time` tools.

## 4. Critical Implementation Paths

1. **Downloading the code:** The `svn export` command is critical for obtaining the correct source files.
2. **Renaming the package:** Correctly modifying `pyproject.toml` is essential for the new package to be recognized. This includes updating the `name` field and potentially the `[project.scripts]` entry point.
3. **Running the server:** The `uv run` command will be the primary way to test the server locally.
