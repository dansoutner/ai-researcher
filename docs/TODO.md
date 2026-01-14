# TODO

## High Priority

### MCP Server Integration
- [ ] Integrate arXiv MCP server for paper search and retrieval
  - Server available at: https://glama.ai/mcp/servers/@lecigarevolant/arxiv-mcp-server-gpt
  - Initial setup completed in `mcp_servers/arxiv-mcp-server/`
  - Need: Integration with agent workflows

### Tool Enhancements
- [x] Implement line-editing patch tool
  - Purpose: Replace `write_file` with more surgical edits
  - Design:
    ```python
    @tool
    def edit_file(path: str, old_string: str, new_string: str) -> str:
        """Replace occurrences of old_string with new_string in a file."""
        # Safe read/replace implementation with validation
    ```
    - Benefits: More precise edits, better for large files
    - Possible improvements for future iterations:
      - [ ] Regex pattern support for more flexible matching
      - [ ] Line number-based editing (edit specific line ranges)
      - [ ] Preview mode (show what would change without applying)
      - [ ] Undo/rollback functionality
      - [ ] Batch editing (multiple edits in one call)
      - [ ] Diff output showing exact changes made


## Medium Priority

### Agent Comparison
- [ ] SMS spam classification benchmark across all agent versions
  - Compare agent v1, v2, and v3 performance
  - Metrics: accuracy, iterations, token usage, reliability
  - Goal: Quantify improvements

### Hierarchical Agent System
- [ ] Implement "researcher" meta-agent
  - Coordinates multiple specialized agents
  - Uses "coding" agent (v3) as sub-agent
  - Higher-level planning and research tasks

## Documentation
- [x] Refactor all markdown files for clarity
- [x] Create comprehensive feature documentation
- [x] Add architecture diagrams
- [x] Create documentation index

## Code Quality
- [x] Replace print statements with proper logging in agent_v3
  - Implemented color-coded logging system
  - Custom log levels: DEBUG (cyan), TOOL (blue), INFO (green), USER (magenta), WARNING (yellow), ERROR (red)
  - 27 print statements replaced across 5 files
  - Comprehensive documentation created
  - Demo scripts provided
  - 100% backward compatible

## Future Ideas

### Agent Enhancements
- [ ] Streaming output for long-running tasks
- [ ] Multi-agent collaboration patterns
- [ ] Custom tool plugin system

### Observability
- [ ] LangSmith integration for tracing
- [ ] Performance metrics dashboard
- [ ] Execution replay capability

### Testing
- [ ] Integration tests for common workflows
- [ ] Tool execution test coverage
- [ ] Failure recovery scenario tests

