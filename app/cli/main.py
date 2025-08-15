#!/usr/bin/env python3
"""
StackGuide CLI - Command-line interface for StackGuide.
"""

import sys
import logging
from typing import Optional
from core.ingestion import DataIngestionEngine
from core.config import ConfigManager
from core.knowledge import KnowledgeEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_help():
    """Display help information."""
    print("\n📚 Available Commands:")
    print("  ingest     - Ingest all configured data sources")
    print("  ingest-url - Ingest a specific URL (Confluence, Notion, GitHub, etc.)")
    print("  query      - Ask a question about your documentation")
    print("  sources    - Manage data sources (add/remove projects)")
    print("  status     - Check system status and collection stats")
    print("  help       - Show this help message")
    print("  quit       - Exit the CLI\n")

def run_ingest_url():
    """Ingest a specific URL."""
    print("\n🔗 URL Ingestion")
    print("Enter a URL to ingest (Confluence, Notion, GitHub, Google Docs, etc.)")
    
    url = input("URL: ").strip()
    if not url:
        print("❌ No URL provided")
        return
    
    source_name = input("Source name (optional): ").strip() or None
    
    print(f"\n🔄 Ingesting: {url}")
    print("Please wait...")
    
    try:
        engine = DataIngestionEngine()
        result = engine.ingest_url(url, source_name)
        
        if result.errors:
            print(f"❌ Ingestion failed with errors:")
            for error in result.errors:
                print(f"   - {error}")
        else:
            print(f"✅ URL ingestion complete!")
            print(f"   Chunks created: {result.chunks_created}")
            print(f"   Source: {source_name or 'Unnamed'}")
            
    except Exception as e:
        logger.error(f"Error during URL ingestion: {e}")
        print(f"❌ An error occurred: {e}")

def main():
    print("🚀 StackGuide CLI")
    print("Type 'help' for available commands, 'quit' to exit\n")
    
    while True:
        try:
            command = input("stackguide> ").strip().lower()
            
            if command == "quit" or command == "exit":
                print("Goodbye! 👋")
                break
            elif command == "help":
                run_help()
            elif command == "ingest":
                run_ingestion()
            elif command == "ingest-url":
                run_ingest_url()
            elif command == "sources":
                run_sources()
            elif command == "query":
                run_query()
            elif command == "status":
                run_status()
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"An error occurred: {e}")


