  Summary of your changes:
  - Complete implementation of all three MCP tools
  - Enhanced git analysis with proper subprocess handling
  - Robust error handling for git operations
  - Working directory detection through MCP session roots
  - Security template support added to the template system
  - Diff truncation to handle large outputs
  - Comprehensive debugging information

  Here's the recommended PR template filled out for your changes:

  ## New Feature

  ### Description
  Complete implementation of MCP server tools for PR template analysis and
  suggestions, including git change analysis, template retrieval, and intelligent
  template recommendations.

  ### Motivation
  Transform the starter code into a fully functional MCP server that can analyze git
  repositories, suggest appropriate PR templates, and help developers create better
  pull requests.

  ### Implementation
  - Implemented `analyze_file_changes()` with git subprocess integration
  - Added `get_pr_templates()` for template retrieval from filesystem
  - Built `suggest_template()` with intelligent mapping logic
  - Added comprehensive error handling and working directory detection
  - Expanded template support to include security templates

  ### Testing
  - [x] Existing unit tests should pass
  - [ ] Test with actual git repositories
  - [ ] Verify MCP integration with Claude Code

  ### Documentation
  - [x] Added comprehensive CLAUDE.md file
  - [ ] Updated usage examples based on implementation

  ### Breaking Changes
  None - maintains backward compatibility with existing API
