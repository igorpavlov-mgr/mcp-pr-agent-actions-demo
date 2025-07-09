# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive FastMCP server implementation that combines PR (Pull Request) template analysis with GitHub Actions webhook integration for event-driven automation, CI/CD monitoring, intelligent incident response, and Slack notifications for complete team communication workflows. The server provides tools for direct function calls, prompts for standardized workflows, advanced incident management capabilities, and real-time team notifications.

## Development Commands

### Setup and Dependencies
```bash
# Install all dependencies (includes aiohttp for webhook support, requests for Slack, python-dotenv for environment management)
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

**FastMCP Server Instance**: The main server is instantiated as `mcp = FastMCP("pr-agent")` in server.py:33

**Ten Main Tools**:
1. `analyze_file_changes()` - Analyzes git repository changes using git commands
2. `get_pr_templates()` - Retrieves available PR templates from templates directory
3. `suggest_template()` - Suggests appropriate template based on change analysis
4. `get_recent_actions_events()` - Retrieves recent GitHub Actions webhook events
5. `get_workflow_status()` - Advanced workflow status analysis with repository grouping
6. `get_unseen_events()` - Track which events haven't been processed yet
7. `get_new_failures()` - Identify recent workflow failures that need attention
8. `suggest_team_notification()` - Get team member suggestions for failures
9. `mark_events_as_seen()` - Manually mark events as processed
10. `send_slack_notification()` - Send formatted notifications to team Slack channel

**Eight MCP Prompts**:
1. `analyze_ci_results()` - Analyze CI/CD results and provide insights
2. `create_deployment_summary()` - Generate deployment summary for team communication
3. `generate_pr_status_report()` - Comprehensive PR status combining code and CI/CD
4. `troubleshoot_workflow_failure()` - Systematic workflow troubleshooting guide
5. `review_pull_request()` - Structured PR review combining all data sources
6. `incident_response_dashboard()` - Comprehensive incident response automation
7. `format_ci_failure_alert()` - Create Slack alerts for CI/CD failures with rich formatting
8. `format_ci_success_summary()` - Create Slack messages for successful deployments

**Template System**: 
- Templates stored in `templates/` directory
- Default templates: `bug.md`, `feature.md`, `refactor.md`, `security.md`
- Template mapping defined in `TYPE_MAPPING` dictionary (server.py:56-65)

**Webhook Integration**:
- GitHub Actions events stored in `github_events.json`
- Event collection via webhook endpoints
- Repository-grouped workflow analysis

**Incident Management System**:
- Event state tracking in `events_state.json`
- Team configuration in `team_config.json`
- Persistent tracking of processed events
- Intelligent team notification routing

**Slack Integration**:
- Real-time notifications via webhook URL stored in `.env`
- Secure environment variable management with `python-dotenv`
- Rich formatting support for Slack markdown
- Timeout protection and comprehensive error handling

### Key Implementation Details

**Git Integration**: Uses subprocess to execute git commands for repository analysis:
- `git diff --name-status` for changed files
- `git diff --stat` for statistics
- `git diff` for full diff content (with truncation support)
- `git log --oneline` for commit history

**Working Directory Handling**: The server attempts to determine the working directory through:
1. MCP session roots (preferred method)
2. Provided working_directory parameter
3. Fallback to current working directory

**Template Selection Logic**: Maps change types to template files using `TYPE_MAPPING`:
- "bug"/"fix" → `bug.md`
- "feature"/"enhancement" → `feature.md`  
- "refactor"/"cleanup" → `refactor.md`
- "security"/"vulnerability" → `security.md`

**GitHub Actions Integration**: 
- Events file: `EVENTS_FILE = Path(__file__).parent / "github_events.json"`
- State file: `EVENTS_STATE_FILE = Path(__file__).parent / "events_state.json"`
- Team config: `TEAM_CONFIG_FILE = Path(__file__).parent / "team_config.json"`
- Repository grouping for workflow status
- Time calculations using `datetime`, `timezone`, and `timedelta`
- Conclusion-based filtering (success, failure, cancelled, skipped)

**Incident Response Patterns**:
- Event state management with unique event IDs
- Failure detection and grouping by repository and workflow
- Team notification routing based on repository ownership and expertise
- Time-based failure analysis and escalation
- Persistent state tracking to prevent duplicate notifications

**Event-Driven Patterns**:
- Repository-centric workflow organization
- Time-based analysis for workflow freshness
- Status filtering for targeted monitoring
- Prompt-based standardized workflows
- Automated incident response orchestration

## Configuration for Claude Code

To use this MCP server with Claude Code:

```bash
# Add the MCP server (replace with actual absolute path)
claude mcp add pr-agent -- uv --directory /absolute/path/to/starter run server.py

