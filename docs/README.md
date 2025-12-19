# AskAI CLI - Documentation

This directory contains comprehensive architecture, technical, and user documentation for the AskAI CLI project.

## 📚 Documentation Index

### 🏗️ Architecture & Design

#### [SOFTWARE_ARCHITECTURE.md](SOFTWARE_ARCHITECTURE.md)
**High-level system architecture and design documentation**

Comprehensive overview of the AskAI CLI system architecture:
- System overview and key features
- Architecture layers and component responsibilities
- Design patterns and principles
- Configuration management
- Security considerations
- Performance and scalability aspects
- Extension points for customization

**Target Audience**: Architects, technical leads, senior developers

#### [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
**Detailed technical implementation guide**

Deep dive into technical implementation details:
- Code organization and module structure
- Class hierarchies and relationships
- API interfaces and data models (CLI and REST API)
- Configuration schemas
- Testing architecture
- Deployment structure and runtime dependencies

**Target Audience**: Developers, DevOps engineers, technical maintainers

#### [TUI_ARCHITECTURE.md](TUI_ARCHITECTURE.md)
**Terminal User Interface (TUI) architecture**

Technical documentation for the TUI implementation:
- TUI component architecture
- Textual framework integration
- Widget hierarchy and design
- State management
- Event handling

**Target Audience**: UI developers, TUI contributors

### 🎨 Design & UX

#### [TUI_DESIGN_GUIDE.md](TUI_DESIGN_GUIDE.md)
**TUI design guidelines and patterns**

Design principles and guidelines for the terminal UI:
- Visual design standards
- Widget styling and theming
- User interaction patterns
- Accessibility considerations

**Target Audience**: UI/UX designers, frontend developers

### 📖 User Documentation

#### [USER_MANUAL.md](USER_MANUAL.md)
**Complete user guide for CLI interface**

Comprehensive guide for end users:
- Installation and setup
- Command-line interface usage
- Pattern system overview
- Configuration options
- Examples and tutorials

**Target Audience**: End users, CLI users

#### [TUI_USER_MANUAL.md](TUI_USER_MANUAL.md)
**Terminal UI user guide**

Guide for using the terminal user interface:
- TUI features and navigation
- Interactive mode usage
- Tips and keyboard shortcuts

**Target Audience**: End users preferring interactive UI

### 🔌 API Documentation

#### [API_IMPLEMENTATION.md](API_IMPLEMENTATION.md)
**REST API implementation details**

Technical documentation for the REST API:
- API endpoints and routes
- Request/response formats
- Authentication and security
- Error handling

**Target Audience**: API developers, integrators

#### [PATTERN_EXECUTION_API.md](PATTERN_EXECUTION_API.md)
**Pattern execution via REST API**

Detailed guide for executing patterns through the API:
- Pattern execution endpoints
- Input/output formats
- File upload handling
- Integration examples

**Target Audience**: API users, automation developers

### 🧪 Testing Documentation

#### [TESTING_README.md](TESTING_README.md)
**Overview of test suite and testing strategy**

Testing philosophy and organization:
- Test structure overview
- Running tests
- Test categories (unit, integration)
- Coverage reports

**Target Audience**: Developers, QA engineers

#### [TESTING_SETUP_GUIDE.md](TESTING_SETUP_GUIDE.md)
**Step-by-step testing environment setup**

Guide for setting up the testing environment:
- Dependencies and prerequisites
- Test configuration
- Running specific test suites
- Troubleshooting

**Target Audience**: New contributors, developers

#### [TEST_STRUCTURE.md](TEST_STRUCTURE.md)
**Detailed test organization and conventions**

In-depth documentation of test structure:
- Directory organization
- Naming conventions
- Test patterns and best practices
- Mocking strategies

**Target Audience**: Test developers, contributors

### 🔧 DevOps & CI/CD

#### [CI_PIPELINE.md](CI_PIPELINE.md)
**Continuous Integration pipeline documentation**

CI/CD workflow and configuration:
- GitHub Actions workflows
- Test automation
- Code quality checks
- Security scanning
- Deployment process

**Target Audience**: DevOps engineers, maintainers

#### [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)
**Branch protection rules and workflow**

Git workflow and branch management:
- Branch protection rules
- Pull request requirements
- Review process
- Merge strategies

**Target Audience**: Maintainers, contributors

#### [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md)
**Version numbering and release process**

Semantic versioning and release workflow:
- Version numbering scheme
- Release process
- Changelog management
- Version bumping automation

**Target Audience**: Maintainers, release managers

### 🔒 Security Documentation

