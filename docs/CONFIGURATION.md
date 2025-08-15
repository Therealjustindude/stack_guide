# StackGuide Configuration Guide

This guide explains how to configure data sources, settings, and manage your StackGuide knowledge base.

## 📁 Configuration Files

StackGuide uses a JSON-based configuration system located at `config/sources.json`. This file is automatically created with sensible defaults when you first run the system.

### File Structure
```
config/
└── sources.json          # Main configuration file
```

## 🔧 Configuration Structure

The configuration file has two main sections:

### 1. Sources Configuration
```json
{
  "sources": {
    "local": [...],        # Local filesystem sources
    "git": [...],          # Git repository sources  
    "cloud": [...]         # Cloud service sources (Confluence, etc.)
  }
}
```

### 2. Global Settings
```json
{
  "settings": {
    "default_chunk_size": 1000,
    "default_chunk_overlap": 200,
    "max_file_size_mb": 10,
    "scan_interval_minutes": 60,
    "auto_discovery": {...}
  }
}
```

## 📂 Adding Data Sources

### Local Filesystem Sources

Add local directories to index:

```json
{
  "id": "my-project",
  "name": "My Project",
  "path": "/workspace",
  "type": "local",
  "enabled": true,
  "description": "Main project directory",
  "patterns": ["*.py", "*.md", "*.txt", "*.yaml", "*.yml", "*.json"],
  "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
}
```

**Field Descriptions:**
- `id`: Unique identifier for the source
- `name`: Human-readable name
- `path`: Directory path to index (use `/workspace` for current project)
- `type`: Source type (`local`, `git`, `cloud`)
- `enabled`: Whether to include this source in ingestion
- `description`: Optional description
- `patterns`: File patterns to include (glob patterns)
- `exclude_patterns`: File patterns to exclude

### Git Repository Sources

Add Git repositories to index:

```json
{
  "id": "api-docs",
  "name": "API Documentation",
  "url": "https://github.com/company/api-docs",
  "type": "git",
  "branch": "main",
  "enabled": true,
  "description": "API documentation repository",
  "auth": {
    "type": "ssh_key",
    "path": "~/.ssh/id_rsa"
  }
}
```

**Field Descriptions:**
- `url`: Git repository URL
- `branch`: Branch to clone/checkout
- `auth`: Authentication method (SSH key, token, etc.)

### Cloud Service Sources

Add cloud documentation services:

```json
{
  "id": "team-confluence",
  "name": "Team Documentation",
  "service": "confluence",
  "type": "cloud",
  "enabled": true,
  "description": "Team Confluence space",
  "config": {
    "base_url": "https://company.atlassian.net",
    "space_key": "TEAM",
    "username": "${CONFLUENCE_USERNAME}",
    "api_token": "${CONFLUENCE_API_TOKEN}"
  }
}
```

**Field Descriptions:**
- `service`: Cloud service type (`confluence`, `notion`, `google_drive`)
- `config`: Service-specific configuration
- Environment variables: Use `${VARIABLE_NAME}` for sensitive data

## ⚙️ Global Settings

### Chunking Settings
- `default_chunk_size`: Maximum tokens per chunk (default: 1000)
- `default_chunk_overlap`: Overlap between chunks (default: 200)
- `max_file_size_mb`: Maximum file size to process (default: 10)

### Auto-Discovery Settings
```json
"auto_discovery": {
  "enabled": true,
  "git_repos": true,
  "common_paths": ["~/Development", "~/Documents", "~/Projects"]
}
```

## 🚀 Managing Sources via CLI

### View Current Sources
```bash
# View all configured sources
make cli
stackguide sources

# Or run directly in container
docker compose exec api python -m cli.main sources
```

### Add New Sources
```bash
# Add a local directory
docker compose exec api python -c "
from core.config import ConfigManager, SourceConfig
config = ConfigManager()
source = SourceConfig(
    id='new-project',
    name='New Project',
    path='/workspace/other-project',
    type='local',
    enabled=True,
    description='Another project directory'
)
config.add_source(source)
"
```

