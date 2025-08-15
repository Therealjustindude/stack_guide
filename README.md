# StackGuide 🚀

**StackGuide** is a **local-first AI-powered knowledge assistant** that helps team members find, understand, and act on information about their product — from code and architecture to workflows and environments.

Powered by **OpenAI's open-weight gpt-oss model** running locally via vLLM and paired with a local vector database, StackGuide works fully offline by default but supports optional cloud integrations for distributed teams.

## 🚀 Quick Start Commands

### **One Command to Rule Them All**
```bash
make stackguide      # Full setup & launch (build + dev)
```

### **Smart CLI Launch**
```bash
make stackguide-cli  # Setup, launch & open CLI automatically
```

### **Traditional Step-by-Step**
```bash
make build    # Build Docker images
make dev      # Start services  
make cli      # Open CLI (in new terminal)
```

## 🎯 Key Features

- **Always relevant**: Supports onboarding, feature planning, debugging, and research
- **Local-first**: Runs on the developer's machine with gpt-oss and local embeddings
- **Citations-first**: Every answer links back to the source material
- **Role-agnostic**: Useful for developers, QA, designers, ops, and beyond
- **Secure**: Redacts sensitive values, ignores secrets, and respects .onboarderignore rules
- **Configurable**: Easy to add local directories, Git repos, and cloud services (Confluence, etc.)

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **LLM**: gpt-oss-20b via vLLM (local GPU inference)
- **Vector DB**: Chroma (local file-backed)
- **Interface**: CLI-first (web UI can be added later)
- **Containerization**: Docker & Docker Compose
- **Embeddings**: Local nomic-embed-text model

## ⚙️ Configuration

StackGuide automatically indexes your current project, but you can easily add more data sources:

### Adding Data Sources
```bash
# View current sources
make cli
# Then type: sources

# Edit configuration
vim config/sources.json

# Restart to apply changes
make dev-restart

# Test ingestion
make ingest
```

### Supported Source Types
- **Local directories** - Index any folder on your machine
- **Git repositories** - Clone and index remote repos
- **Cloud services** - Confluence, Notion, Google Drive (coming soon)

See the [Configuration Guide](docs/CONFIGURATION.md) for detailed examples.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with CUDA support (for vLLM)
- NVIDIA Docker runtime
- gpt-oss model files

### Getting Started from Scratch

```bash
# 1. Build Docker images (first time or after changes)
make build

# 2. Start development environment
make dev

# 3. In another terminal, open the CLI
make cli
```

## 📚 Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Configuration Guide](docs/CONFIGURATION.md)** - Complete guide to configuring data sources and settings
- **[Quick Start: Adding Sources](docs/QUICK_START_SOURCES.md)** - 3-step guide to add your first data source
- **[API Reference](docs/API.md)** - API endpoints and usage (coming soon)
- **[Connectors Guide](docs/CONNECTORS.md)** - Cloud service integration (coming soon)

### One-Command Launch

```bash
# Development mode (with hot reloading)
make dev

# Production mode
make up
```

### CLI Usage

```bash
# Start interactive CLI
make cli

# Run a specific query
make query Q="How do I set up my development environment?"

# Smart query (auto-starts services if needed)
make quick-query Q="How do I set up my development environment?"

# View configured data sources
make cli
# Then type: sources

# Or directly from the container
docker compose exec api python -m cli.main query "Where is the payment integration code?"
docker compose exec api python -m cli.main sources
```

### Smart Development Workflows

```bash
# Quick refresh (for dependency changes)
make dev-refresh

# Quick restart (no rebuild)
make dev-restart

# Full development cycle (clean + build + dev)
make dev-cycle

# Start with monitoring
make dev-monitor
```

### Manual Setup

```bash
# Clone and setup
git clone <your-repo>
cd stack_guide

# Initial setup
make setup

# Start development environment
make dev
```

## 🔍 Health Monitoring & Troubleshooting

### **Quick Health Commands**

StackGuide provides simple Makefile commands for all your health monitoring needs:

#### **1. Quick Health Overview**
```bash
# Get a complete health summary
make health

# Test all health endpoints
make health-all

# Individual service health checks
make health-api      # Test API health
make health-llm      # Test LLM service health
make health-chroma   # Test Chroma DB health
```

#### **2. Service Status & Monitoring**
```bash
# View service status
make status

# Monitor resource usage
make stats

# Test inter-service connectivity
make network
```

#### **3. Logs & Debugging**
```bash
# View logs for specific services
make logs-api        # API service logs
make logs-llm        # LLM service logs
make logs-chroma     # Chroma DB logs

# Follow all logs in real-time
make logs-follow
```

#### **4. Service Management**
```bash
# Restart individual services
make restart-api     # Restart API service
make restart-llm     # Restart LLM service
make restart-chroma  # Restart Chroma DB

# Restart all services
make restart-all
```

### **Manual Health Checks (Advanced)**

If you prefer to run commands manually or need more detailed inspection:

```bash
# Service status
docker compose ps

# Health endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/api/v2/heartbeat

# Container inspection
docker compose exec api ls -la
docker stats --no-stream

# Network connectivity
docker network ls | grep stackguide
docker compose exec api curl http://chroma:8000/api/v2/heartbeat
```

### **Common Health Issues & Solutions**

#### **Service Won't Start**
```bash
# Quick health check
make health

# Check if ports are already in use
lsof -i :8000  # API port
lsof -i :8001  # LLM port
lsof -i :8002  # Chroma port

# Restart services
make dev-restart

# Full rebuild if needed
make dev-cycle
```

