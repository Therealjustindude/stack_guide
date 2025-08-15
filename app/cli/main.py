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


def main():
    """Main CLI entry point."""
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


def run_help():
    """Show available commands."""
    print("\n📚 Available Commands:")
    print("  ingest   - Ingest data from configured sources")
    print("  sources  - View configured data sources")
    print("  query    - Ask a question about your documentation")
    print("  status   - Show system status and health")
    print("  help     - Show this help message")
    print("  quit     - Exit the CLI\n")


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
    """Display configured data sources."""
    print("📁 Configured Data Sources:\n")
    
    try:
        config = ConfigManager()
        
        if not config.sources:
            print("No sources configured. Edit config/sources.json to add sources.")
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
