# StackGuide 🚀

**Local-first, AI-powered knowledge assistant** that provides instant answers about your codebases, architecture, and workflows.

## ✨ Features

- **Instant Answers** - Ask questions about your code and get accurate responses with citations
- **Local-First** - Runs completely offline with open-source AI models
- **Smart Ingestion** - Automatically indexes local files, Git repos, and cloud services
- **CLI-First** - Simple command-line interface for developers
- **Privacy-Focused** - All processing happens locally by default

## 🔒 Privacy & Security - Business-Ready Architecture

### Complete Data Privacy Guarantee:
- **100% Local Processing** - All AI inference happens on your machine
- **Local Vector Database** - Your document embeddings never leave your computer
- **Local AI Models** - gpt-oss/llama models run entirely locally
- **No External AI Calls** - Zero data sent to external AI services

### Cloud Integration (User-Controlled):
- **Document Collection Only** - Pull docs from Confluence, Notion, etc.
- **Local Processing** - All documents processed and indexed locally
- **No Data Upload** - Cloud services only provide source documents
- **User Consent Required** - Cloud connectors only enabled when explicitly configured

### Business Benefits:
- **Data Residency** - Everything stays in your jurisdiction
- **Compliance Ready** - Meets strict data privacy requirements
- **No Vendor Lock-in** - You own all your data and models
- **Offline Capable** - Works without internet once docs are pulled
- **Team Scalable** - Each user has their own secure local instance

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <your-repo>
cd stack_guide

# 2. Launch (starts all services)
make dev

# 3. Add your first data source
make cli
# Then type: sources

# 4. Start asking questions
make cli
# Then type: query "How do I set up the database?"
```

## 📚 Documentation

- **[Configuration Guide](docs/CONFIGURATION.md)** - Add data sources and customize settings
- **[Quick Start: Adding Sources](docs/QUICK_START_SOURCES.md)** - 3-step guide to add your first source
- **[API Reference](docs/API.md)** - API endpoints and usage (coming soon)

## 🏗️ Architecture

- **Backend**: FastAPI + Python 3.11+
- **AI Model**: gpt-oss-20b (local GPU) or llama2-7b-chat (CPU)
- **Vector DB**: Chroma (local file-backed)
- **Containerization**: Docker & Docker Compose

## 🔧 Development

```bash
# Start development environment
make dev

# Check service health
make status

# Rebuild containers
make build

# Clean everything
make clean
```

## 📖 What's Next?

- **RAG Pipeline** - Query processing and response generation
- **Cloud Connectors** - Confluence, Notion, Google Drive integration
- **Auto-Discovery** - Automatically find documentation on your machine
- **Team Mode** - Shared knowledge bases and collaboration

---

**Questions?** Check the [Configuration Guide](docs/CONFIGURATION.md) or open an issue.