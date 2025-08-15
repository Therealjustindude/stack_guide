# Enterprise Documentation Ingestion Guide

Smart strategies for ingesting enterprise documentation without overwhelming your system.

## 🎯 **The Challenge**

Enterprise documentation systems are massive:
- **Confluence**: 10,000+ pages per workspace
- **Notion**: Hundreds of databases and pages
- **SharePoint**: Thousands of documents
- **GitHub**: Multiple repositories with extensive documentation

**Problem**: Bulk ingestion = poor search quality + massive storage costs

## 🚀 **Smart Ingestion Strategies**

### **1. URL-Based Ingestion (Recommended)**

Ingest only specific, relevant pages:

```bash
# Ingest a specific Confluence page
make ingest-url
# Enter: https://confluence.company.com/pages/viewpage.action?pageId=12345
# Name: "API Setup Guide"

# Ingest a specific Notion page
make ingest-url
# Enter: https://company.notion.site/Setup-Guide-abc123
# Name: "Development Environment Setup"

# Ingest a GitHub README
make ingest-url
# Enter: https://github.com/company/api-service/blob/main/README.md
# Name: "API Service Documentation"
```

### **2. Smart Workspace Discovery**

Instead of ingesting everything, discover what's available first:

```bash
# List available Confluence spaces
curl -H "Authorization: Bearer $CONFLUENCE_TOKEN" \
  "https://company.atlassian.net/wiki/rest/api/space"

# List pages in a specific space
curl -H "Authorization: Bearer $CONFLUENCE_TOKEN" \
  "https://company.atlassian.net/wiki/rest/api/content?spaceKey=API&type=page"
```

### **3. Filtered Ingestion**

Use metadata to filter relevant content:

```yaml
# config/sources.json
{
  "sources": {
    "confluence": [
      {
        "id": "api-documentation",
        "name": "API Documentation",
        "space_key": "API",
        "filters": {
          "labels": ["api", "documentation", "setup"],
          "last_updated": "2024-01-01",
          "exclude_labels": ["draft", "archive", "meeting-notes"],
          "page_types": ["page", "blogpost"],
          "authors": ["tech-team", "api-team"]
        },
        "enabled": true
      }
    ]
  }
}
```

## 🔍 **Content Discovery Workflow**

### **Step 1: Audit Your Documentation**

```bash
# 1. Identify key documentation areas
- API Documentation
- Setup Guides
- Architecture Decisions
- Troubleshooting Guides
- Deployment Procedures

# 2. Map to specific URLs/pages
- API Setup: https://confluence.company.com/pages/viewpage.action?pageId=12345
- Environment Config: https://confluence.company.com/pages/viewpage.action?pageId=67890
- Troubleshooting: https://confluence.company.com/pages/viewpage.action?pageId=11111
```

### **Step 2: Prioritize by Relevance**

```bash
# High Priority (Ingest First)
- Setup guides
- API documentation
- Architecture diagrams
- Configuration examples

# Medium Priority (Ingest Later)
- Troubleshooting guides
- Best practices
- Code examples

# Low Priority (Skip)
- Meeting notes
- Personal pages
- Archive content
- Draft documents
```

### **Step 3: Incremental Ingestion**

```bash
# Day 1: Core setup documentation
make ingest-url  # API Setup Guide
make ingest-url  # Environment Configuration
make ingest-url  # Database Setup

# Day 2: Additional guides
make ingest-url  # Troubleshooting Guide
make ingest-url  # Deployment Procedures

# Day 3: Architecture docs
make ingest-url  # System Architecture
make ingest-url  # Data Flow Diagrams
```

## ⚙️ **Configuration Examples**

### **Confluence Integration**

```yaml
# config/confluence.yaml
confluence:
  base_url: "https://company.atlassian.net"
  username: "${CONFLUENCE_USERNAME}"
  api_token: "${CONFLUENCE_API_TOKEN}"
  
  # Smart filtering
  filters:
    spaces:
      - "API"      # API documentation
      - "DEV"      # Development guides
      - "ARCH"     # Architecture docs
    
    exclude_spaces:
      - "HR"       # Human resources
      - "FIN"      # Finance
      - "MKT"      # Marketing
    
    page_filters:
      labels: ["documentation", "api", "setup", "guide"]
      exclude_labels: ["draft", "archive", "personal"]
      min_last_updated: "2023-01-01"
```

### **Notion Integration**

```yaml
# config/notion.yaml
notion:
  integration_token: "${NOTION_TOKEN}"
  
  # Target specific databases
  databases:
    - "API Documentation"
    - "Setup Guides"
    - "Architecture Decisions"
  
  # Filter by properties
  filters:
    status: "Published"
    category: ["API", "Setup", "Architecture"]
    exclude_status: ["Draft", "Archive"]
```

## 📊 **Monitoring & Quality Control**

### **Ingestion Metrics**

```bash
# Check ingestion status
make status

# View collection stats
make cli
stackguide> status
```

### **Quality Indicators**

- **Chunk count**: Should be reasonable (100-1000 per major doc)
- **Relevance scores**: Should be >70% for related queries
- **Response quality**: Answers should be specific and actionable

### **When to Stop**

Stop ingesting when:
- Response quality starts declining
- Storage usage becomes excessive
- Search results become less relevant

## 🚨 **Common Pitfalls & Solutions**

### **Pitfall 1: Too Much Content**
```
Problem: 50,000 chunks, poor search quality
Solution: Filter by relevance, use URL-based ingestion
```

### **Pitfall 2: Outdated Information**
```
Problem: Old docs overwhelming current docs
Solution: Filter by last_updated date, exclude archives
```

### **Pitfall 3: Irrelevant Content**
```
Problem: Meeting notes and personal pages
Solution: Use labels and page types to filter
```

## 🎯 **Recommended Workflow**

### **For New Teams:**
1. **Start small**: Ingest 5-10 key documents
2. **Test quality**: Query the system and evaluate responses
3. **Expand gradually**: Add more docs based on gaps
4. **Monitor quality**: Stop when quality declines

### **For Existing Teams:**
1. **Audit current docs**: Identify what's actually useful
2. **Remove outdated content**: Clean up old, irrelevant docs
3. **Add missing pieces**: Fill gaps in documentation
4. **Maintain quality**: Regular cleanup and updates

## 🔧 **Commands Reference**

```bash
# URL-based ingestion
make ingest-url

# Bulk ingestion (use carefully)
make ingest

# Check system status
make status

# Query documentation
make cli
stackguide> query "How do I set up the API?"
```

## 📚 **Next Steps**

1. **Start with URL ingestion** for your most important docs
2. **Set up smart filters** for bulk ingestion
3. **Monitor quality** and adjust as needed
4. **Build a curated knowledge base** rather than a data dump

Remember: **Quality over quantity**. A small, well-curated knowledge base is much more valuable than a large, unfiltered one.
