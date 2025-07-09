#!/usr/bin/env python3
"""
Module 1: Basic MCP Server - Starter Code
Implements tools for analyzing git changes and suggesting PR templates
"""

"""
Module 2: GitHub Actions Integration with MCP Prompts
Extends the PR agent with webhook handling and standardized CI/CD workflows using Prompts.
"""

"""
Module 3: Slack Notification Integration - Complete Solution
Combines all MCP primitives (Tools and Prompts) for complete team communication workflows.
"""

import json
import os
import subprocess
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from typing import Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# File where webhook server stores events
EVENTS_FILE = Path(__file__).parent / "github_events.json"

# File to track event processing state
EVENTS_STATE_FILE = Path(__file__).parent / "events_state.json"

# File to store team member mappings
TEAM_CONFIG_FILE = Path(__file__).parent / "team_config.json"

# PR template directory (shared across all modules)
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Default PR templates
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "refactor.md": "Refactor",
    "security.md": "Security"
}

# Type mapping for PR templates
TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "security": "security.md",
    "vulnerability": "security.md"
}

# MCP Tools

@mcp.tool()
async def analyze_file_changes(
    base_branch: str = "main",
    include_diff: bool = True,
    max_diff_lines: int = 500,
    working_directory: Optional[str] = None
) -> str:
    """Get the full diff and list of changed files in the current git repository.
    
    Args:
        base_branch: Base branch to compare against (default: main)
        include_diff: Include the full diff content (default: true)
        max_diff_lines: Maximum number of diff lines to include (default: 500)
        working_directory: Directory to run git commands in (default: current directory)
    """
    try:
        # Try to get working directory from roots first
        if working_directory is None:
            try:
                context = mcp.get_context()
                roots_result = await context.session.list_roots()
                # Get the first root - Claude Code sets this to the CWD
                root = roots_result.roots[0]
                # FileUrl object has a .path property that gives us the path directly
                working_directory = root.uri.path
            except Exception:
                # If we can't get roots, fall back to current directory
                pass
        
        # Use provided working directory or current directory
        cwd = working_directory if working_directory else os.getcwd()
        
        # Debug output
        debug_info = {
            "provided_working_directory": working_directory,
            "actual_cwd": cwd,
            "server_process_cwd": os.getcwd(),
            "server_file_location": str(Path(__file__).parent),
            "roots_check": None
        }
        
        # Add roots debug info
        try:
            context = mcp.get_context()
            roots_result = await context.session.list_roots()
            debug_info["roots_check"] = {
                "found": True,
                "count": len(roots_result.roots),
                "roots": [str(root.uri) for root in roots_result.roots]
            }
        except Exception as e:
            debug_info["roots_check"] = {
                "found": False,
                "error": str(e)
            }
        
        # Get list of changed files
        files_result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        
        # Get diff statistics
        stat_result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        # Get the actual diff if requested
        diff_content = ""
        truncated = False
        if include_diff:
            diff_result = subprocess.run(
                ["git", "diff", f"{base_branch}...HEAD"],
                capture_output=True,
                text=True,
                cwd=cwd
            )
            diff_lines = diff_result.stdout.split('\n')
            
            # Check if we need to truncate
            if len(diff_lines) > max_diff_lines:
                diff_content = '\n'.join(diff_lines[:max_diff_lines])
                diff_content += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
                diff_content += "\n... Use max_diff_lines parameter to see more ..."
                truncated = True
            else:
                diff_content = diff_result.stdout
        
        # Get commit messages for context
        commits_result = subprocess.run(
            ["git", "log", "--oneline", f"{base_branch}..HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        analysis = {
            "base_branch": base_branch,
            "files_changed": files_result.stdout,
            "statistics": stat_result.stdout,
            "commits": commits_result.stdout,
            "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)",
            "truncated": truncated,
            "total_diff_lines": len(diff_lines) if include_diff else 0,
            "_debug": debug_info
        }
        
        return json.dumps(analysis, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Git error: {e.stderr}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
    templates = [
        {
            "filename": filename,
            "type": template_type,
            "content": (TEMPLATES_DIR / filename).read_text()
        }
        for filename, template_type in DEFAULT_TEMPLATES.items()
    ]
    
    return json.dumps(templates, indent=2)


@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Your analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    
    # Get available templates
    templates_response = await get_pr_templates()
    templates = json.loads(templates_response)
    
    # Find matching template
    template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
    selected_template = next(
        (t for t in templates if t["filename"] == template_file),
        templates[0]  # Default to first template if no match
    )
    
    suggestion = {
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"],
        "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
    }
    
    return json.dumps(suggestion, indent=2)


@mcp.tool()
async def get_recent_actions_events(limit: int = 10) -> str:
    """Get recent GitHub Actions events received via webhook.
    
    Args:
        limit: Maximum number of events to return (default: 10)
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps([])
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    # Return most recent events
    recent = events[-limit:]
    return json.dumps(recent, indent=2)


@mcp.tool()
async def get_workflow_status(conclusion: Optional[str] = None) -> str:
    """Get the current status of GitHub Actions workflows.
    
    Args:
        conclusion: Optional filter by conclusion (success, failure, cancelled, skipped, etc.)
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    if not events:
        return json.dumps({"message": "No GitHub Actions events received yet"})
    
    # Filter for workflow events
    workflow_events = [
        e for e in events 
        if e.get("workflow_run") is not None
    ]
    
    # Filter by conclusion if provided
    if conclusion:
        workflow_events = [
            e for e in workflow_events
            if e["workflow_run"].get("conclusion") == conclusion
        ]
    
    # Group by repository
    repositories = {}
    current_time = datetime.now(timezone.utc)
    
    for event in workflow_events:
        run = event["workflow_run"]
        repo = event["repository"]
        
        if repo not in repositories:
            repositories[repo] = {
                "repository": repo,
                "workflows": {},
                "latest_run": None,
                "total_runs": 0
            }
        
        repositories[repo]["total_runs"] += 1
        
        # Track latest run per workflow within repository
        workflow_name = run["name"]
        if workflow_name not in repositories[repo]["workflows"]:
            repositories[repo]["workflows"][workflow_name] = []
        
        # Calculate time since last run
        updated_at = run["updated_at"]
        if updated_at:
            try:
                run_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                time_diff = current_time - run_time
                time_since = {
                    "days": time_diff.days,
                    "hours": time_diff.seconds // 3600,
                    "minutes": (time_diff.seconds % 3600) // 60,
                    "total_seconds": time_diff.total_seconds()
                }
            except:
                time_since = {"error": "Could not parse timestamp"}
        else:
            time_since = {"error": "No timestamp available"}
        
        workflow_info = {
            "name": workflow_name,
            "status": run["status"],
            "conclusion": run.get("conclusion"),
            "run_number": run["run_number"],
            "updated_at": updated_at,
            "time_since_run": time_since,
            "html_url": run["html_url"]
        }
        
        repositories[repo]["workflows"][workflow_name].append(workflow_info)
        
        # Update latest run for repository
        if (repositories[repo]["latest_run"] is None or 
            updated_at > repositories[repo]["latest_run"]["updated_at"]):
            repositories[repo]["latest_run"] = workflow_info
    
    # Convert workflows dict to list and sort by most recent
    for repo_data in repositories.values():
        for workflow_name in repo_data["workflows"]:
            repo_data["workflows"][workflow_name].sort(
                key=lambda x: x["updated_at"], 
                reverse=True
            )
    
    # Create summary
    summary = {
        "total_repositories": len(repositories),
        "filter_applied": f"conclusion={conclusion}" if conclusion else "none",
        "generated_at": current_time.isoformat(),
        "repositories": list(repositories.values())
    }
    
    return json.dumps(summary, indent=2)


@mcp.tool()
async def get_unseen_events(mark_as_seen: bool = False) -> str:
    """Get events that haven't been processed yet and optionally mark them as seen.
    
    Args:
        mark_as_seen: If True, mark returned events as seen (default: False)
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    # Read or initialize state
    seen_events = set()
    if EVENTS_STATE_FILE.exists():
        with open(EVENTS_STATE_FILE, 'r') as f:
            state = json.load(f)
            seen_events = set(state.get("seen_event_ids", []))
    
    # Find unseen events (using timestamp + event_type + repository as unique ID)
    unseen_events = []
    new_seen_ids = set()
    
    for event in events:
        event_id = f"{event['timestamp']}:{event['event_type']}:{event['repository']}"
        if event_id not in seen_events:
            unseen_events.append({
                **event,
                "event_id": event_id
            })
            new_seen_ids.add(event_id)
    
    # Mark as seen if requested
    if mark_as_seen and unseen_events:
        seen_events.update(new_seen_ids)
        state = {
            "seen_event_ids": list(seen_events),
            "last_processed": datetime.now(timezone.utc).isoformat()
        }
        with open(EVENTS_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    result = {
        "unseen_count": len(unseen_events),
        "events": unseen_events,
        "marked_as_seen": mark_as_seen
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_new_failures(since_hours: int = 24) -> str:
    """Identify new workflow failures that need attention.
    
    Args:
        since_hours: Look for failures within the last N hours (default: 24)
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    # Filter for workflow failures within time window
    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=since_hours)
    
    failures = []
    for event in events:
        if event.get("workflow_run") and event["workflow_run"].get("conclusion") == "failure":
            event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
            if event_time >= cutoff_time:
                failures.append(event)
    
    # Group by repository and workflow
    failure_groups = {}
    for failure in failures:
        run = failure["workflow_run"]
        repo = failure["repository"]
        workflow_name = run["name"]
        
        key = f"{repo}:{workflow_name}"
        if key not in failure_groups:
            failure_groups[key] = {
                "repository": repo,
                "workflow_name": workflow_name,
                "failure_count": 0,
                "first_failure": failure["timestamp"],
                "latest_failure": failure["timestamp"],
                "failures": []
            }
        
        failure_groups[key]["failure_count"] += 1
        failure_groups[key]["failures"].append({
            "timestamp": failure["timestamp"],
            "run_number": run["run_number"],
            "html_url": run["html_url"],
            "sender": failure["sender"]
        })
        
        # Update latest failure time
        if failure["timestamp"] > failure_groups[key]["latest_failure"]:
            failure_groups[key]["latest_failure"] = failure["timestamp"]
    
    # Sort by failure count (most failures first)
    sorted_failures = sorted(failure_groups.values(), key=lambda x: x["failure_count"], reverse=True)
    
    result = {
        "time_window_hours": since_hours,
        "total_failure_groups": len(sorted_failures),
        "total_individual_failures": len(failures),
        "failure_groups": sorted_failures
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def suggest_team_notification(repository: str, workflow_name: str, failure_type: str = "general") -> str:
    """Suggest which team member to notify based on repository and failure type.
    
    Args:
        repository: Repository name (e.g., "user/repo")
        workflow_name: Name of the failing workflow
        failure_type: Type of failure (general, frontend, backend, deployment, security)
    """
    # Read team configuration
    team_config = {}
    if TEAM_CONFIG_FILE.exists():
        with open(TEAM_CONFIG_FILE, 'r') as f:
            team_config = json.load(f)
    
    # Default team mapping structure
    default_config = {
        "repositories": {},
        "expertise": {
            "frontend": ["frontend-lead"],
            "backend": ["backend-lead"],
            "deployment": ["devops-lead"],
            "security": ["security-lead"],
            "general": ["tech-lead"]
        },
        "on_call": {
            "primary": "on-call-primary",
            "secondary": "on-call-secondary"
        }
    }
    
    # Merge with existing config
    config = {**default_config, **team_config}
    
    suggestions = []
    
    # 1. Check repository-specific owners
    if repository in config.get("repositories", {}):
        repo_owners = config["repositories"][repository]
        suggestions.extend([{
            "type": "repository_owner",
            "person": person,
            "reason": f"Repository owner for {repository}"
        } for person in repo_owners])
    
    # 2. Check expertise-based routing
    if failure_type in config.get("expertise", {}):
        experts = config["expertise"][failure_type]
        suggestions.extend([{
            "type": "expertise",
            "person": person,
            "reason": f"Expert in {failure_type} issues"
        } for person in experts])
    
    # 3. Add on-call rotation
    if config.get("on_call", {}).get("primary"):
        suggestions.append({
            "type": "on_call_primary",
            "person": config["on_call"]["primary"],
            "reason": "Primary on-call engineer"
        })
    
    if config.get("on_call", {}).get("secondary"):
        suggestions.append({
            "type": "on_call_secondary",
            "person": config["on_call"]["secondary"],
            "reason": "Secondary on-call engineer"
        })
    
    # 4. Workflow-specific suggestions
    workflow_suggestions = []
    if "test" in workflow_name.lower():
        workflow_suggestions.append("QA team should be notified for test failures")
    elif "deploy" in workflow_name.lower():
        workflow_suggestions.append("DevOps team should be notified for deployment failures")
    elif "security" in workflow_name.lower():
        workflow_suggestions.append("Security team should be notified for security check failures")
    
    result = {
        "repository": repository,
        "workflow_name": workflow_name,
        "failure_type": failure_type,
        "notification_suggestions": suggestions,
        "workflow_specific_notes": workflow_suggestions,
        "config_file_location": str(TEAM_CONFIG_FILE),
        "config_exists": TEAM_CONFIG_FILE.exists()
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def mark_events_as_seen(event_ids: list = None) -> str:
    """Mark specific events as seen to prevent them from appearing in unseen events.
    
    Args:
        event_ids: List of event IDs to mark as seen (format: "timestamp:event_type:repository")
    """
    if not event_ids:
        return json.dumps({"error": "No event IDs provided"})
    
    # Read or initialize state
    seen_events = set()
    if EVENTS_STATE_FILE.exists():
        with open(EVENTS_STATE_FILE, 'r') as f:
            state = json.load(f)
            seen_events = set(state.get("seen_event_ids", []))
    
    # Add new seen events
    seen_events.update(event_ids)
    
    # Save state
    state = {
        "seen_event_ids": list(seen_events),
        "last_processed": datetime.now(timezone.utc).isoformat(),
        "manually_marked_count": len(event_ids)
    }
    
    with open(EVENTS_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    result = {
        "marked_as_seen": len(event_ids),
        "total_seen_events": len(seen_events),
        "event_ids_marked": event_ids
    }
    
    return json.dumps(result, indent=2)

# MCP Tool for Slack Notification

@mcp.tool()
async def send_slack_notification(message: str) -> str:
    """Send a formatted notification to the team Slack channel.
    
    Args:
        message: The message to send to Slack (supports Slack markdown)
        
    IMPORTANT: For CI failures, use format_ci_failure_alert prompt first!
    IMPORTANT: For deployments, use format_ci_success_summary prompt first!
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return "Error: SLACK_WEBHOOK_URL environment variable not set"
    
    try:
        # Prepare the payload with proper Slack formatting
        payload = {
            "text": message,
            "mrkdwn": True
        }
        
        # Send POST request to Slack webhook
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return "✅ Message sent successfully to Slack"
        else:
            return f"❌ Failed to send message. Status: {response.status_code}, Response: {response.text}"
        
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Check your internet connection and try again."
    except requests.exceptions.ConnectionError:
        return "❌ Connection error. Check your internet connection and webhook URL."
    except Exception as e:
        return f"❌ Error sending message: {str(e)}"


# MCP Prompts

@mcp.prompt()
async def analyze_ci_results():
    """Analyze recent CI/CD results and provide insights."""
    return """Please analyze the recent CI/CD results from GitHub Actions:

1. First, call get_recent_actions_events() to fetch the latest CI/CD events
2. Then call get_workflow_status() to check current workflow states
3. Identify any failures or issues that need attention
4. Provide actionable next steps based on the results

Format your response as:
## CI/CD Status Summary
- **Overall Health**: [Good/Warning/Critical]
- **Failed Workflows**: [List any failures with links]
- **Successful Workflows**: [List recent successes]
- **Recommendations**: [Specific actions to take]
- **Trends**: [Any patterns you notice]"""


@mcp.prompt()
async def create_deployment_summary():
    """Generate a deployment summary for team communication."""
    return """Create a deployment summary for team communication:

1. Check workflow status with get_workflow_status()
2. Look specifically for deployment-related workflows
3. Note the deployment outcome, timing, and any issues

Format as a concise message suitable for Slack:

🚀 **Deployment Update**
- **Status**: [✅ Success / ❌ Failed / ⏳ In Progress]
- **Environment**: [Production/Staging/Dev]
- **Version/Commit**: [If available from workflow data]
- **Duration**: [If available]
- **Key Changes**: [Brief summary if available]
- **Issues**: [Any problems encountered]
- **Next Steps**: [Required actions if failed]

Keep it brief but informative for team awareness."""


@mcp.prompt()
async def generate_pr_status_report():
    """Generate a comprehensive PR status report including CI/CD results."""
    return """Generate a comprehensive PR status report:

1. Use analyze_file_changes() to understand what changed
2. Use get_workflow_status() to check CI/CD status
3. Use suggest_template() to recommend the appropriate PR template
4. Combine all information into a cohesive report

Create a detailed report with:

## 📋 PR Status Report

### 📝 Code Changes
- **Files Modified**: [Count by type - .py, .js, etc.]
- **Change Type**: [Feature/Bug/Refactor/etc.]
- **Impact Assessment**: [High/Medium/Low with reasoning]
- **Key Changes**: [Bullet points of main modifications]

### 🔄 CI/CD Status
- **All Checks**: [✅ Passing / ❌ Failing / ⏳ Running]
- **Test Results**: [Pass rate, failed tests if any]
- **Build Status**: [Success/Failed with details]
- **Code Quality**: [Linting, coverage if available]

### 📌 Recommendations
- **PR Template**: [Suggested template and why]
- **Next Steps**: [What needs to happen before merge]
- **Reviewers**: [Suggested reviewers based on files changed]

### ⚠️ Risks & Considerations
- [Any deployment risks]
- [Breaking changes]
- [Dependencies affected]"""


@mcp.prompt()
async def troubleshoot_workflow_failure():
    """Help troubleshoot a failing GitHub Actions workflow."""
    return """Help troubleshoot failing GitHub Actions workflows:

1. Use get_recent_actions_events() to find recent failures
2. Use get_workflow_status() to see which workflows are failing
3. Analyze the failure patterns and timing
4. Provide systematic troubleshooting steps

Structure your response as:

## 🔧 Workflow Troubleshooting Guide

### ❌ Failed Workflow Details
- **Workflow Name**: [Name of failing workflow]
- **Failure Type**: [Test/Build/Deploy/Lint]
- **First Failed**: [When did it start failing]
- **Failure Rate**: [Intermittent or consistent]

### 🔍 Diagnostic Information
- **Error Patterns**: [Common error messages or symptoms]
- **Recent Changes**: [What changed before failures started]
- **Dependencies**: [External services or resources involved]

### 💡 Possible Causes (ordered by likelihood)
1. **[Most Likely]**: [Description and why]
2. **[Likely]**: [Description and why]
3. **[Possible]**: [Description and why]

### ✅ Suggested Fixes
**Immediate Actions:**
- [ ] [Quick fix to try first]
- [ ] [Second quick fix]

**Investigation Steps:**
- [ ] [How to gather more info]
- [ ] [Logs or data to check]

**Long-term Solutions:**
- [ ] [Preventive measure]
- [ ] [Process improvement]

### 📚 Resources
- [Relevant documentation links]
- [Similar issues or solutions]"""

# Additional MCP Prompt for Mocdule 2 (Excercise 1)

@mcp.prompt()
async def review_pull_request() -> str:
    """
    Provide a structured PR review summary combining code changes and CI/CD status.
    """
    # Get recent code changes
    changes_summary = await analyze_file_changes()
    
    # Get workflow status
    workflow_status = await get_workflow_status()
    
    return f"""
# 🧠 PR Review Assistant

## 🔍 Code Changes Summary
```json
{changes_summary}
```

## 🔄 CI/CD Status  
```json
{workflow_status}
```

## 📋 Review Summary
Based on the code changes and CI/CD status above, here's a comprehensive review:

### ✅ What's Working Well
- Code changes are properly tracked
- CI/CD pipeline integration is active

### ⚠️ Areas for Attention
- Review the specific changes and their impact
- Monitor workflow status for any failures

### 🎯 Next Steps
1. Review the code changes in detail
2. Ensure all CI/CD checks pass
3. Address any workflow failures if present
"""


@mcp.prompt()
async def incident_response_dashboard():
    """Generate a comprehensive incident response dashboard for new failures and required notifications."""
    return """Create a comprehensive incident response dashboard:

1. First, use get_unseen_events() to check for any new events since last check
2. Then use get_new_failures() to identify recent failures needing attention
3. For each failure group, use suggest_team_notification() to identify who to notify
4. Use get_workflow_status(conclusion="failure") to get current failure status
5. Mark critical events as seen using mark_events_as_seen() after processing

Generate this structured dashboard:

## 🚨 Incident Response Dashboard

### 📊 New Events Summary
- **Unseen Events**: [Count and summary]
- **New Failures**: [Count in last 24 hours]
- **Critical Repositories**: [Those with multiple failures]

### 🔥 Active Failures Requiring Action
For each failure group:
- **Repository**: [Name]
- **Workflow**: [Name]
- **Failure Count**: [Number of failures]
- **Duration**: [Time since first failure]
- **Recommended Notifications**: [Who to notify and why]
- **Action Required**: [Specific steps to take]

### 👥 Team Notification Plan
- **Immediate Notifications**: [People to notify right now]
- **Repository Owners**: [Specific repository maintainers]
- **Expertise-Based**: [Subject matter experts]
- **On-Call Escalation**: [If needed]

### 📈 Failure Trends
- **Most Failing Workflows**: [Top 3 by failure count]
- **Most Affected Repositories**: [Top 3 by failure frequency]
- **Escalation Needed**: [Repeated failures requiring management attention]

### ✅ Next Steps
1. [ ] Notify identified team members
2. [ ] Create incidents for critical failures
3. [ ] Mark events as seen once processed
4. [ ] Schedule follow-up if needed

Keep the dashboard concise but actionable - focus on what needs immediate attention."""


# MCP Prompts for Slack Notification

@mcp.prompt()
async def format_ci_failure_alert():
    """Create a Slack alert for CI/CD failures with rich formatting."""
    return """Format this GitHub Actions failure as a Slack message using ONLY Slack markdown syntax:

:rotating_light: *CI Failure Alert* :rotating_light:

A CI workflow has failed:
*Workflow*: workflow_name
*Branch*: branch_name
*Status*: Failed
*View Details*: <https://github.com/test/repo/actions/runs/123|View Logs>

Please check the logs and address any issues.

CRITICAL: Use EXACT Slack link format: <https://full-url|Link Text>
Examples:
- CORRECT: <https://github.com/user/repo|Repository>
- WRONG: [Repository](https://github.com/user/repo)
- WRONG: https://github.com/user/repo

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format without special characters
- :emoji_name: for emojis"""


@mcp.prompt()
async def format_ci_success_summary():
    """Create a Slack message celebrating successful deployments."""
    return """Format this successful GitHub Actions run as a Slack message using ONLY Slack markdown syntax:

:white_check_mark: *Deployment Successful* :white_check_mark:

Deployment completed successfully for [Repository Name]

*Changes:*
- Key feature or fix 1
- Key feature or fix 2

*Links:*
<https://github.com/user/repo|View Changes>

CRITICAL: Use EXACT Slack link format: <https://full-url|Link Text>
Examples:
- CORRECT: <https://github.com/user/repo|Repository>
- WRONG: [Repository](https://github.com/user/repo)
- WRONG: https://github.com/user/repo

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format with - or *
- :emoji_name: for emojis"""


if __name__ == "__main__":
    mcp.run()