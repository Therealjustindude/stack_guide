# Project Management Guide

StackGuide makes it easy to add your personal coding projects to your knowledge base, so you can quickly get back up to speed on any project.

## 🚀 Quick Start

### 1. Add Your First Project
```bash
# Start StackGuide
make dev

# Add a project
make add-project
```

### 2. Use the CLI for Full Control
```bash
make cli
# Then type: sources
```

## 📁 Managing Projects

### Add a New Project
```bash
make cli
sources> add
```

**What you'll need:**
- Project path (e.g., `~/Projects/weather-app`)
- Project name (optional - auto-detected from path)
- Description (optional - helps with context)
- Project ID (optional - auto-generated)

**Example:**
```
sources> add
Enter project path: ~/Projects/weather-app
Enter project name (optional): Weather Dashboard
Enter project description (optional): Personal weather app with React frontend
Enter project ID (optional): weather-app
```

### List Your Projects
```bash
make cli
sources> list
```

### Remove a Project
```bash
make cli
sources> remove
# Select project by number
```

## 🔧 Makefile Shortcuts

```bash
# Add new project (interactive)
make add-project

# Show project management commands
make projects

# Open CLI for full management
make cli
```

## 📊 Project Configuration

Projects are automatically configured with:
- **Smart file patterns** - Detects common code files (`.md`, `.py`, `.js`, `.ts`, etc.)
- **Exclusions** - Ignores build artifacts, dependencies, and sensitive files
- **Path mapping** - Automatically maps to Docker container paths
- **Metadata** - Stores name, description, and configuration

## 🎯 Use Cases

### Personal Project Discovery
```bash
query "What projects do I have that use React?"
query "Which of my projects are Python-based?"
query "Do I have any unfinished projects with TODO items?"
```

### Quick Project Resume
```bash
query "How do I run the weather-app project?"
query "What was I working on in the blog-engine project?"
query "What dependencies does the api-gateway project need?"
```

### Cross-Project Insights
```bash
query "Which of my projects have similar authentication patterns?"
query "Do any of my projects use the same database setup?"
query "What testing frameworks am I using across projects?"
```

## 🚨 Important Notes

- **Path Mapping**: Projects are mapped to `/host` in containers
- **File Types**: Automatically detects and indexes common code files
- **Privacy**: All processing happens locally
- **Storage**: Project metadata stored in `config/sources.json`

## 🔍 Troubleshooting

### Project Not Found
- Check the path exists on your machine
- Ensure StackGuide is running (`make dev`)
- Verify the project was added (`sources list`)

### Files Not Indexed
- Check file patterns in project configuration
- Ensure files aren't excluded by patterns
- Run `make ingest` to re-index

### Path Issues
- Use absolute paths or `~` for home directory
- StackGuide automatically maps to container paths
- Check Docker volume mounts in `docker-compose.dev.yml`

## 📚 Next Steps

After adding projects:
1. **Ingest** - Run `make ingest` to index your projects
2. **Query** - Ask questions about your codebases
3. **Organize** - Add descriptions and organize by purpose
4. **Share** - Export your project configuration for team use

---

**Need help?** Use `make cli` then type `sources help` for interactive assistance.