# Verify configuration
claude mcp list
```

## Tool Usage Patterns

### Git Analysis Tools
- `analyze_file_changes()` - For understanding code changes
- `get_pr_templates()` - For retrieving available templates
- `suggest_template()` - For AI-powered template recommendations

### GitHub Actions Tools
- `get_recent_actions_events()` - For webhook event history
- `get_workflow_status()` - For comprehensive workflow analysis

### Incident Response Tools
- `get_unseen_events()` - For tracking unprocessed events
- `get_new_failures()` - For identifying recent failures requiring attention
- `suggest_team_notification()` - For team member routing and notification
- `mark_events_as_seen()` - For event state management

### Slack Integration Tools
- `send_slack_notification()` - For sending formatted messages to team Slack channel
- `format_ci_failure_alert()` - For creating properly formatted failure alerts
- `format_ci_success_summary()` - For creating deployment success celebrations

### Prompt Usage
- Use prompts for standardized workflows and team communication
- Prompts automatically call multiple tools and provide structured output
- Examples: `analyze_ci_results`, `create_deployment_summary`, `incident_response_dashboard`
- The `incident_response_dashboard` prompt orchestrates multiple incident response tools

## Common Workflows

### Basic Event Processing
1. Use `get_unseen_events()` to check for new events
2. Use `get_new_failures()` to identify failures needing attention
3. Use `suggest_team_notification()` for each failure to determine who to notify
4. Use `mark_events_as_seen()` to mark events as processed

### Comprehensive Incident Response
1. Use `incident_response_dashboard()` prompt for complete automation
2. This orchestrates all incident response tools automatically
3. Provides structured dashboard with notification recommendations

### Team Configuration
1. Edit `team_config.json` to set up repository owners and expertise mapping
2. Configure on-call rotations and notification preferences
3. Test with `suggest_team_notification()` to verify routing

### Slack Integration Workflow
1. Create `.env` file with `SLACK_WEBHOOK_URL` configuration
2. Use `format_ci_failure_alert()` or `format_ci_success_summary()` prompts for proper formatting
3. Send formatted messages via `send_slack_notification()` tool
4. Monitor delivery status and handle any webhook failures

## Testing Strategy

The test suite (`test_server.py`) validates:
- Function imports and FastMCP registration
- JSON response format for all tools
- Error handling for git operations and incident response
- Template retrieval and suggestion logic
- Starter code vs. implementation detection
- Webhook event processing and state management
- Datetime calculations for workflow analysis
- Event state tracking and team notification logic
- Slack webhook integration and message formatting
- Environment variable loading and secure configuration

## File Structure

```
starter/
├── server.py              # Main MCP server implementation
├── pyproject.toml         # Project dependencies and metadata
├── .env                   # Environment variables (Slack webhook URL)
├── github_events.json     # GitHub Actions webhook events storage
├── events_state.json      # Event processing state tracking
├── team_config.json       # Team member and expertise mapping
├── webhook_server.py      # GitHub webhook receiver (optional)
├── test_server.py         # Comprehensive test suite
├── validate_starter.py    # Starter code validation
├── templates/             # PR template files
│   ├── bug.md
│   ├── feature.md
│   ├── refactor.md
│   └── security.md
├── CLAUDE.md             # This file - Claude Code guidance
└── README.md             # Project documentation
```

## Development Notes

### Error Handling
- All tools return JSON strings for consistent Claude integration
- Comprehensive error handling for git operations, webhook processing, and incident response
- Graceful fallbacks for missing webhook events, malformed data, or configuration issues
- Event state management with error recovery

### Performance Considerations
- Diff truncation to manage large outputs (`max_diff_lines` parameter)
- Efficient repository grouping for workflow analysis
- Time calculations optimized for webhook event processing
- Event state tracking optimized to prevent duplicate processing
- Intelligent caching of team configuration data

### Webhook Integration
- Events are stored in structured JSON format
- Repository-based organization for better tracking
- Time-based analysis for workflow freshness monitoring
- Support for multiple event types (ping, push, workflow_run, check_run, pull_request)
- Event state management to track processing status

### Incident Response System
- Persistent event state tracking prevents duplicate notifications
- Time-based failure detection with configurable windows
- Repository and workflow grouping for intelligent analysis
- Team notification routing based on ownership and expertise
- Configurable team mapping and on-call rotation support

### Template System
- Extensible template framework with security support
- Intelligent type mapping for automated template selection
- Content read from markdown files in templates directory

### Dependencies
- `mcp[cli]>=1.0.0` - FastMCP framework
- `aiohttp>=3.10.0,<4.0.0` - HTTP client for webhook handling
- `requests>=2.31.0` - HTTP client for Slack webhook notifications
- `python-dotenv>=1.0.0` - Environment variable management for secure configuration
- `datetime`, `timezone`, `timedelta` - For time calculations and event tracking
- `subprocess` - For git command execution
- `json` - For structured data handling

## Common Development Tasks

### Adding New Templates
1. Create new template file in `templates/` directory
2. Add to `DEFAULT_TEMPLATES` dictionary
3. Update `TYPE_MAPPING` for intelligent selection

### Extending Webhook Support
1. Add new event types to webhook processing logic
2. Update relevant tools (`get_workflow_status()`, `get_new_failures()`) for new event types
3. Consider adding new prompts for specific automation scenarios
4. Update event state tracking if needed

### Enhancing Slack Integration
1. Add new Slack formatting prompts for specific notification types
2. Extend `send_slack_notification()` with additional features (e.g., message threading, channel selection)
3. Add retry logic for failed webhook deliveries
4. Implement message queuing for high-volume notifications
5. Add support for Slack interactive components (buttons, modals)

### Enhancing Incident Response
1. Add new failure detection patterns in `get_new_failures()`
2. Extend team notification logic in `suggest_team_notification()`
3. Update team configuration schema in `team_config.json`
4. Add new automation prompts for specific incident types

### Testing New Features
1. Add unit tests to `test_server.py`
2. Test webhook integration with real GitHub Actions events
3. Validate prompt outputs for consistency
4. Test incident response workflows end-to-end
5. Verify event state tracking and team notification routing

### Debugging

#### Event Processing
- Check `github_events.json` for webhook event collection
- Use `get_recent_actions_events()` to verify webhook integration
- Check `events_state.json` for event processing state
- Use `get_unseen_events()` to identify unprocessed events

#### Incident Response
- Use `get_new_failures()` to verify failure detection logic
- Test `suggest_team_notification()` with different repositories and failure types
- Check `team_config.json` for proper team mapping configuration
- Use `incident_response_dashboard()` prompt to test complete workflow

#### Git Integration
- Monitor git command execution in `analyze_file_changes()`
- Server includes debug information in responses
- Check working directory resolution logic

#### Slack Integration
- Test `send_slack_notification()` with different message formats
- Verify `.env` file loading and environment variable access
- Check webhook delivery status and error handling
- Test prompt formatting with `format_ci_failure_alert()` and `format_ci_success_summary()`

### Configuration Management

#### Team Configuration (`team_config.json`)
```json
{
  "repositories": {
    "org/repo": ["owner1", "owner2"]
  },
  "expertise": {
    "frontend": ["frontend-dev"],
    "backend": ["backend-dev"],
    "security": ["security-engineer"]
  },
  "on_call": {
    "primary": "on-call-engineer",
    "secondary": "backup-engineer"
  }
}
```

#### Event State Management
- Event IDs format: `{timestamp}:{event_type}:{repository}`
- State tracking prevents duplicate processing
- Configurable retention and cleanup policies

#### Slack Configuration (`.env`)
```bash
# Slack webhook URL for team notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

**Security Best Practices:**
- Never commit `.env` files to version control
- Use environment-specific webhook URLs
- Rotate webhook URLs periodically
- Monitor delivery failures and webhook health

This MCP server provides a complete solution for intelligent PR analysis and event-driven GitHub Actions automation with comprehensive incident response capabilities and real-time Slack notifications, leveraging Claude's AI capabilities for enhanced development workflows and seamless team coordination.