# AgentOps

AI-powered QA co-pilot for vibe coders - Requirements-driven test automation.

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Set up your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Try the demo
cd examples/demo-project
agentops init
agentops infer --all
agentops import-requirements
agentops generate-tests
agentops run --all
```

## 📁 Project Structure

```
AgentOps/
├── agentops_ai/              # Main package
│   ├── agentops_cli/         # Command-line interface
│   ├── agentops_core/        # Core business logic
│   ├── docs/                 # Documentation
│   ├── prompts/              # LLM prompt templates
│   └── .tours/               # CodeTour files
├── examples/                 # Example projects
│   └── demo-project/         # Demo project
├── .github/                  # CI/CD workflows
├── .private/                 # Internal documentation
└── docs/                     # Project documentation
```

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Poetry
- OpenAI API key

### Setup

```bash
# Clone and install
git clone <repository-url>
cd AgentOps
poetry install

# Set environment variables
export OPENAI_API_KEY="your-api-key"
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=agentops_ai

# Run linting
poetry run ruff check agentops_ai
poetry run black --check agentops_ai
```

### Documentation

```bash
# Start documentation server
cd agentops_ai/docs
poetry run mkdocs serve
```

## 📚 Documentation

- **[Quick Start Guide](agentops_ai/docs/QUICK_START.md)** - Get up and running
- **[Architecture Overview](agentops_ai/docs/ARCHITECTURE_OVERVIEW.md)** - System design
- **[API Reference](agentops_ai/docs/api/)** - Complete API docs
- **[Readiness Checklist](agentops_ai/docs/READINESS_CHECKLIST.md)** - Engineer onboarding

## 🎯 Core Workflow

AgentOps follows a simple **Infer → Approve → Test** workflow:

1. **Infer**: Extract requirements from code changes using LLM
2. **Approve**: Review and approve requirements (interactive or bulk)
3. **Test**: Generate and execute comprehensive test suites

## 🔧 CLI Commands

```bash
agentops init                    # Initialize project
agentops infer <file>            # Infer requirements from file
agentops infer --all             # Infer for all Python files
agentops import-requirements     # Import edited requirements
agentops generate-tests          # Generate tests from requirements
agentops run --all               # Run tests with RCA
agentops traceability            # Export traceability matrix
```

## 🏗️ Architecture

AgentOps uses a modular architecture:

- **CLI Layer**: Command-line interface with Click
- **Core Engine**: Business logic and orchestration
- **Service Layer**: LLM-based test generation
- **Storage Layer**: SQLite database for requirements

## 🤝 Contributing

1. Read the [Architecture Overview](agentops_ai/docs/ARCHITECTURE_OVERVIEW.md)
2. Complete the [Readiness Checklist](agentops_ai/docs/READINESS_CHECKLIST.md)
3. Explore the CodeTours in `.tours/`
4. Follow the development workflow

## 📄 License

[Add your license here]

---

**Built for vibe coders who want to ship fast without sacrificing quality! 🚀** 