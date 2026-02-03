# Documentation Index

Complete guide to AI Researcher documentation.

## Quick Start (Choose Your Speed)

**New to the project?** Pick your preferred entry point:

1. **[Project README](../README.md)** - Project overview and 5-minute setup
2. **[Getting Started](GETTING_STARTED.md)** - Comprehensive setup and basic usage (recommended)
3. **[Advanced Configuration](ADVANCED.md)** - Complex usage patterns and customization

## Core Documentation

### User Guides
- **[Getting Started](GETTING_STARTED.md)** - Primary user guide
  - 5-minute setup
  - Basic usage patterns
  - Common tasks
  - Quick troubleshooting

- **[Advanced Configuration](ADVANCED.md)** - Advanced usage
  - Multiple installation options
  - Custom LLM providers
  - Complex usage patterns
  - Performance optimization

- **[Quick Reference](QUICK_REFERENCE.md)** - Fast lookup
  - Common commands
  - API examples
  - Troubleshooting shortcuts

### Technical Documentation
- **[agent_v3_claude/README.md](../ai_researcher/agent_v3_claude/README.md)** - Complete technical guide
  - All available tools
  - Configuration options
  - Detailed usage examples

- **[agent_v3_claude/ARCHITECTURE.md](../ai_researcher/agent_v3_claude/ARCHITECTURE.md)** - System architecture
  - Component design
  - Data flow
  - Design patterns
  - Extension points

### Specialized Guides  
- **[MCP All Agents Guide](MCP_ALL_AGENTS_GUIDE.md)** - MCP integration
- **[Features](FEATURES.md)** - Comprehensive feature overview
- **[TODO](TODO.md)** - Development roadmap

### Utilities
- **[LOGGING_QUICK_REF.txt](LOGGING_QUICK_REF.txt)** - Logging system reference

## Archived Documentation

Historical and technical implementation documents are stored in the `archive/` directory:
- Implementation details and changelogs
- Bug fix summaries
- Legacy integration guides
- Development notes

---

**Need help?** Start with [Getting Started](GETTING_STARTED.md) for most use cases.


## Feature Documentation

### Comprehensive Guide
- **[FEATURES.md](FEATURES.md)** - All features in one place
  - Executor structured output
  - Routing logic
  - Tools integration
  - Architecture refactoring

### Individual Feature Guides

#### Executor Structured Output
- **[EXECUTOR_OUTPUT_SUMMARY.md](EXECUTOR_OUTPUT_SUMMARY.md)** - Implementation summary
  - ExecutorOutput TypedDict
  - Automatic retry logic
  - Benefits and usage

- **[EXECUTOR_WORKFLOW_DIAGRAM.md](EXECUTOR_WORKFLOW_DIAGRAM.md)** - Visual workflow
  - Before/after comparison
  - Code flow examples
  - Benefits summary

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast lookup guide
  - Quick syntax examples
  - Code locations
  - Common patterns

#### Routing Logic
- **[ROUTING_FIX_SUMMARY.md](ROUTING_FIX_SUMMARY.md)** - Routing implementation
  - Verdict handling
  - Complete workflow
  - Example scenarios

#### Tools
- **[AGENT_V3_TOOLS_INTEGRATION.md](AGENT_V3_TOOLS_INTEGRATION.md)** - Tools guide
  - All 26 tools documented
  - Safety features
  - Usage examples

#### MCP Integration
- **[HUGGINGFACE_MCP_INTEGRATION.md](HUGGINGFACE_MCP_INTEGRATION.md)** - HuggingFace MCP server integration
  - Configuration details
  - Usage examples
  - HTTP MCP server support
  - Architecture changes

- **[HUGGINGFACE_MCP_QUICK_REF.md](HUGGINGFACE_MCP_QUICK_REF.md)** - Quick reference
  - Quick start examples
  - API exports
  - Usage patterns

- **[HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md](HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md)** - Implementation summary
  - All changes made
  - New classes and functions
  - Testing instructions

- **[HUGGINGFACE_MCP_INTEGRATION_CHANGELOG.md](HUGGINGFACE_MCP_INTEGRATION_CHANGELOG.md)** - Complete changelog
  - Files modified/created
  - Detailed changes
  - Statistics

## By Task

### I want to...

**Use the agent**
→ [readme.md](readme.md) → [agent_v3_claude/README.md](agent_v3_claude/README.md)

**Understand the architecture**
→ [agent_v3_claude/ARCHITECTURE.md](agent_v3_claude/ARCHITECTURE.md)

**Learn about specific features**
→ [FEATURES.md](FEATURES.md)