### Enable/Disable Sources
```bash
# Disable a source
docker compose exec api python -c "
from core.config import ConfigManager
config = ConfigManager()
config.update_source('my-project', {'enabled': False})
"
```

## 📝 Configuration Examples

### Complete Example Configuration
```json
{
  "sources": {
    "local": [
      {
        "id": "stackguide-project",
        "name": "StackGuide Project",
        "path": "/workspace",
        "type": "local",
        "enabled": true,
        "description": "Current StackGuide project files",
        "patterns": ["*.py", "*.md", "*.txt", "*.yaml", "*.yml", "*.json"],
        "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
      },
      {
        "id": "other-project",
        "name": "Other Project",
        "path": "/workspace/../other-project",
        "type": "local",
        "enabled": false,
        "description": "Another project (disabled)",
        "patterns": ["*.py", "*.md"],
        "exclude_patterns": ["__pycache__", "*.pyc"]
      }
    ],
    "git": [
      {
        "id": "api-docs",
        "name": "API Documentation",
        "url": "https://github.com/company/api-docs",
        "type": "git",
        "branch": "main",
        "enabled": true,
        "description": "API documentation repository"
      }
    ],
    "cloud": [
      {
        "id": "team-confluence",
        "name": "Team Documentation",
        "service": "confluence",
        "type": "cloud",
        "enabled": true,
        "description": "Team Confluence space",
        "config": {
          "base_url": "https://company.atlassian.net",
          "space_key": "TEAM",
          "username": "${CONFLUENCE_USERNAME}",
          "api_token": "${CONFLUENCE_API_TOKEN}"
        }
      }
    ]
  },
  "settings": {
    "default_chunk_size": 1000,
    "default_chunk_overlap": 200,
    "max_file_size_mb": 10,
    "scan_interval_minutes": 60,
    "auto_discovery": {
      "enabled": true,
      "git_repos": true,
      "common_paths": ["~/Development", "~/Documents", "~/Projects"]
    }
  }
}
```

## 🔒 Security Considerations

### Environment Variables
- Store sensitive data (API tokens, passwords) in environment variables
- Use `${VARIABLE_NAME}` syntax in configuration
- Never commit credentials to version control

### File Exclusions
- Always exclude sensitive files (`.env`, `.pem`, `.key`)
- Exclude build artifacts and temporary files
- Consider excluding large binary files

### Access Control
- Limit source paths to necessary directories
- Use read-only access where possible
- Audit source configurations regularly

## 🛠️ Troubleshooting

### Common Issues

**Source not found:**
- Check if the path exists in the container
- Verify volume mounts in docker-compose.yml
- Ensure the source is enabled

**Configuration not loading:**
- Check file permissions
- Verify JSON syntax
- Restart containers after config changes

**Ingestion errors:**
- Check Chroma DB connection
- Verify file access permissions
- Review exclusion patterns

### Debug Commands
```bash
# Check configuration loading
docker compose exec api python -c "
from core.config import ConfigManager
config = ConfigManager()
print('Sources:', len(config.get_enabled_sources()))
print('Settings:', config.get_settings())
"

# Test source access
docker compose exec api ls -la /workspace

# Check Chroma DB status
docker compose exec api python -c "
from core.ingestion import DataIngestionEngine
engine = DataIngestionEngine()
print('Chroma connected:', engine.chroma_client is not None)
"
```

## 📚 Next Steps

1. **Configure your first local source** using the examples above
2. **Test ingestion** with `make ingest`
3. **Add Git repositories** for additional documentation
4. **Configure cloud services** like Confluence
5. **Customize settings** for your use case

For more advanced configuration options, see the [Connectors Guide](CONNECTORS.md) and [API Reference](API.md).