#### [github/CODEQL_README.md](github/CODEQL_README.md)
**CodeQL security analysis overview**

Overview of CodeQL security scanning:
- What CodeQL checks
- Expected warnings
- Security model for CLI tools

**Target Audience**: Security reviewers, maintainers

#### [github/CODEQL_FALSE_POSITIVES.md](github/CODEQL_FALSE_POSITIVES.md)
**Documentation of known false positive security warnings**

Detailed explanation of CodeQL false positives:
- Path injection warnings (7 alerts)
- Why they're safe for CLI tools
- Security measures in place
- Validation and canonicalization

**Target Audience**: Security reviewers, code reviewers

#### [github/CODEQL_DISMISSAL_TEMPLATE.md](github/CODEQL_DISMISSAL_TEMPLATE.md)
**Template for dismissing CodeQL alerts on GitHub**

Copy-paste templates for dismissing false positive alerts:
- Standard dismissal comment
- Short version for quick dismissals

**Target Audience**: Maintainers, PR reviewers

### 📊 Visual Documentation

#### [drawings/README.md](drawings/README.md)
**Architecture diagrams and visual documentation**

Guide to D2 diagrams in the drawings folder:
- How to generate diagrams
- Diagram descriptions
- Tools and setup

**Target Audience**: Architects, technical documentation writers

---

## 🚀 Quick Reference

### Key Components

| Component | Location | Description |
|-----------|----------|-------------|
| **Main Application** | `src/askai/main.py` | Entry point and orchestration |
| **CLI Interface** | `src/askai/presentation/cli/` | Command parsing and handling |
| **REST API Interface** | `src/askai/presentation/api/` | HTTP endpoints and Swagger documentation |
| **TUI Interface** | `src/askai/presentation/tui/` | Terminal UI components |
| **AI Services** | `src/askai/core/ai/` | AI model integration via OpenRouter |
| **Pattern System** | `src/askai/core/patterns/` | Template-based AI interactions |
| **Question Processing** | `src/askai/core/questions/` | Standalone question handling |
| **Output Processing** | `src/askai/output/` | Response formatting and file generation |
| **Chat Management** | `src/askai/core/chat/` | Persistent conversation sessions |
| **Configuration** | `src/askai/utils/` | YAML-based configuration system |

### Architecture Highlights

- ✅ **Layered Architecture**: Clear separation between presentation (CLI/API/TUI), application, service, and infrastructure layers
- ✅ **Multiple Interfaces**: Command-line, REST API, and Terminal UI with shared core logic
- ✅ **Pattern-Based Design**: Extensible template system for structured AI interactions
- ✅ **Multimodal Support**: Text, images, PDFs, and URLs as input
- ✅ **Flexible Output**: Console display, file generation, and command execution
- ✅ **Configuration-Driven**: YAML configuration with interactive setup wizard
- ✅ **Error Resilient**: Comprehensive error handling with graceful degradation

### Extension Points

- 🔧 **Custom Patterns**: Add new patterns in private patterns directory
- 🎨 **Display Formatters**: Implement new terminal and file display formats in `output/formatters/`
- 📝 **File Writers**: Add specialized writers for new file types in `output/writers/`
- ⚙️ **Content Processors**: Extend content processing capabilities in `output/processors/`
- 🤖 **AI Providers**: Extend for additional AI service providers
- 📥 **Input Processors**: Add support for new file types and content sources

## 📋 Project Overview

AskAI CLI is a sophisticated command-line interface application that provides AI-powered assistance through structured patterns and interactive conversations. The system integrates with multiple AI providers through the OpenRouter API and supports various input formats including text, images, PDFs, and URLs.

### Key Features

- 🎯 **Pattern-Based AI**: Structured templates for consistent AI interactions
- 💬 **Interactive Chat**: Persistent conversation sessions with context
- 🖥️ **Multiple Interfaces**: CLI, REST API, and Terminal UI
- 📸 **Multimodal Input**: Text, images, PDFs, URLs
- 📝 **Flexible Output**: Console, files, structured formats (JSON, Markdown, HTML)
- ⚙️ **Highly Configurable**: YAML-based configuration with interactive setup
- 🔒 **Secure**: Input validation, path sanitization, API key management

## 🔗 Quick Links

