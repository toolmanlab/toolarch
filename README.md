# ToolArch

**Architecture intelligence for your codebase.**

> Part of the [toolmanlab](https://github.com/toolmanlab) ecosystem — built by engineers who actually maintain production code.

## What is ToolArch?

ToolArch is a code architecture analysis engine that helps you monitor structural health as your codebase grows. It parses source code into a dependency graph, computes architecture metrics, and surfaces problems before they become irreversible.

**The problem:** AI coding agents (Claude Code, Cursor, etc.) accelerate development speed, but they don't watch your architecture. Code grows fast, dependencies tangle, layers leak, and by the time you notice, refactoring costs more than rewriting.

**The solution:** Run `toolarch analyze` on your project and get instant visibility into dependency cycles, layer violations, coupling hotspots, and complexity trends — before your codebase crosses the point of no return.

## Key Features

- **Dependency graph construction** — Tree-sitter AST parsing → module/function-level call graph
- **Cycle detection** — Tarjan's SCC algorithm to find circular dependencies
- **Layer compliance** — Define architectural layers, detect cross-layer violations
- **Complexity heatmap** — Identify bloated modules and functions
- **Coupling metrics** — Robert C. Martin's instability/abstractness indicators
- **CLI-first** — `toolarch analyze <path>` → terminal report + HTML export
- **Graph Adapter architecture** — Pluggable input layer: built-in Tree-sitter parser, or import from GitNexus / code-review-graph / code-graph-rag

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **MVP** | CLI analyzer for Python projects. Dependency graph, cycle detection, layer compliance, complexity metrics. Terminal + HTML report. | 🔨 Building |
| **V1** | MCP Server for AI agents. Architecture-aware code navigation for Claude Code / Cursor. | 📋 Planned |
| **V2** | Multi-agent analysis (LangGraph). AI readability scoring. React visualization dashboard. Java support. | 📋 Planned |

## Architecture

```
┌─────────────────────────────────────────────┐
│              ToolArch Core                   │
│                                              │
│  Analyzers        Metrics        Reporters   │
│  ┌──────────┐    ┌──────────┐   ┌─────────┐ │
│  │ Cycle    │    │ Martin   │   │ Terminal │ │
│  │ Layer    │    │ Coupling │   │ HTML     │ │
│  │ Complexity│   │ Cohesion │   │ JSON     │ │
│  └──────────┘    └──────────┘   └─────────┘ │
├──────────── Graph Adapter ───────────────────┤
│  Standard interface: nodes, edges, call_graph │
├──────────────────────────────────────────────┤
│  Built-in         GitNexus      code-review  │
│  (Tree-sitter     adapter       -graph       │
│   + SQLite)       (planned)     adapter      │
└──────────────────────────────────────────────┘
```

The **Graph Adapter** layer decouples analysis from parsing. The built-in adapter (Tree-sitter + SQLite) works standalone with zero external dependencies. When you need richer graph capabilities, plug in an external code intelligence engine.

## Quick Start

```bash
# Install
pip install toolarch

# Analyze a Python project
toolarch analyze ~/projects/my-app

# Generate HTML report
toolarch analyze ~/projects/my-app --format html --output report.html
```

## Why not just use SonarQube / CodeScene / GitNexus?

- **SonarQube / CodeScene** — Rule-based code quality. Great at line-level issues, but don't model architecture (dependency graphs, layer compliance, coupling metrics across modules).
- **GitNexus / code-review-graph** — Code intelligence for AI agents. Excellent at blast-radius analysis and token reduction, but no architecture governance layer (no cycle detection, no layer rules, no Martin metrics).
- **ToolArch** — Architecture-level analysis. Sits *above* code intelligence tools, consuming their graph data via adapters and providing structural governance that none of them offer.

## Background

Born from real pain: maintaining Java microservices at scale (deep dependency chains, hidden coupling, architecture drift). Started as a custom tool, then discovered the open-source code intelligence ecosystem (GitNexus, code-review-graph, code-graph-rag) had solved the parsing layer. Instead of reinventing the wheel, ToolArch focuses on what they don't do — **architecture governance**.

## Tech Stack

- **Python** + **FastAPI** (MCP server, V1)
- **Tree-sitter** (AST parsing)
- **SQLite** (lightweight graph storage)
- **LangGraph** (multi-agent analysis, V2)
- **React** + **TypeScript** (visualization dashboard, V2)

## Related Projects

- [ToolRef](https://github.com/toolmanlab/toolref) — Domain knowledge RAG engine for AI agents
- [ToolOps](https://github.com/toolmanlab/toolops) — Pluggable AI app infrastructure toolkit

## License

MIT