**Quick lookup for executor output**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**See visual workflows**
→ [EXECUTOR_WORKFLOW_DIAGRAM.md](EXECUTOR_WORKFLOW_DIAGRAM.md)

**Understand routing logic**
→ [ROUTING_FIX_SUMMARY.md](ROUTING_FIX_SUMMARY.md)

**Learn about available tools**
→ [AGENT_V3_TOOLS_INTEGRATION.md](AGENT_V3_TOOLS_INTEGRATION.md)

**Use MCP tools with any agent**
→ [MCP_ALL_AGENTS_GUIDE.md](MCP_ALL_AGENTS_GUIDE.md)

**Integrate HuggingFace MCP server**
→ [HUGGINGFACE_MCP_INTEGRATION.md](HUGGINGFACE_MCP_INTEGRATION.md) → [HUGGINGFACE_MCP_QUICK_REF.md](HUGGINGFACE_MCP_QUICK_REF.md)

**Understand the refactoring**
→ [agent_v3_claude/REFACTORING_SUMMARY.md](agent_v3_claude/REFACTORING_SUMMARY.md)

**Set up arXiv MCP server**
→ [mcp_servers/arxiv-mcp-server/README.md](mcp_servers/arxiv-mcp-server/README.md)

## By Audience

### End Users
Priority reading:
1. [readme.md](readme.md) - Project overview
2. [agent_v3_claude/README.md](agent_v3_claude/README.md) - Usage guide
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common tasks

### Developers
Priority reading:
1. [agent_v3_claude/ARCHITECTURE.md](agent_v3_claude/ARCHITECTURE.md) - System design
2. [FEATURES.md](FEATURES.md) - Feature implementations
3. [agent_v3_claude/REFACTORING_SUMMARY.md](agent_v3_claude/REFACTORING_SUMMARY.md) - Code organization

### Researchers
Priority reading:
1. [agent_v3_claude/ARCHITECTURE.md](agent_v3_claude/ARCHITECTURE.md) - Design patterns
2. [EXECUTOR_WORKFLOW_DIAGRAM.md](EXECUTOR_WORKFLOW_DIAGRAM.md) - Workflow comparison
3. [FEATURES.md](FEATURES.md) - Feature analysis

## Document Relationships

```
readme.md (project overview)
├── agent_v3_claude/README.md (v3 guide)
│   ├── agent_v3_claude/ARCHITECTURE.md (technical details)
│   └── agent_v3_claude/REFACTORING_SUMMARY.md (history)
│
├── FEATURES.md (all features)
│   ├── EXECUTOR_OUTPUT_SUMMARY.md (executor feature)
│   │   ├── EXECUTOR_WORKFLOW_DIAGRAM.md (visual)
│   │   └── QUICK_REFERENCE.md (quick lookup)
│   ├── ROUTING_FIX_SUMMARY.md (routing feature)
│   ├── AGENT_V3_TOOLS_INTEGRATION.md (tools feature)
│   └── HUGGINGFACE_MCP_INTEGRATION.md (HuggingFace MCP)
│       ├── HUGGINGFACE_MCP_QUICK_REF.md (quick reference)
│       ├── HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md (summary)
│       └── HUGGINGFACE_MCP_INTEGRATION_CHANGELOG.md (changelog)
│
├── MCP_ALL_AGENTS_GUIDE.md (MCP usage guide)
└── mcp_servers/arxiv-mcp-server/README.md (MCP server)
```

## Maintenance Notes

### Document Purpose

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| readme.md | Project entry point | On major changes |
| agent_v3_claude/README.md | v3 user guide | On API changes |
| agent_v3_claude/ARCHITECTURE.md | Technical reference | On architecture changes |
| FEATURES.md | Feature index | When features added |
| QUICK_REFERENCE.md | Quick syntax lookup | Rarely (stable API) |
| *_SUMMARY.md | Implementation details | On feature completion |

### Cross-References

All documents cross-reference related documentation using relative links. When moving files, update links accordingly.

### Versioning

- Agent v1: Legacy, minimal docs
- Agent v2: LangGraph + Together, see readme.md
- Agent v3: Production-ready, comprehensive docs (this index)

## Contributing

When adding new features:
1. Update [FEATURES.md](FEATURES.md) with feature overview
2. Create detailed `FEATURE_NAME_SUMMARY.md` if needed
3. Update [agent_v3_claude/README.md](agent_v3_claude/README.md) if API changes
4. Update [agent_v3_claude/ARCHITECTURE.md](agent_v3_claude/ARCHITECTURE.md) if architecture changes
5. Add entry to this index

