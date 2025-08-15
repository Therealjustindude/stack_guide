# Configuration Guide ⚙️

Complete guide to configuring StackGuide data sources and settings.

## 📋 Quick Start

```bash
# 1. View current sources
make cli
# Then type: sources

# 2. Edit configuration
vim config/sources.json

# 3. Restart to apply changes
make dev-restart

# 4. Test ingestion
make ingest
```

## 🚀 Auto-Discovery (Recommended)

Instead of manually configuring each source, use auto-discovery to automatically find documentation on your computer:

```bash
# Run auto-discovery to find potential sources
make discover

# Review discovered sources
stackguide sources review

# Auto-configure sources
stackguide sources auto-configure
```

### What Gets Discovered

**Common Directories:**
- `~/Development` - Your development projects
- `~/Documents` - Personal and work documents
- `~/Projects` - Project documentation
- `~/Desktop` - Quick access files

**Git Repositories:**
- Automatically detects Git repos in common paths
- Suggests them as Git sources
- Auto-configures branch and remote information

**Documentation Files:**
- Markdown files (`.md`)
- Text files (`.txt`)
- Configuration files (`.json`, `.yaml`, `.yml`)
- Database schemas (`.sql`)
- API documentation (`.xml`, `.ini`)

## ⚙️ Manual Configuration

### Configuration File Structure

```json
{
  "sources": {
    "local": [...],
    "git": [...],
    "cloud": [...]
  },
  "settings": {
    "default_chunk_size": 1000,
    "default_chunk_overlap": 200,
    "auto_discovery": {
      "enabled": true,
      "git_repos": true,
      "common_paths": ["~/Development", "~/Documents"]
    }
  }
}
```

### Local Sources

Index directories on your computer:

```json
{
  "id": "company-docs",
  "name": "Company Documentation",
  "path": "/host/company-docs",
  "type": "local",
  "enabled": true,
  "description": "External company documentation on your computer",
  "patterns": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.xml", "*.ini", "*.sql", "*.csv"],
  "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
}
```

**Path Explanation**: 
- `/workspace` = your StackGuide project directory (mounted from host)
- `/host/company-docs` = host machine directory at the same level as your project, then into `company-docs`
- This allows you to index any directory on your computer at the same level as your StackGuide project

**Field Descriptions:**
- `id`: Unique identifier for the source
- `name`: Human-readable name
- `path`: Directory path to index
- `type`: Source type (always "local" for filesystem sources)
- `enabled`: Whether to process this source
- `description`: Optional description
- `patterns`: File patterns to include (defaults to common documentation formats)
- `exclude_patterns`: Patterns to exclude (defaults to common build artifacts)

### Git Sources

Index remote repositories:

```json
{
  "id": "api-repo",
  "name": "API Repository",
  "url": "https://github.com/company/api",
  "type": "git",
  "branch": "main",
  "enabled": true,
  "description": "Main API repository",
  "auth": {
    "type": "ssh_key",
    "path": "~/.ssh/id_rsa"
  }
}
```

**Field Descriptions:**
- `url`: Git repository URL
- `branch`: Branch to clone (defaults to "main")
- `auth`: Authentication method (SSH key or username/password)

### Cloud Sources

Connect to cloud documentation services:

```json
{
  "id": "team-confluence",
  "name": "Team Documentation",
  "service": "confluence",
  "type": "cloud",
  "enabled": false,
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
- `service`: Cloud service type (confluence, notion, google-drive)
- `config`: Service-specific configuration
- Environment variables: Use `${VARIABLE_NAME}` for sensitive values

## 🔧 Global Settings

### Chunking Settings

```json
"settings": {
  "default_chunk_size": 1000,        // Characters per chunk
  "default_chunk_overlap": 200,      // Overlap between chunks
  "max_file_size_mb": 10,            // Maximum file size to process
  "scan_interval_minutes": 60        // How often to check for changes
}
```

### Auto-Discovery Settings

```json
"auto_discovery": {
  "enabled": true,
  "git_repos": true,
  "common_paths": [
    "~/Development",
    "~/Documents", 
    "~/Projects",
    "~/Company",
    "~/Work"
  ]
}
```

## 🚀 Managing Sources via CLI

### View and Manage Sources

```bash
# View all configured sources
make cli
# Then type: sources

# Or run directly in container
docker compose exec api python -m cli.main sources
```

### Auto-Discovery Commands

```bash
# Discover potential sources
stackguide discover

# Review discovered sources
stackguide sources review

# Auto-configure sources
stackguide sources auto-configure

# Scan specific directory
stackguide discover --path ~/Company
```

### Add New Sources

```bash
# Edit configuration file
vim config/sources.json

# Restart services to apply changes
make dev-restart

# Test ingestion
make ingest
```

## 🔒 Security Considerations

### File Exclusions

StackGuide automatically excludes sensitive files:
- `.env*` files (environment variables)
- `.git` directories
- `node_modules` and build artifacts
- `__pycache__` and compiled Python files

### Custom Exclusions

Add your own exclusion patterns:

```json
"exclude_patterns": [
  "__pycache__", "*.pyc", ".git", "node_modules", ".env*",
  "*.log", "*.tmp", "secrets/", "private/"
]
```

### Environment Variables

For cloud services, use environment variables instead of hardcoded credentials:

```json
"config": {
  "username": "${CONFLUENCE_USERNAME}",
  "api_token": "${CONFLUENCE_API_TOKEN}"
}
```

## 🌐 Multi-Computer Usage

StackGuide can be used across multiple computers in a team environment:

### Shared Configuration

- **Central config**: Store `sources.json` in a shared repository
- **Environment-specific paths**: Use relative paths that work on different machines
- **Volume mounts**: Mount different host directories on different computers

### Example Multi-Computer Setup

```json
{
  "id": "shared-docs",
  "name": "Shared Documentation",
  "path": "/host/shared-docs",
  "type": "local",
  "enabled": true,
  "description": "Team documentation accessible to all developers"
}
```

### Path Considerations

- **Relative paths**: Use `../` to navigate outside the project directory
- **Host mounts**: Different computers can mount different host directories
- **Cross-platform**: Paths work on macOS, Linux, and Windows (with Docker)

### Team Workflow

1. **Shared repository**: Store configuration in version control
2. **Local customization**: Each developer can customize their local paths
3. **Documentation sync**: Team members can access shared documentation
4. **Consistent indexing**: Same sources produce consistent results across machines

## 🔍 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Source not found** | Check path exists and is accessible from container |
| **Permission denied** | Verify Docker volume mount permissions |
| **No files processed** | Check file patterns and exclude patterns |
| **Configuration errors** | Validate JSON syntax and required fields |

### Debug Commands

```bash
# Check if path is accessible
docker compose exec api ls -la /host/your-directory

# View configuration
docker compose exec api cat /app/config/sources.json

# Test file access
docker compose exec api find /host -name "*.md" | head -5
```

### Validation

StackGuide validates your configuration:
- Required fields are present
- Paths are accessible
- File patterns are valid
- Authentication is configured (for cloud sources)

## 📚 Next Steps

- **[Quick Start: Adding Sources](QUICK_START_SOURCES.md)** - 3-step guide to add your first data source
- **[Connectors Guide](CONNECTORS.md)** - Cloud service integration details
- **[API Reference](API.md)** - Programmatic access to sources and settings

For more advanced configuration options, see the [Connectors Guide](CONNECTORS.md) and [API Reference](API.md).
