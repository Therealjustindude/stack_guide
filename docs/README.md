# StackGuide Documentation

Welcome to the StackGuide documentation! This directory contains comprehensive guides for configuring and using StackGuide.

## 📚 Available Guides

### Getting Started
- **[Configuration Guide](CONFIGURATION.md)** - Complete guide to configuring data sources and settings
- **[Quick Start: Adding Sources](QUICK_START_SOURCES.md)** - 3-step guide to add your first data source

### Coming Soon
- **[API Reference](API.md)** - API endpoints and usage
- **[Connectors Guide](CONNECTORS.md)** - Cloud service integration (Confluence, Notion, etc.)
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Development Guide](DEVELOPMENT.md)** - Contributing to StackGuide

## 🚀 Quick Reference

### Essential Commands
```bash
# Start development environment
make dev

# Open CLI
make cli

# View sources
stackguide sources

# Ingest data
make ingest

# Search documents
make search Q="your query"
```

### Configuration File
- **Location**: `config/sources.json`
- **Auto-created**: Yes, with sensible defaults
- **Format**: JSON with validation

### Data Sources
- **Local**: Directories on your machine
- **Git**: Remote repositories
- **Cloud**: Confluence, Notion, Google Drive

## 💡 Need Help?

1. **Check the guides above** for detailed explanations
2. **Use the CLI help**: `stackguide --help`
3. **View service status**: `make status`
4. **Check logs**: `make logs-api`

## 🔗 Related Links

- [Main README](../README.md) - Project overview and quick start
- [GitHub Issues](https://github.com/your-repo/stackguide/issues) - Report bugs or request features
- [Discussions](https://github.com/your-repo/stackguide/discussions) - Ask questions and share ideas