- 📖 [Main README](../README.md) - Setup instructions and usage examples
- 🐙 [GitHub Repository](https://github.com/ngroegli/askai-cli) - Source code
- 🐛 [Issues](https://github.com/ngroegli/askai-cli/issues) - Bug reports and feature requests
- 💡 [Discussions](https://github.com/ngroegli/askai-cli/discussions) - Questions and ideas

## 📐 Documentation Standards

### Visual Documentation

#### Diagram Conventions
- 🔵 **Blue tones**: Core application components
- 🟣 **Purple tones**: CLI and user interface components
- 🟠 **Orange tones**: AI and external service integration
- 🟢 **Green tones**: Data processing and transformation
- ⚫ **Gray tones**: Infrastructure and configuration
- 🔴 **Red tones**: Error handling and critical paths

#### Diagram Tools
- **D2**: Declarative diagramming language for architecture diagrams
- **Mermaid**: Flowcharts and sequence diagrams (where applicable)

### Code Documentation Standards

| Type | Requirement | Description |
|------|-------------|-------------|
| **Docstrings** | Required | All public modules, classes, and functions must have docstrings |
| **Type Hints** | Encouraged | Progressive adoption for better code clarity |
| **Inline Comments** | As needed | For complex logic and business rules |
| **Examples** | Encouraged | Code examples for key usage patterns |

### Documentation Format

- **Headers**: Use descriptive headers with emoji for visual scanning
- **Lists**: Use bullet points or numbered lists for clarity
- **Tables**: For structured comparisons and reference data
- **Code Blocks**: With language syntax highlighting
- **Links**: Relative links for internal documentation, absolute for external

## 🤝 Contributing to Documentation

When updating the codebase, please ensure documentation stays current:

### Documentation Checklist

- [ ] **Code Changes**: Update docstrings and inline comments
- [ ] **Architecture Changes**: Update architecture diagrams and documents
- [ ] **New Features**: Add documentation for new components and patterns
- [ ] **Configuration Changes**: Update configuration schemas and examples
- [ ] **API Changes**: Update API documentation and examples
- [ ] **Breaking Changes**: Document in changelog and migration guide

### Documentation File Organization

```
docs/
├── README.md                           # This file - documentation index
├── SOFTWARE_ARCHITECTURE.md            # High-level architecture
├── TECHNICAL_ARCHITECTURE.md           # Technical implementation
├── USER_MANUAL.md                      # User guide (CLI)
├── TUI_USER_MANUAL.md                  # User guide (TUI)
├── API_IMPLEMENTATION.md               # REST API documentation
├── PATTERN_EXECUTION_API.md            # Pattern API guide
├── TUI_ARCHITECTURE.md                 # TUI technical docs
├── TUI_DESIGN_GUIDE.md                 # TUI design guidelines
├── TESTING_README.md                   # Testing overview
├── TESTING_SETUP_GUIDE.md              # Testing setup
├── TEST_STRUCTURE.md                   # Test organization
├── CI_PIPELINE.md                      # CI/CD documentation
├── BRANCH_PROTECTION.md                # Git workflow
├── VERSION_MANAGEMENT.md               # Release process
├── github/                             # GitHub-specific docs
│   ├── CODEQL_README.md
│   ├── CODEQL_FALSE_POSITIVES.md
│   └── CODEQL_DISMISSAL_TEMPLATE.md
└── drawings/                           # Architecture diagrams
    ├── README.md
    ├── *.d2                            # D2 diagram sources
    └── *.svg                           # Generated diagrams
```

### Documentation Tools

- **Markdown**: Primary documentation format
- **D2**: Architecture diagrams (`d2lang.com`)
- **Python Docstrings**: Google style for code documentation
- **YAML Comments**: Inline documentation for configuration files
- **OpenAPI/Swagger**: REST API specification

## 🚀 Getting Started with Documentation

### For New Contributors

1. Start with [README.md](../README.md) for project overview
2. Read [SOFTWARE_ARCHITECTURE.md](SOFTWARE_ARCHITECTURE.md) for system understanding
3. Review [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) for implementation details
4. Check [TESTING_SETUP_GUIDE.md](TESTING_SETUP_GUIDE.md) to set up development environment

### For Users

1. [USER_MANUAL.md](USER_MANUAL.md) - Complete CLI user guide
2. [TUI_USER_MANUAL.md](TUI_USER_MANUAL.md) - Terminal UI guide
3. [API_IMPLEMENTATION.md](API_IMPLEMENTATION.md) - REST API usage

### For Maintainers

1. [CI_PIPELINE.md](CI_PIPELINE.md) - CI/CD workflows
2. [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) - Git workflow
3. [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Release process
4. [github/CODEQL_FALSE_POSITIVES.md](github/CODEQL_FALSE_POSITIVES.md) - Security review notes

---

## 📄 License

This documentation is part of the AskAI CLI project and is subject to the same license as the project.

---

*This documentation is actively maintained and reflects the current state of the AskAI CLI project. Last updated: December 2025.*
