# StackGuide Configuration Guide

This guide explains how to configure data sources, settings, and manage your StackGuide knowledge base.

## 📁 Configuration Files

StackGuide uses a JSON-based configuration system located at `config/sources.json`. This file is automatically created with sensible defaults when you first run the system.

## 🚀 **Quick Start: 3-Step Setup**

### **Step 1: Auto-Discover Sources**
```bash
stackguide discover
```
This automatically finds documentation on your computer.

### **Step 2: Review & Approve**
```bash
stackguide sources review
```
See what was found and choose what to include.

### **Step 3: Auto-Configure & Ingest**
```bash
stackguide sources auto-configure
make ingest
```
StackGuide configures everything and ingests your documentation.

**That's it!** You now have a fully configured knowledge base.

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
    "local": [...],        # Project and external directory sources
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

### 🚀 **Recommended: Start with Auto-Discovery**

For most users, we recommend starting with auto-discovery to automatically find and configure your documentation:

```bash
# 1. Run auto-discovery to find documentation on your computer
stackguide discover

# 2. Review what was found
stackguide sources review

# 3. Auto-configure the sources you want
stackguide sources auto-configure
```

This will automatically:
- Find your code projects and documentation
- Detect Git repositories
- Suggest appropriate file patterns
- Create sensible configurations

### ⚙️ **Advanced: Manual Configuration**

**When to use manual configuration:**
- You need specific file patterns or exclusions
- Auto-discovery missed some directories
- You want to configure cloud services (Confluence, etc.)
- You need fine-grained control over source behavior

**How to manually configure:**

#### Project Sources (Optional)

**Note**: By default, StackGuide does not ingest its own project files to avoid confusion. If you want to index your StackGuide project for development purposes, you can add:

```json
{
  "id": "stackguide-project",
  "name": "StackGuide Project",
  "path": "/workspace",
  "type": "project",
  "enabled": false,
  "description": "Current StackGuide project files (disabled by default)",
  "patterns": ["*.py", "*.md", "*.txt", "*.yaml", "*.yml", "*.json"],
  "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
}
```

#### External Directory Sources

Index documentation on your computer outside the StackGuide project:

```json
{
  "id": "company-docs",
  "name": "Company Documentation",
  "path": "/workspace/../company-docs",
  "type": "external",
  "enabled": true,
  "description": "External company documentation on your computer",
  "patterns": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.xml", "*.ini", "*.sql", "*.csv"],
  "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
}
```

**Path Explanation**: 
- `/workspace` = your StackGuide project directory (mounted from host)
- `/workspace/../company-docs` = goes up one level from your project, then into `company-docs`
- This allows you to index any directory on your computer relative to where StackGuide is running

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

**What Auto-Discovery Does:**
- **Automatically scans** common directories for documentation
- **Detects Git repositories** and suggests them as sources
- **Finds documentation files** in various formats (Markdown, PDF, etc.)
- **Suggests configurations** for discovered sources
- **Makes setup easier** by auto-populating your sources list

**How to Use Auto-Discovery:**
1. **Enable it** in your configuration (enabled by default)
2. **Run discovery**: `stackguide discover` or `make discover`
3. **Review suggestions** and choose which to add
4. **Auto-configure** sources with one command

## 🔍 Auto-Discovery

### Quick Setup with Auto-Discovery

Instead of manually configuring each source, use auto-discovery to automatically find documentation on your computer:

```bash
# Run auto-discovery to find potential sources
make discover

# Or use the CLI directly
stackguide discover

# Review and approve discovered sources
stackguide sources review

# Auto-configure all approved sources
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

### Customizing Auto-Discovery

Add your own paths to scan:

```json
"auto_discovery": {
  "enabled": true,
  "git_repos": true,
  "common_paths": [
    "~/Development",
    "~/Documents", 
    "~/Projects",
    "~/Company",
    "~/Work",
    "/Users/username/Shared"
  ]
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
  "path": "/workspace/../shared-docs",
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
