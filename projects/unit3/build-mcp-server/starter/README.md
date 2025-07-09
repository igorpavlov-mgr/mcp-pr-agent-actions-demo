# PR Agent MCP Server

A comprehensive MCP server that combines PR template analysis with GitHub Actions webhook integration for event-driven automation, CI/CD monitoring, and intelligent incident response.

## Overview

This project evolved from a basic PR template suggestion tool into a full-featured MCP server that provides:

- **Git Analysis Tools**: Analyze code changes and suggest appropriate PR templates
- **GitHub Actions Integration**: Webhook-based event collection and workflow monitoring
- **Event-Driven Automation**: MCP Prompts for standardized CI/CD workflows
- **Intelligent Template Selection**: AI-powered template recommendations based on code changes
- **Incident Response System**: Event tracking, failure detection, and team notification automation
- **Team Management**: Repository ownership mapping and expertise-based routing

## Architecture

### Core Components

1. **FastMCP Server**: Built on FastMCP framework with tools and prompts
2. **Git Integration**: Subprocess-based git analysis with diff handling
3. **Webhook Events**: GitHub Actions webhook integration via `github_events.json`
4. **Template System**: Extensible PR template framework with security support
5. **Event Processing**: Repository-grouped workflow status with time tracking
6. **Incident Management**: Event state tracking and team notification system

### Event-Driven Patterns

The server follows established patterns for event-driven automation:

- **Webhook Collection**: GitHub Actions events stored in structured JSON format
- **Repository Grouping**: Workflows organized by repository for better tracking
- **Time-Based Analysis**: Datetime calculations for workflow timing insights
- **Status Filtering**: Conclusion-based filtering for targeted monitoring
- **Event State Management**: Persistent tracking of processed events to prevent duplicates
- **Failure Detection**: Automated identification of new failures requiring attention
- **Team Routing**: Intelligent notification routing based on repository ownership and expertise

## Setup

### 1. Install uv

Follow the official installation instructions at: https://docs.astral.sh/uv/getting-started/installation/

### 2. Install dependencies

```bash
# Install all dependencies including webhook support
uv sync

# Install with dev dependencies for testing
uv sync --all-extras
```

### 3. Configure the MCP Server

Add the server to Claude Code:

```bash
# Add the MCP server (replace with your actual path)
claude mcp add pr-agent -- uv --directory /absolute/path/to/starter run server.py

# Verify it's configured
claude mcp list
```

### 4. Set up team configuration (optional)

Edit `team_config.json` to customize repository ownership and team routing:

```json
{
  "repositories": {
    "your-org/repo-name": ["owner1", "owner2"]
  },
  "expertise": {
    "frontend": ["frontend-lead"],
    "backend": ["backend-lead"],
    "security": ["security-lead"]
  },
  "on_call": {
    "primary": "on-call-engineer",
    "secondary": "backup-engineer"
  }
}
```

## Tools Available

### Git Analysis Tools

1. **analyze_file_changes** - Get git diff and changed files with repository analysis
   - Parameters: `base_branch`, `include_diff`, `max_diff_lines`, `working_directory`
   - Returns: JSON with files changed, statistics, commits, and diff content

2. **get_pr_templates** - List available PR templates with content
   - Returns: Array of template objects with filename, type, and content

3. **suggest_template** - AI-powered template suggestion based on change analysis
   - Parameters: `changes_summary`, `change_type`
   - Returns: Recommended template with reasoning and usage hints

### GitHub Actions Tools

4. **get_recent_actions_events** - Retrieve recent GitHub Actions webhook events
   - Parameters: `limit` (default: 10)
   - Returns: Array of recent webhook events from `github_events.json`

5. **get_workflow_status** - Advanced workflow status analysis
   - Parameters: `conclusion` (optional filter: success, failure, cancelled, skipped)
   - Returns: Repository-grouped workflow status with time calculations
   - Features: Time since last run, conclusion filtering, comprehensive statistics

### Incident Response Tools

6. **get_unseen_events** - Track which events haven't been processed yet
   - Parameters: `mark_as_seen` (optional: mark returned events as processed)
   - Returns: List of unprocessed events with unique event IDs
   - Features: Persistent state tracking to prevent duplicate processing