def run_ingestion():
    """Run data ingestion from configured sources."""
    print("🔄 Starting data ingestion...")
    
    try:
        engine = DataIngestionEngine()
        result = engine.ingest_all(force_reindex=True)
        
        print(f"✅ Ingestion complete!")
        print(f"   Files processed: {result.files_processed}")
        print(f"   Chunks created: {result.chunks_created}")
        print(f"   Sources processed: {len(result.sources_updated)}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"❌ Ingestion failed: {e}")


def run_sources():
    """Display and manage configured data sources."""
    print("📁 Data Source Management:\n")
    print("Available commands:")
    print("  list       - Show all configured sources")
    print("  add        - Add a new project/directory")
    print("  remove     - Remove a source")
    print("  help       - Show this help")
    print("  back       - Return to main menu\n")
    
    while True:
        try:
            command = input("sources> ").strip().lower()
            
            if command == "back" or command == "quit":
                break
            elif command == "help":
                print("\nAvailable commands:")
                print("  list       - Show all configured sources")
                print("  add        - Add a new project/directory")
                print("  remove     - Remove a source")
                print("  help       - Show this help")
                print("  back       - Return to main menu\n")
            elif command == "list":
                _list_sources()
            elif command == "add":
                _add_source()
            elif command == "remove":
                _remove_source()
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error in sources menu: {e}")
            print(f"An error occurred: {e}")


def _list_sources():
    """Display configured data sources."""
    print("\n📁 Configured Data Sources:\n")
    
    try:
        config = ConfigManager()
        
        if not config.sources:
            print("No sources configured. Use 'add' to add your first project.")
            return
        
        for source_type, source_list in config.sources.items():
            print(f"🔸 {source_type.upper()} Sources:")
            for source in source_list:
                status = "✅ Enabled" if source.enabled else "❌ Disabled"
                print(f"   {source.name} ({source.id}) - {status}")
                if source.description:
                    print(f"      {source.description}")
                if hasattr(source, 'path') and source.path:
                    print(f"      Path: {source.path}")
                print()
                
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        print(f"❌ Failed to load sources: {e}")


def _add_source():
    """Add a new local project/directory source."""
    print("\n➕ Add New Project/Directory\n")
    
    # Get project path
    path = input("Enter project path (e.g., ~/Projects/weather-app): ").strip()
    if not path:
        print("❌ No path provided")
        return
    
    # Expand user path
    import os
    expanded_path = os.path.expanduser(path)
    
    # Check if path exists
    if not os.path.exists(expanded_path):
        print(f"❌ Path does not exist: {expanded_path}")
        return
    
    # Get project name
    name = input("Enter project name (optional): ").strip()
    if not name:
        name = os.path.basename(expanded_path)
    
    # Get description
    description = input("Enter project description (optional): ").strip()
    
    # Get project ID
    project_id = input("Enter project ID (optional, will auto-generate): ").strip()
    if not project_id:
        project_id = name.lower().replace(" ", "-").replace("_", "-")
    
    print(f"\n📋 Adding project:")
    print(f"   Name: {name}")
    print(f"   Path: {expanded_path}")
    print(f"   ID: {project_id}")
    if description:
        print(f"   Description: {description}")
    
    confirm = input("\nAdd this project? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    try:
        # Add to config
        config = ConfigManager()
        
        # Create new source
        new_source = {
            "id": project_id,
            "name": name,
            "path": f"/host{expanded_path.replace(os.path.expanduser('~'), '')}",
            "type": "local",
            "enabled": True,
            "description": description,
            "patterns": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.java", "*.go", "*.rs", "*.rb", "*.php"],
            "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*", "dist", "build", "target", "vendor"]
        }
        
        # Add to local sources
        if "local" not in config.sources:
            config.sources["local"] = []
        
        config.sources["local"].append(new_source)
        
        # Save config
        config.save()
        
        print(f"✅ Project '{name}' added successfully!")
        print(f"   Path: {new_source['path']}")
        print(f"   Use 'ingest' to index this project")
        
    except Exception as e:
        logger.error(f"Failed to add source: {e}")
        print(f"❌ Failed to add source: {e}")


def _remove_source():
    """Remove a configured source."""
    print("\n🗑️  Remove Source\n")
    
    try:
        config = ConfigManager()
        
        if not config.sources:
            print("No sources configured.")
            return
        
        # Show available sources
        print("Available sources:")
        source_count = 0
        for source_type, source_list in config.sources.items():
            for source in source_list:
                source_count += 1
                print(f"  {source_count}. {source.name} ({source.id}) - {source_type}")
        
        if source_count == 0:
            print("No sources to remove.")
            return
        
        # Get selection
        try:
            selection = int(input(f"\nEnter source number (1-{source_count}): ").strip())
            if selection < 1 or selection > source_count:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        # Find and remove source
        source_count = 0
        for source_type, source_list in list(config.sources.items()):
            for i, source in enumerate(source_list):
                source_count += 1
                if source_count == selection:
                    # Confirm removal
                    confirm = input(f"\nRemove '{source.name}' ({source.id})? (y/N): ").strip().lower()
                    if confirm != 'y':
                        print("❌ Cancelled")
                        return
                    
                    # Remove source
                    source_list.pop(i)
                    
                    # Remove empty source types
                    if not source_list:
                        del config.sources[source_type]
                    
                    # Save config
                    config.save()
                    
                    print(f"✅ Source '{source.name}' removed successfully!")
                    return
        
        print("❌ Source not found")
        
    except Exception as e:
        logger.error(f"Failed to remove source: {e}")
        print(f"❌ Failed to remove source: {e}")


def run_query():
    """Run a query using the knowledge engine."""
    print("❓ Ask a question about your documentation:")
    question = input("Question: ").strip()
    
    if not question:
        print("Please provide a question.")
        return
    
    print(f"\n🔍 Searching for: '{question}'")
    print("Please wait...\n")
    
    try:
        # Initialize knowledge engine
        knowledge_engine = KnowledgeEngine()
        
        # Process the query
        response = knowledge_engine.query(question)
        
        # Display the answer
        print("💡 Answer:")
        print(response.answer)
        print()
        
        # Display sources
        if response.sources:
            print("📚 Sources:")
            for i, source in enumerate(response.sources, 1):
                print(f"  {i}. {source.source} (Score: {source.score:.2f})")
                if source.metadata.get('file_path'):
                    print(f"     File: {source.metadata['file_path']}")
                print()
            
            print(f"Confidence: {response.confidence:.2f}")
        else:
            print("No sources found.")
            
    except Exception as e:
        logger.error(f"Query failed: {e}")
        print(f"❌ Query failed: {e}")


def run_status():
    """Show system status and health."""
    print("📊 System Status:\n")
    
    try:
        # Check knowledge engine
        knowledge_engine = KnowledgeEngine()
        stats = knowledge_engine.get_collection_stats()
        
        print("🔍 Knowledge Engine:")
        print(f"   Status: {stats['status']}")
        print(f"   Documents: {stats['total_documents']}")
        print(f"   Collection: {stats['collection_name']}")
        
        # Check configuration
        config = ConfigManager()
        enabled_sources = []
        for source_list in config.sources.values():
            enabled_sources.extend([s for s in source_list if s.enabled])
        
        print(f"\n⚙️  Configuration:")
        print(f"   Enabled sources: {len(enabled_sources)}")
        
        # Check data ingestion engine
        ingestion_engine = DataIngestionEngine()
        print(f"\n📥 Data Ingestion:")
        print(f"   Sources configured: {len(ingestion_engine.sources)}")
        
        print("\n✅ All systems operational!")
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        print(f"❌ Status check failed: {e}")


if __name__ == "__main__":
    main()
