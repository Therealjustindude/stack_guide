# Quick Start: Adding Data Sources

This guide shows you how to quickly add data sources to StackGuide in 3 simple steps.

## 🚀 Quick Start (3 Steps)

### Step 1: Edit Configuration
Open `config/sources.json` and add your source:

```json
{
  "sources": {
    "local": [
      {
        "id": "my-project",
        "name": "My Project",
        "path": "/workspace",
        "type": "local",
        "enabled": true,
        "description": "My project files",
        "patterns": ["*.py", "*.md", "*.txt"],
        "exclude_patterns": ["__pycache__", "*.pyc", ".git"]
      }
    ]
  }
}
```

### Step 2: Restart Services
```bash
make dev-restart
```

### Step 3: Test Ingestion
```bash
make ingest
```

## 📂 Common Source Types

### Local Directory
```json
{
  "id": "docs",
  "name": "Documentation",
  "path": "/workspace/docs",
  "type": "local",
  "enabled": true
}
```

### Git Repository
```json
{
  "id": "api-docs",
  "name": "API Docs",
  "url": "https://github.com/company/api-docs",
  "type": "git",
  "branch": "main",
  "enabled": true
}
```

### Confluence Space
```json
{
  "id": "team-docs",
  "name": "Team Docs",
  "service": "confluence",
  "type": "cloud",
  "enabled": true,
  "config": {
    "base_url": "https://company.atlassian.net",
    "space_key": "TEAM"
  }
}
```

## 🔧 CLI Commands

### View Sources
```bash
make cli
# Then type: sources
```

### Check Status
```bash
make status
```

### View Logs
```bash
make logs-api
```

## ⚠️ Common Issues

**Source not found?**
- Use `/workspace` for current project
- Check volume mounts in docker-compose.yml
- Restart containers after config changes

**Files not processing?**
- Verify file patterns in `patterns` array
- Check exclusion patterns
- Ensure source is `enabled: true`

## 📚 Next Steps

- [Full Configuration Guide](CONFIGURATION.md)
- [Connectors Guide](CONNECTORS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