7. **get_new_failures** - Identify recent workflow failures that need attention
   - Parameters: `since_hours` (default: 24)
   - Returns: Grouped failure analysis with counts and timing
   - Features: Repository and workflow grouping, failure frequency analysis

8. **suggest_team_notification** - Get team member suggestions for failures
   - Parameters: `repository`, `workflow_name`, `failure_type`
   - Returns: Notification suggestions based on ownership and expertise
   - Features: Repository owners, expertise routing, on-call escalation

9. **mark_events_as_seen** - Manually mark events as processed
   - Parameters: `event_ids` (list of event IDs to mark as seen)
   - Returns: Confirmation of marked events
   - Features: Prevents duplicate notifications and processing

## MCP Prompts

### Automation Prompts

1. **analyze_ci_results** - Analyze CI/CD results and provide insights
   - Fetches recent events and workflow status
   - Identifies failures and provides actionable recommendations

2. **create_deployment_summary** - Generate deployment summary for team communication
   - Checks deployment workflows and creates Slack-ready messages
   - Includes status, timing, and issue tracking

3. **generate_pr_status_report** - Comprehensive PR status combining code and CI/CD
   - Integrates git analysis with workflow status
   - Provides complete PR readiness assessment

4. **troubleshoot_workflow_failure** - Systematic workflow troubleshooting guide
   - Analyzes failure patterns and provides diagnostic steps
   - Includes cause analysis and suggested fixes

5. **review_pull_request** - Structured PR review combining all data sources
   - Calls multiple tools to provide comprehensive review
   - Combines code changes with CI/CD status for complete picture

6. **incident_response_dashboard** - Comprehensive incident response automation
   - Orchestrates unseen event detection, failure analysis, and team notifications
   - Generates actionable incident response dashboard
   - Provides structured workflow for handling CI/CD failures

## Template System

### Available Templates

- **bug.md** - Bug fix template with issue tracking
- **feature.md** - New feature template with documentation checklist
- **refactor.md** - Code refactoring template
- **security.md** - Security-related changes template

### Template Mapping

The server uses intelligent type mapping:
- `bug`, `fix` → `bug.md`
- `feature`, `enhancement` → `feature.md`  
- `refactor`, `cleanup` → `refactor.md`
- `security`, `vulnerability` → `security.md`

## Usage Examples

### Basic PR Analysis

```bash
# Ask Claude to analyze changes
"Can you analyze my changes and suggest a PR template?"
```

### CI/CD Monitoring

```bash
# Check recent GitHub Actions events
"What are the recent GitHub Actions events?"

# Analyze CI/CD status
"Use the analyze_ci_results prompt to check our CI/CD health"

# Get workflow status for specific conclusion
"Show me all failed workflows using get_workflow_status with conclusion='failure'"
```

### Incident Response

```bash
# Check for unseen events
"Use get_unseen_events to check for any new events since last check"

# Identify new failures
"Use get_new_failures to find failures in the last 24 hours"

# Get team notification suggestions
"Who should be notified for a deployment failure in the backend repository?"

# Generate comprehensive incident dashboard
"Use the incident_response_dashboard prompt to create a complete incident response report"
```

### Event Management

```bash
# Mark events as processed
"Mark these event IDs as seen: ['2025-07-08T03:00:19.373313:workflow_run:user/repo']"

# Get unseen events and mark them as seen
"Use get_unseen_events with mark_as_seen=true to process new events"
```

### Comprehensive PR Review

```bash
# Use the review_pull_request prompt
"Generate a comprehensive PR review using the review_pull_request prompt"
```

## Webhook Integration

### Event Collection

The server expects GitHub Actions webhook events in `github_events.json`:

```json
[
  {
    "timestamp": "2025-07-08T03:00:19.373313",
    "event_type": "workflow_run",
    "action": "completed",
    "workflow_run": {
      "name": "CI",
      "status": "completed",
      "conclusion": "success",
      "updated_at": "2025-07-08T03:00:15Z",
      "html_url": "https://github.com/user/repo/actions/runs/123"
    },
    "repository": "user/repo",
    "sender": "username"
  }
]
```