#### **Import Errors in API**
```bash
# Check API health
make health-api

# Check Python path in container
docker compose exec api python -c "import sys; print(sys.path)"

# Verify file structure
docker compose exec api ls -la /app/
docker compose exec api python -c "import api.main; print('Import successful')"
```

#### **LLM Service Issues**
```bash
# Check LLM service health
make health-llm

# View LLM service logs
make logs-llm

# Restart just the LLM service
make restart-llm
```

#### **Chroma DB Issues**
```bash
# Check Chroma DB health
make health-chroma

# Check Chroma data directory
ls -la data/chroma/

# Reset Chroma data (if corrupted)
rm -rf data/chroma/*
make dev-restart
```

### **Development Environment Monitoring**

#### **Real-time Monitoring**
```bash
# Start all services with monitoring
make dev-monitor

# This will show:
# - Service status
# - Resource usage
# - Live logs
# - Health check results
```

#### **Quick Health Summary**
```bash
# Get a quick overview of all services
make health

# Check if everything is ready
make quick-query Q="test"
```

## 📁 Project Structure

```
stack_guide/
├── app/                    # Application code
│   ├── cli/              # Command-line interface
│   ├── core/             # Core business logic
│   ├── connectors/       # Data source connectors
│   ├── models/           # ML models and utilities
│   └── utils/            # Shared utilities
├── docker/                # Docker configuration
├── data/                  # Persistent data (mounted volumes)
├── models/                # AI model files (mounted volumes)
├── tests/                 # Test suite
├── docker-compose.yml     # Production Docker setup
├── docker-compose.dev.yml # Development Docker setup
├── Makefile              # Development commands
└── README.md             # This file
```

## 🔧 Available Commands

### **🚀 Quick Start Commands**
```bash
make stackguide      # Full setup & launch (build + dev)
make stackguide-cli  # Setup, launch & open CLI automatically
make quick-query     # Smart query that starts services if needed
```

### **📋 When to Use Each Command**

| Use Case | Command | Description |
|----------|---------|-------------|
| **First time setup** | `make stackguide` | Builds images and starts services |
| **Daily development** | `make dev` | Starts services (assumes images exist) |
| **Dependency changes** | `make dev-refresh` | Rebuilds and restarts |
| **Quick restart** | `make dev-restart` | Restarts without rebuilding |
| **Fresh start** | `make dev-cycle` | Clean + build + start |
| **Smart query** | `make quick-query Q="..."` | Auto-starts services if needed |

### **🔄 Development Workflows**
```bash
make dev             # Start development environment (hot reload)
make dev-refresh     # Rebuild and restart (for dependency changes)
make dev-restart     # Quick restart (no rebuild)
make dev-cycle       # Full cycle: clean + build + dev
make dev-logs        # Start dev environment with logs
make dev-monitor     # Start dev environment with monitoring
```

### **🔧 Core Commands**
```bash
make build           # Build Docker images
make up              # Start production environment
make down            # Stop all services
make logs            # View service logs
make clean           # Clean up everything
```

### **💻 CLI & Queries**
```bash
make cli             # Open interactive CLI
make query           # Run specific query (requires Q= parameter)
```

### **🧪 Development Tools**
```bash
make test            # Run tests
make lint            # Run linting
make format          # Format code
make setup           # Initial setup
make ingest          # Ingest data
```

### **📚 Help**
```bash
make help            # Show all available commands
```

## 🌐 Service Ports

- **API Backend**: http://localhost:8000
- **vLLM Service**: http://localhost:8001
- **Chroma DB**: http://localhost:8002
- **CLI**: Direct terminal access via `make cli`

## 🎯 Development Modes

### **🚀 Quick Start Mode**
```bash
make stackguide      # One command to get everything running
```

### **🔄 Iterative Development Mode**
```bash
make dev-refresh     # For dependency changes
make dev-restart     # For code changes
make dev-cycle       # For major changes
```

### **🔍 Query Mode**
```bash
make quick-query Q="Your question here"  # Smart auto-start
make cli             # Interactive CLI session
```

## 📚 Example Queries

- *"How do I set up my local development environment?"* → Step-by-step instructions with citations to relevant docs and scripts.
- *"Give me an overview of how data flows when a user completes checkout."* → Explains routes, services, and database interactions, with links to the exact files.
- *"Where can I find documentation for the payment integration?"* → Locates and cites relevant Confluence pages, ADRs, or repo files.
- *"What steps are needed to enable feature X in staging?"* → Pulls from config docs, environment setup guides, and integration notes.

## 🔒 Security & Privacy

- **Local-first**: All processing happens locally by default
- **No data sent externally**: Unless cloud connectors are explicitly enabled
- **Secrets handling**: Automatic detection and redaction of sensitive information
- **File exclusions**: Respects .onboarderignore patterns

## 🚀 Future Team Mode

StackGuide can be deployed on shared infrastructure with larger models (gpt-oss-120b) while maintaining its privacy-first, citation-driven approach. Supports role-based access control for developers, QA, designers, ops, and support teams.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

- Check the [issues](https://github.com/your-repo/issues) page
- Review the [documentation](docs/)
- Contact the team

## 🚨 Troubleshooting

### **Common Issues**

| Problem | Solution |
|---------|----------|
| **Services won't start** | `make dev-cycle` (clean + build + start) |
| **Dependency issues** | `make dev-refresh` (rebuild + restart) |
| **CLI not working** | Ensure services are running with `make dev` |
| **Port conflicts** | Check if ports 8000, 8001, 8002 are free |
| **GPU issues** | Verify NVIDIA Docker runtime is installed |

### **Reset Everything**
```bash
make clean        # Remove all containers and images
make stackguide   # Fresh start from scratch
```

---

**Built with ❤️ for teams who value knowledge, privacy, and local-first development.**