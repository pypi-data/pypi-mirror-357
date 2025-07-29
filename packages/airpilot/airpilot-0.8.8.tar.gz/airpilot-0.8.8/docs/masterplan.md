# AirPilot Master Plan

## The Vision: Universal Intelligence Control Ecosystem

AirPilot is designed to be a universal intelligence control system that works across all environments, with seamless configuration inheritance and tool independence.

## Architecture Overview

### Configuration Hierarchy (CRITICAL)

**System Global**: `~/.airpilot` FILE (fallback/default configuration)
**Project Local**: `project/.airpilot` FILE (project-specific overrides)

**NEVER EVER**: `.airpilot` files inside `.air` directories - this violates fundamental separation of concerns.

### VSCode Extension Integration Strategy

**Current Behavior:**

- VSCode extension checks: Does `project/.airpilot` exist? Use it.
- If not: Falls back to `~/.airpilot` as system default
- This creates seamless inheritance: global → project overrides

**Future Enhancement:**

- VSCode extension will automatically look for `~/.airpilot` as system fallback
- Provides universal configuration management across all projects
- Enables system-wide intelligence control even without project-level config

## Implementation Phases

### Phase 1: Foundation (Current)

- [x] Create proper global/project config files with correct schemas
- [x] Establish `.airpilot` FILE + `.air/` DIRECTORY architecture
- [x] Implement basic CLI functionality with premium licensing
- [x] Ensure config schema compatibility with VSCode extension

### Phase 2: Python CLI Feature Parity

- [ ] Implement all VSCode extension functionality in Python CLI
- [ ] Real-time vendor synchronization (Claude, Cursor, Cline, GitHub Copilot, etc.)
- [ ] File watching and automatic sync
- [ ] Advanced configuration management
- [ ] Premium features: cloud sync, backup, advanced analytics

### Phase 3: TypeScript CLI Development

- [ ] Create exact replica of Python AirPilot in TypeScript
- [ ] Maintain 100% feature parity between Python and TypeScript versions
- [ ] Shared configuration schema and architecture
- [ ] Cross-platform compatibility and performance optimization

### Phase 4: Universal Ecosystem

- [ ] Python CLI becomes core intelligence engine
- [ ] TypeScript CLI provides alternative implementation
- [ ] VSCode extension becomes optional UI layer, not required dependency
- [ ] All tools work together seamlessly via shared config schema

## The Magic: Tool Independence

**System-Level Intelligence:**

- User installs Python CLI premium → Gets full sync functionality system-wide
- Works everywhere: terminal, IDE, scripts, automation
- No dependency on specific editors or extensions

**Seamless Integration:**

- VSCode extension enhances workflow but isn't required
- TypeScript CLI provides Node.js ecosystem integration
- All tools share the same configuration and intelligence patterns

**Universal Configuration:**

- `~/.airpilot` provides system defaults for all tools
- `project/.airpilot` allows project-specific customization
- Hierarchical inheritance ensures consistent behavior

## End State Vision

**Core Philosophy:**
Universal intelligence control that works everywhere, with any tool, in any environment.

**Primary Engine:**
Python CLI as the foundational intelligence layer with full feature set.

**Alternative Implementation:**
TypeScript CLI providing identical functionality for Node.js ecosystems.

**UI Layers:**
VSCode extension and other editor integrations as optional interfaces to the core engines.

**Configuration:**
Unified schema enabling seamless tool interoperability and user preference inheritance.

---

**CRITICAL ARCHITECTURE REMINDER:**

- `~/.airpilot` = AirPilot configuration FILE (never directory!)
- `~/.air/` = Air content DIRECTORY
- `project/.airpilot` = AirPilot configuration FILE (never directory!)
- `project/.air/` = Air content DIRECTORY
- These must NEVER be intertwined - separation of concerns is fundamental