### GitHub Webhook Configuration

Configure your GitHub repository webhook with these events:
- ✅ **workflow runs** - Essential for failure detection and monitoring
- ✅ **pushes** - Context for correlating changes with failures
- ✅ **check runs** - Individual check results
- ✅ **pull requests** - PR-related workflow triggers

### Supported Event Types

- **ping** - Webhook setup verification
- **push** - Code push events (provides context)
- **workflow_run** - GitHub Actions workflow execution (primary data source)
- **check_run** - Individual check results
- **pull_request** - Pull request events (future enhancement opportunities)

## Testing

### Run Tests

```bash
# Test the MCP server directly
uv run server.py

# Test individual tools (example)
uv run python3 -c "import asyncio; from server import suggest_template; print(asyncio.run(suggest_template('test', 'bug')))"
```

### Test Webhook Integration

1. Set up GitHub webhook pointing to your webhook server
2. Configure webhook events: workflow runs, pushes, check runs, pull requests
3. Push code changes or trigger workflows manually
4. Use `get_recent_actions_events` to verify event collection
5. Test failure detection with `get_new_failures`
6. Test team notifications with `suggest_team_notification`

### Test MCP Tools

```bash
# Test git analysis
"Can you analyze my git changes using analyze_file_changes?"

# Test template suggestion
"Can you suggest a template for my bug fix using suggest_template?"

# Test GitHub Actions events
"Show me recent GitHub Actions events using get_recent_actions_events"
```

### Test Incident Response

```bash
# Test the complete incident response workflow
"Use the incident_response_dashboard prompt to test the full incident response system"

# Test event state tracking
"Use get_unseen_events to verify event tracking works correctly"

# Test team notification routing
"Test suggest_team_notification with different repositories and failure types"
```

## Running the Server

```bash
# Start the MCP server
uv run server.py
```

The server will:
- Initialize FastMCP with all tools and prompts
- Be ready to process git analysis requests
- Monitor `github_events.json` for webhook events
- Track event processing state in `events_state.json`
- Use team configuration from `team_config.json`
- Provide comprehensive CI/CD monitoring and incident response capabilities

## Event-Driven Automation Patterns

### Repository-Centric Design

- All workflow data is grouped by repository
- Time calculations show workflow freshness
- Status filtering enables targeted monitoring
- Repository ownership mapping for notification routing

### Prompt-Based Workflows

- Standardized prompts for common CI/CD tasks
- Consistent output formatting for team communication
- Extensible pattern for new automation scenarios
- Orchestrated incident response workflows

### Intelligent Analysis

- AI-powered template selection based on code changes
- Context-aware failure analysis and troubleshooting
- Comprehensive reporting combining multiple data sources
- Smart team notification routing based on expertise and ownership

### Event State Management

- Persistent tracking of processed events
- Prevention of duplicate notifications
- Time-based failure detection and escalation
- Configurable team routing and expertise mapping

## Dependencies

- `mcp[cli]>=1.0.0` - FastMCP framework
- `aiohttp>=3.10.0,<4.0.0` - HTTP client for webhook handling
- `pytest>=8.3.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support

## File Structure

```
starter/
├── server.py              # Main MCP server implementation
├── pyproject.toml         # Project dependencies and metadata
├── github_events.json     # Webhook events storage
├── events_state.json      # Event processing state tracking
├── team_config.json       # Team member and expertise mapping
├── webhook_server.py      # GitHub webhook receiver (optional)
├── templates/             # PR template files
│   ├── bug.md
│   ├── feature.md
│   ├── refactor.md
│   └── security.md
├── CLAUDE.md             # Claude Code guidance
└── README.md             # This file
```

## Integration Examples

### Sample GitHub Actions Workflow

The server works perfectly with simple CI workflows:

```yaml
name: CI
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run tests
        run: |
          pip install uv
          uv sync
          uv run server.py
```

This MCP server provides a complete solution for intelligent PR analysis and event-driven GitHub Actions automation with comprehensive incident response capabilities, leveraging Claude's AI capabilities for enhanced development workflows and team coordination.