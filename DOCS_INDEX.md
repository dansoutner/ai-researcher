# Documentation Index

Complete guide to AI Researcher documentation.

## Quick Start

**New to the project?** Start here:
1. [Project README](readme.md) - Project overview and installation
2. [Agent v3 README](agent_v3_claude/README.md) - Recommended agent guide
3. [Quick Reference](QUICK_REFERENCE.md) - Fast lookup for common tasks

## Core Documentation

### Project Overview
- **[readme.md](readme.md)** - Main project documentation
  - All agent versions overview
  - Installation instructions
  - Project structure
  - Testing guide

### Agent v3 Claude (Recommended)
- **[agent_v3_claude/README.md](agent_v3_claude/README.md)** - Complete user guide
  - Usage examples
  - Configuration options
  - Available tools
  - Workflow details

- **[agent_v3_claude/ARCHITECTURE.md](agent_v3_claude/ARCHITECTURE.md)** - Technical architecture
  - Component design
  - Data flow
  - Design patterns
  - Extension points

- **[agent_v3_claude/REFACTORING_SUMMARY.md](agent_v3_claude/REFACTORING_SUMMARY.md)** - Evolution history
  - Module breakdown
  - Improvements made
  - Before/after comparison

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
│   └── AGENT_V3_TOOLS_INTEGRATION.md (tools feature)
│
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

