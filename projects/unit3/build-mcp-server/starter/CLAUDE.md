# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP server implementation for a PR (Pull Request) agent that helps developers analyze git changes and suggest appropriate PR templates. The server provides three main tools for Claude to use when analyzing code changes and recommending PR templates.

## Development Commands

### Setup and Dependencies
```bash
# Install all dependencies
uv sync

# Install with development dependencies (includes testing)
uv sync --all-extras
```

### Running the Server
```bash
# Run the MCP server directly
uv run server.py

# Run with Python module flag
uv run -m server
```

### Testing
```bash
# Run all tests
uv run pytest test_server.py -v

# Run tests with verbose output
uv run pytest test_server.py -v --tb=short

# Validate starter code setup
uv run python validate_starter.py
```

## Architecture

### Core Components

**FastMCP Server Instance**: The main server is instantiated as `mcp = FastMCP("pr-agent")` in server.py:16

**Three Main Tools**:
1. `analyze_file_changes()` - Analyzes git repository changes using git commands
2. `get_pr_templates()` - Retrieves available PR templates from templates directory
3. `suggest_template()` - Suggests appropriate template based on change analysis

**Template System**: 
- Templates stored in `templates/` directory
- Default templates: `bug.md`, `feature.md`, `refactor.md`
- Template mapping defined in `TYPE_MAPPING` dictionary (server.py:29-36)

### Key Implementation Details

**Git Integration**: Uses subprocess to execute git commands for repository analysis:
- `git diff --name-status` for changed files
- `git diff --stat` for statistics
- `git diff` for full diff content
- `git log --oneline` for commit history

**Working Directory Handling**: The server attempts to determine the working directory through:
1. MCP session roots (preferred method)
2. Provided working_directory parameter
3. Fallback to current working directory

**Template Selection Logic**: Maps change types to template files using `TYPE_MAPPING`:
- "bug"/"fix" → `bug.md`
- "feature"/"enhancement" → `feature.md`  
- "refactor"/"cleanup" → `refactor.md`

## Configuration for Claude Code

To use this MCP server with Claude Code:

```bash
# Add the MCP server (replace with actual absolute path)
claude mcp add pr-agent -- uv --directory /absolute/path/to/starter run server.py

# Verify configuration
claude mcp list
```

## Testing Strategy

The test suite (`test_server.py`) validates:
- Function imports and FastMCP registration
- JSON response format for all tools
- Error handling for git operations
- Template retrieval and suggestion logic
- Starter code vs. implementation detection

## File Structure

```
starter/
├── server.py           # Main MCP server implementation
├── pyproject.toml      # Project dependencies and metadata
├── test_server.py      # Comprehensive test suite
├── validate_starter.py # Starter code validation
├── templates/          # PR template files
│   ├── bug.md
│   ├── feature.md
│   └── refactor.md
└── README.md          # Project documentation
```

## Development Notes

- The server includes debug information in responses to help with troubleshooting working directory issues
- All tools return JSON strings for consistent Claude integration
- Template content is read from markdown files in the templates directory
- Error handling includes both subprocess and general exception catching
- The implementation supports diff truncation to manage large outputs (max_diff_lines parameter)