# Quick Start: Adding Data Sources 🚀

**3-step guide to add your first data source to StackGuide**

## 🎯 What You'll Learn

- How to add a local directory as a data source
- How to configure file patterns and exclusions
- How to test that your source is working

## 📋 Prerequisites

- StackGuide is running (`make dev`)
- You have a directory with documentation files (`.md`, `.txt`, `.json`, etc.)

## 🚀 Step 1: View Current Sources

First, see what sources are already configured:

```bash
# Open the CLI
make cli

# Then type: sources
```

This shows your current data sources. You should see at least one source (the company documentation example).

## ⚙️ Step 2: Add Your Data Source

Edit the configuration file to add your directory:

```bash
# Edit the configuration
vim config/sources.json
```

Add a new source to the `local` section:

```json
{
  "id": "my-project",
  "name": "My Project",
  "path": "/host/my-project",
  "type": "local",
  "enabled": true,
  "description": "My project documentation",
  "patterns": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
  "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
}
```

**Important**: 
- Replace `/host/my-project` with the actual path to your directory
- The path should be relative to your StackGuide project (e.g., if your project is at `~/Development/stack_guide`, use `/host/../my-project`)

## 🧪 Step 3: Test Your Source

Restart services and test ingestion:

```bash
# Restart to apply changes
make dev-restart

# Test ingestion
make ingest
```

You should see output like:
```
Processing source: My Project
Files processed: 5, chunks created: 23
```

## 🔍 Verify It's Working

Check that your files were ingested:

```bash
# Open CLI
make cli

# Then type: query "What documentation files do you have?"
```

## 🎉 Success!

You've successfully added your first data source! StackGuide will now:

- Index all matching files in your directory
- Create searchable chunks for each file
- Include your content in query responses
- Automatically update when files change

## 🚀 Next Steps

- **Add more sources**: Repeat the process for other directories
- **Configure Git repos**: Add remote repositories
- **Set up cloud services**: Connect to Confluence, Notion, etc.
- **Customize settings**: Adjust chunk sizes, file patterns, etc.

## 🆘 Need Help?

- **Path issues**: Check the [Configuration Guide](CONFIGURATION.md) for path examples
- **Ingestion problems**: See the troubleshooting section in the main configuration guide
- **More examples**: Check the [Configuration Guide](CONFIGURATION.md) for advanced examples

---

**Ready to add more sources?** Check out the [Configuration Guide](CONFIGURATION.md) for advanced options!
