# Ask AI 🤖

[![CI Status](https://github.com/ngroegli/askai/actions/workflows/ci.yml/badge.svg)](https://github.com/ngroegli/askai/actions/workflows/ci.yml)
[![Code Quality](https://github.com/ngroegli/askai/actions/workflows/pylint.yml/badge.svg)](https://github.com/ngroegli/askai/actions/workflows/pylint.yml)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

> **⚡ Not just another ChatGPT wrapper** — Ask AI gives you the **flexibility of quick AI questions** AND the **power of structured workflow patterns**. Use it like ChatGPT for fast answers, or leverage reusable patterns for production workflows.

**Ask AI** is a versatile AI assistant that adapts to your needs:

- 🚀 **Quick & Flexible**: Ask questions, analyze files, pipe command output — zero setup required
- 🎯 **Structured Workflows**: Create reusable patterns for consistent, production-ready automation
- 💬 **Context-Aware**: Persistent chat sessions with full conversation memory
- 📸 **Multimodal**: Work with text, images, PDFs, and URLs seamlessly
- 🎨 **Multiple Outputs**: Console, files (Markdown/JSON/HTML), or pipe to other tools
- �️ **Your Choice**: CLI for scripts, REST API for integrations, TUI for interactive use

---

## 🎯 What Makes AskAI Different?

### The Best of Both Worlds: Flexibility **AND** Structure

AskAI gives you **two powerful ways** to work with AI, each valuable for different scenarios:

#### 🚀 Quick Questions: Fast & Flexible

Perfect for exploration, one-off tasks, and rapid experimentation:

```bash
# Ask anything, instantly
askai -q "What's the fastest sorting algorithm?"

# Analyze files on the fly
askai -fi error.log -q "What's causing these errors?"

# Pipe command output
systemctl status nginx | askai -q "Is this healthy?"
```

✅ **Zero setup** — Just ask and get answers
✅ **Completely flexible** — Any question, any context
✅ **Perfect for learning** — Experiment and iterate quickly

#### 🎯 Pattern Workflows: Structured & Reusable

When you find a workflow worth repeating, turn it into a **pattern** — think "infrastructure as code" for AI:

```yaml
# Pattern: log_interpretation.md
name: "Log Analysis Expert"
inputs:
  - name: log_file
    description: Path to log file
  - name: log_level
    description: Filter by severity (ERROR, WARN, INFO)
outputs:
  - name: issues
    type: json
    description: Structured list of issues found
  - name: recommendations
    type: markdown
    description: Action items to resolve issues
```

```bash
# Execute with structured inputs
askai -up log_interpretation -pi '{
  "log_file": "/var/log/nginx/error.log",
  "log_level": "ERROR"
}'

# Get consistent, structured outputs every time
# No prompt engineering needed — the pattern handles it!
```

✅ **Consistent results** — Same analysis methodology every time
✅ **Team collaboration** — Share patterns across organization
✅ **Production-ready** — Structured outputs for automation
✅ **Still fast** — One command, repeatable workflow

### When to Use Each Approach

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| "What does this error mean?" | **Quick Question** | One-off investigation, need flexibility |
| Daily log analysis for ops team | **Pattern** | Consistency, team alignment, automation |
| Trying different prompt variations | **Quick Question** | Fast iteration and experimentation |
| Standard compliance reporting | **Pattern** | Audit trail, standardized output |
| Learning a new technology | **Quick Question** | Conversational, exploratory |
| CI/CD integration | **Pattern** | Reliable, structured, scriptable |

### Built-In Patterns (Ready to Use)

| Pattern | What It Does | Example Use Case |
|---------|--------------|------------------|
| **log_interpretation** | Analyzes logs, finds patterns, suggests fixes | Production debugging, security audits |
| **kql_generation** | Generates KQL queries from natural language | Azure Sentinel query building |
| **linux_cli_command_generation** | Creates shell commands from descriptions | DevOps automation, learning Linux |
| **pdf_summary** | Extracts key points from documents | Research papers, compliance docs |
| **data_visualization** | Generates visualization code (Python/R) | Data analysis, report generation |

**📁 Browse `patterns/` folder** — use as-is, modify, or create your own!

**The power is in having both.** Start with quick questions for exploration, graduate to patterns when you find workflows worth standardizing.

---

## 🚀 Quick Start

### Installation

**Option 1: Quick Install (Recommended)**

The installer handles:

✔️ Python virtual environment setup
✔️ Dependency installation
✔️ Shell alias creation
✔️ Initial configuration template


```bash
git clone https://github.com/ngroegli/askai
cd askai
chmod +x install.sh
./install.sh
```


After installation, you can either:

- Manually edit your configuration:

  ```bash
  nano ~/.askai_config.yml
  ```

- Or simply run `askai` with no config file—the tool will walk you through an interactive setup wizard to create your configuration from a template.

For a template and all available configuration options, see [`config/config_example.yml`](./config/config_example.yml).

Reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

**Option 2: Manual Installation**

1. Clone the repository:

```bash
git clone https://github.com/ngroegli/askai
cd askai
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example config:

```bash
cp config/config_example.yml ~/.askai_config.yml
```

Edit `~/.askai_config.yml` with your API key and preferences.

5. Create an alias for easy access:

```bash
alias askai="python /full/path/to/askai/askai.py"
```

Add this to your `.bashrc`, `.zshrc`, or `.profile`, then reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Alternatively, for true system-wide installation:

```bash
chmod +x askai.py
sudo ln -s /full/path/to/askai/askai.py /usr/local/bin/askai
```

---

## 💡 Usage Examples

### 1. Quick Questions — Fast & Simple ⚡

Get instant answers without any setup:

```bash
# Ask anything
askai -q "What's the difference between TCP and UDP?"

# Get code explanations
askai -q "Explain this regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Quick troubleshooting
askai -q "Why would a Python script give 'ModuleNotFoundError'?"
```

### 2. Analyze Files & Context 📁

Work with files directly — no copying and pasting:

```bash
# Analyze text files
askai -fi error.log -q "What are the most critical errors?"

# Review code
askai -fi script.py -q "Are there any security issues in this code?"

# Analyze images
askai -img screenshot.png -q "What's wrong with this UI?"

# Process PDFs
askai -pdf report.pdf -q "Summarize the key findings"

# Scrape and analyze web content
askai -url https://example.com/article -q "What's the main argument?"
```

### 3. Pipe Command Output 🔄

The power of Unix pipes + AI:

```bash
# Debug errors in real-time
systemctl status nginx 2>&1 | askai -q "Is this healthy?"

# Analyze system state
docker ps -a | askai -q "Which containers are stopped and why might that be?"

# Get explanations
ls -la | askai -q "Explain the permissions and ownership"

# Smart filtering
journalctl -u ssh -n 100 | askai -q "Any suspicious login attempts?"
```

### 4. Pattern Workflows — Structured & Repeatable 🎯

When you need consistency and reusability:

```bash
# List available patterns
askai --list-patterns

# Production log analysis
askai -up log_interpretation -pi '{
  "log_file": "/var/log/nginx/error.log",
  "log_level": "ERROR"
}'

# Generate database queries
askai -up kql_generation -pi '{
  "query_description": "Show failed login attempts in last 24 hours",
  "data_source": "SecurityEvent"
}'

# DevOps automation
askai -up linux_cli_command_generation -pi '{
  "task_description": "Find all files larger than 100MB modified in last 7 days"
}'
```

**💡 Pro tip**: Patterns use the same `-fi`, `-img`, `-pdf` flags as quick questions, but with structured inputs and consistent outputs!

### 5. Save & Format Output 💾

Export results in multiple formats:

```bash
# Save as Markdown (default)
askai -q "Top 5 Python frameworks" -o report.md -f md

# Get JSON output for automation
askai -q "List HTTP status codes" -f json -o data.json

# Generate HTML reports
askai -up log_interpretation -pi '{"log_file": "app.log"}' -f html -o report.html

# Combine with patterns
askai -up pdf_summary -pi '{"pdf_file": "report.pdf"}' -o summary.md
```

### 6. Interactive Chat Sessions 💬

Have persistent conversations with context:

```bash
# Start interactive chat mode (TUI interface)
askai --interactive
# Or use the short form
askai -i

# Within the interface, have multi-turn conversations:
> Explain Docker containers
> How do I mount volumes?
> Show me an example docker-compose.yml
```

The interactive mode maintains full conversation context — perfect for learning, debugging, or exploring complex topics!

### 7. Advanced Options ⚙️

Fine-tune your AI interactions:

```bash
# Override default AI model
askai -q "Tell me a joke" -m "anthropic/claude-3-opus-20240229"

# Combine multiple inputs (multimodal)
askai -img diagram.jpg -pdf specs.pdf -q "Does the diagram match the specifications?"

# Use different models for patterns
askai -up data_visualization -pi '{"data": "sales.csv"}' -m "anthropic/claude-3.5-sonnet"
```

---

## 🎯 Key Features

| Feature | Description | Best For |
|---------|-------------|----------|
| 🚀 **Quick Questions** | Ask anything, instant answers | Exploration, learning, one-off tasks |
| 🎯 **Pattern Workflows** | Structured, reusable AI processes | Production use, team collaboration, automation |
| 💬 **Chat Sessions** | Persistent multi-turn conversations | Deep problem-solving, learning complex topics |
| � **Multimodal Support** | Text, images, PDFs, URLs | Document analysis, visual debugging |
| � **Unix Pipes** | Pipe command output directly to AI | Real-time debugging, system analysis |
| 🎨 **Multiple Output Formats** | Markdown, JSON, HTML, plain text | Integration, reporting, automation |
| 🖥️ **Three Interfaces** | CLI, REST API, Terminal UI (TUI) | Different workflows and preferences |
| 🔌 **Extensible** | Custom patterns, multiple AI providers | Tailored to your specific needs |
| 🔒 **Secure** | Path validation, API key management | Enterprise-ready security |
| 🧪 **Production-Ready** | 300+ tests, CI/CD, comprehensive docs | Professional development workflows |

---

## 📚 Documentation

### For Users

- **[USER_MANUAL.md](docs/USER_MANUAL.md)** - Complete user guide with advanced features
- **[TUI_USER_MANUAL.md](docs/TUI_USER_MANUAL.md)** - Terminal UI guide for interactive mode
- **Pattern Files** - Check `patterns/` folder for examples and templates

### For Developers

- **[SOFTWARE_ARCHITECTURE.md](docs/SOFTWARE_ARCHITECTURE.md)** - System architecture and design
- **[TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md)** - Implementation details
- **[API_IMPLEMENTATION.md](docs/API_IMPLEMENTATION.md)** - REST API documentation
- **[TESTING_README.md](docs/TESTING_README.md)** - Testing guide and conventions

### For Contributors

- **[CI_PIPELINE.md](docs/CI_PIPELINE.md)** - CI/CD workflows and processes
- **[BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md)** - Git workflow and PR guidelines
- **[VERSION_MANAGEMENT.md](docs/VERSION_MANAGEMENT.md)** - Release and versioning

**Full documentation index:** See [docs/](docs/) folder for complete documentation listing.

---

## 🏗️ Architecture Overview

AskAI follows a modern layered architecture:

```
┌─────────────────────────────────────────┐
│     Presentation Layer                  │
│  ┌─────────┬──────────┬──────────────┐ │
│  │   CLI   │  REST API │     TUI      │ │
│  └─────────┴──────────┴──────────────┘ │
├─────────────────────────────────────────┤
│         Application Layer               │
│  ┌──────────────┬───────────────────┐  │
│  │  Patterns    │  Questions │ Chat │  │
│  └──────────────┴───────────────────┘  │
├─────────────────────────────────────────┤
│          Service Layer                  │
│  ┌──────────────────────────────────┐  │
│  │    AI Service (OpenRouter)       │  │
│  └──────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       Infrastructure Layer              │
│  ┌────────┬─────────┬────────────────┐ │
│  │ Config │ Logging │ Output Writers │ │
│  └────────┴─────────┴────────────────┘ │
└─────────────────────────────────────────┘
```

**Key directories:**
- `src/askai/core/` - Business logic (AI, patterns, questions, chat)
- `src/askai/presentation/` - User interfaces (CLI, API, TUI)
- `src/askai/output/` - Output processing (formatters, writers)
- `src/askai/utils/` - Shared utilities (config, logging)

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/ngroegli/askai
cd askai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
make test-unit
make test-integration
```

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run specific test category
make test-integration-pattern
make test-integration-question

# Check code quality
make lint
```

### Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** your feature branch from `develop`:
   ```bash
   git checkout -b feature/amazing-feature develop
   ```
3. **Make** your changes and test thoroughly
4. **Run** quality checks:
   ```bash
   make lint
   make test
   ```
5. **Submit** a pull request to `develop` branch

**Branch structure:**
- `main` - Stable production releases
- `develop` - Integration branch for features
- `feature/*` - Individual feature branches

See [BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) for detailed workflow guidelines.

### CI/CD Pipeline

GitHub Actions automatically:
- ✅ Runs Pylint checks on all pushes
- ✅ Executes test suite on pull requests
- ✅ Blocks PRs with critical errors
- ✅ Generates security reports with CodeQL

See [CI_PIPELINE.md](docs/CI_PIPELINE.md) for complete CI/CD documentation.

---

## 🔐 Security

- **API keys** are stored locally in `~/.askai_config.yml` (never committed to git)
- **Path validation** prevents directory traversal attacks
- **CodeQL scanning** runs on every push to detect security issues
- **Dependency audits** via GitHub Dependabot

Report security vulnerabilities privately via GitHub Security Advisories.

---

## 🤝 Contributing

Contributions are welcome! Please see:
- [BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) - Git workflow and PR process
- [CI_PIPELINE.md](docs/CI_PIPELINE.md) - CI/CD and quality checks
- [TESTING_README.md](docs/TESTING_README.md) - Testing guidelines

---

## 📄 License

[GNU General Public License v3.0](LICENSE) - See LICENSE file for details.

---

## 🌟 Support & Community

- 📖 **Documentation**: Browse the [docs/](docs/) folder
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/ngroegli/askai/issues)
- 💬 **Discussions**: Join [GitHub Discussions](https://github.com/ngroegli/askai/discussions)

---

## ⚙️ Requirements

- Python 3.7 or higher
- OpenRouter API key
- Dependencies: See [requirements.txt](requirements.txt)

---

