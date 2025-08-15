# StackGuide Documentation 📚

Welcome to the complete StackGuide documentation! This guide covers everything you need to know about setting up, configuring, and using StackGuide.

## 🚀 Quick Start

- **[Main README](../README.md)** - Project overview and quick start
- **[Quick Start: Adding Sources](QUICK_START_SOURCES.md)** - 3-step guide to add your first data source

## 📖 Core Guides

### **Configuration & Setup**
- **[Configuration Guide](CONFIGURATION.md)** - Complete guide to configuring data sources and settings
- **[Environment Setup](ENVIRONMENT.md)** - Development, staging, and production setup (coming soon)

### **Usage & Features**
- **[CLI Reference](CLI.md)** - Complete CLI commands and usage (coming soon)
- **[API Reference](API.md)** - API endpoints and usage (coming soon)
- **[Query Examples](QUERIES.md)** - Example queries and use cases (coming soon)

### **Advanced Topics**
- **[Connectors Guide](CONNECTORS.md)** - Cloud service integration (Confluence, Notion, etc.)
- **[Architecture Guide](ARCHITECTURE.md)** - System design and technical details (coming soon)
- **[Development Guide](DEVELOPMENT.md)** - Contributing and extending StackGuide (coming soon)

## 🏗️ Architecture Overview

StackGuide is built with a **local-first, containerized architecture**:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │  FastAPI API    │    │   Chroma DB     │
│   (Terminal)    │◄──►│   (Python)      │◄──►│  (Vector DB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │  (gpt-oss/llama)│
                       └─────────────────┘
```

### **Key Components**

- **CLI Interface** - Simple command-line interface for developers
- **FastAPI Backend** - Python-based API with hot reloading
- **Chroma DB** - Local vector database for document storage
- **LLM Service** - Local AI model (GPU: gpt-oss-20b, CPU: llama2-7b-chat)
- **Data Connectors** - Local files, Git repos, cloud services

## 🔧 Development Commands

### **Essential Commands**
```bash
make dev              # Start development environment
make build            # Build Docker images
make status           # Check service health
make cli              # Open interactive CLI
make clean            # Clean up everything
```

### **Advanced Workflows**
```bash
make dev-refresh      # Rebuild and restart (dependency changes)
make dev-restart      # Quick restart (code changes)
make dev-cycle        # Full cycle: clean + build + dev
make dev-monitor      # Start with monitoring
```

### **Health & Debugging**
```bash
make health           # Quick health overview
make health-all       # Test all health endpoints
make logs             # View service logs
make logs-follow      # Follow logs in real-time
```

## 📁 Project Structure

```
stack_guide/
├── app/                    # Application code
│   ├── cli/              # Command-line interface
│   ├── core/             # Core business logic
│   ├── api/              # FastAPI application
│   ├── llm/              # LLM service integration
│   └── utils/            # Shared utilities
├── config/                # Configuration files
│   └── sources.json      # Data source configuration
├── docs/                  # Documentation
├── docker/                # Docker configuration
├── data/                  # Persistent data (mounted volumes)
├── models/                # AI model files (mounted volumes)
├── docker-compose.yml     # Production Docker setup
├── docker-compose.dev.yml # Development Docker setup
├── Makefile              # Development commands
└── README.md             # Project overview
```

## 🌐 Service Architecture

### **Development Mode**
- **API**: http://localhost:8000 (FastAPI with hot reload)
- **LLM**: http://localhost:8001 (CPU-friendly llama2-7b-chat)
- **Chroma**: http://localhost:8002 (Local vector database)

### **Production Mode**
- **API**: http://localhost:8000 (FastAPI)
- **LLM**: http://localhost:8001 (GPU-accelerated gpt-oss-20b)
- **Chroma**: http://localhost:8002 (Local vector database)

## 🔒 Security & Privacy

- **Local-First**: All processing happens locally by default
- **No External Data**: Unless cloud connectors are explicitly enabled
- **Secrets Handling**: Automatic detection and redaction of sensitive information
- **File Exclusions**: Respects .onboarderignore patterns

## 🚀 Future Features

### **Phase 1: Core RAG Pipeline** ✅
- [x] Data ingestion from local sources
- [x] Configuration-driven source management
- [x] Basic CLI interface
- [ ] Query processing and retrieval
- [ ] Response generation with citations

### **Phase 2: Cloud Connectors**
- [ ] Confluence integration
- [ ] Notion integration
- [ ] Google Drive integration
- [ ] Custom connector framework

### **Phase 3: Advanced Features**
- [ ] Auto-discovery of documentation
- [ ] Team collaboration features
- [ ] Advanced query capabilities
- [ ] Performance optimization

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests
5. **Submit** a pull request

### **Development Setup**
```bash
# Clone and setup
git clone <your-fork>
cd stack_guide

# Start development environment
make dev

# Make changes and test
make cli
# Test your changes...

# Run tests (when available)
make test
```

## 🆘 Support & Troubleshooting

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
make dev          # Fresh start from scratch
```

### **Getting Help**
- Check the [issues](https://github.com/your-repo/issues) page
- Review the [Configuration Guide](CONFIGURATION.md)
- Open a new issue with detailed error information

---

**Built with ❤️ for teams who value knowledge, privacy, and local-first development.**
