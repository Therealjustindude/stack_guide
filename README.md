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

## 🎯 **Convenient Scripts (Recommended)**

**Skip the `make` commands! Use these intuitive scripts instead:**

### **Install the Scripts:**
```bash
# Make scripts executable and add to PATH
chmod +x install-scripts.sh
./install-scripts.sh
```

### **Use the Scripts:**
```bash
# Start everything and open CLI
stackguide start

# Start with GPU support
stackguide start-gpu

# Build containers without starting (useful for first-time setup)
stackguide docker-build

# Build GPU containers without starting
stackguide docker-build-gpu

# Just open CLI (starts services if needed)
stackguide cli

# Ingest URLs from Confluence, Notion, GitHub
stackguide ingest-url

# Run a quick query
stackguide query "How do I configure the API?"

# Check system status
stackguide status

# View logs
stackguide logs

# Stop services
stackguide stop
```

### **Build vs Start:**
- **`stackguide docker-build`** - Builds containers (takes time, do once)
- **`stackguide start`** - Starts existing containers (fast, do daily)
- **`stackguide start`** will auto-build if containers don't exist

### **Why Use Scripts?**
- **Intuitive Commands** - `stackguide start` instead of `make dev`
- **Cross-Platform** - Works on macOS, Linux, and Windows
- **Smart Auto-Start** - Services start automatically when needed
- **Better UX** - Colored output, progress indicators, helpful messages
- **Available Everywhere** - Run from any directory once installed

## 🔗 URL Ingestion - Enterprise Documentation

**Ingest specific pages from Confluence, Notion, GitHub, and other web sources without overwhelming your system.**

### **Why URL Ingestion?**
- **Targeted Content** - Only ingest the specific documentation you need
- **No Mass Ingestion** - Avoid pulling entire Confluence workspaces
- **Local Processing** - All content processed and stored locally
- **Privacy First** - No data sent to external AI services

### **How to Use URL Ingestion:**

#### **1. Start the CLI:**
```bash
make cli
# or
docker compose exec api python3 -m cli.main
```

#### **2. Use the ingest-url command:**
```
stackguide> ingest-url
```

#### **3. Enter your URL and source name:**
```
🔗 URL Ingestion
Enter a URL to ingest (Confluence, Notion, GitHub, Google Docs, etc.)
URL: https://yourcompany.atlassian.net/wiki/spaces/TEAM/pages/123456789/API+Documentation
Source name (optional): API Documentation

🔄 Ingesting: https://yourcompany.atlassian.net/wiki/spaces/TEAM/pages/123456789/API+Documentation
Please wait...
✅ URL ingestion complete!
   Chunks created: 8
   Source: API Documentation
```

### **Supported Platforms:**

| **Platform** | **Example URLs** | **Features** |
|--------------|------------------|--------------|
| **Confluence** | `https://company.atlassian.net/wiki/...` | Page content extraction, formatting preservation |
| **Notion** | `https://company.notion.site/...` | Page content, database views |
| **GitHub** | `https://github.com/user/repo/blob/main/README.md` | README files, documentation, code comments |
| **Generic Web** | Any web page | HTML content extraction, text chunking |

### **4. Query Your Ingested Content:**
```
stackguide> query "How do I configure the API authentication?"
```

### **Advanced Usage:**

#### **Ingest Multiple Pages:**
```bash
# Ingest API documentation
make cli
ingest-url
# URL: https://confluence.company.com/pages/viewpage.action?pageId=12345
# Name: API Setup Guide

# Ingest troubleshooting guide
ingest-url
# URL: https://confluence.company.com/pages/viewpage.action?pageId=67890
# Name: Troubleshooting Guide
```

#### **Check What's Ingested:**
```
stackguide> status
# Shows all ingested sources and document counts
```

## 📚 Documentation

- **[Configuration Guide](docs/CONFIGURATION.md)** - Add data sources and customize settings
- **[Quick Start: Adding Sources](docs/QUICK_START_SOURCES.md)** - 3-step guide to add your first source
- **[Enterprise Ingestion Guide](docs/ENTERPRISE_INGESTION.md)** - Smart strategies for large documentation systems
- **[Feedback Template](docs/FEEDBACK_TEMPLATE.md)** - Template for testing feedback and bug reports
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

### ✅ **Recently Implemented:**
- **RAG Pipeline** - Query processing and response generation ✅
- **Cloud Connectors** - Confluence, Notion, GitHub URL ingestion ✅
- **Smart Ingestion** - URL-based and filtered enterprise ingestion ✅
- **Feedback System** - Automated metrics and structured feedback collection ✅
- **Response Quality** - Improved confidence scoring and answer generation ✅

### 🚀 **Coming Soon:**
- **Auto-Discovery** - Automatically find documentation on your machine
- **Team Mode** - Shared knowledge bases and collaboration
- **Advanced Filtering** - AI-powered content relevance scoring
- **Real-time Updates** - Monitor and auto-ingest changed documents
- **Performance Dashboard** - Visual metrics and system health monitoring

---

**Questions?** Check the [Configuration Guide](docs/CONFIGURATION.md) or open an issue.