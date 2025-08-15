#!/usr/bin/env python3
"""
StackGuide CLI - Local-first AI Knowledge Assistant

Usage:
    stackguide query "your question here"
    stackguide interactive
    stackguide ingest
    stackguide status
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add the app directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge import KnowledgeEngine
from core.ingestion import DataIngestionEngine
from utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="StackGuide - Local-first AI Knowledge Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    stackguide query "How do I set up my development environment?"
    stackguide query "Where is the payment integration code?"
    stackguide interactive
    stackguide ingest
    stackguide search "Docker configuration"
    stackguide status
    stackguide sources
        """
    )
    
    parser.add_argument(
        "command",
        choices=["query", "interactive", "ingest", "status", "search", "sources"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "query_text",
        nargs="?",
        help="Query text (required for 'query' command)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel("DEBUG")
    
    try:
        if args.command == "query":
            if not args.query_text:
                print("Error: Query text is required for 'query' command")
                sys.exit(1)
            run_query(args.query_text)
        elif args.command == "interactive":
            run_interactive()
        elif args.command == "ingest":
            run_ingestion()
        elif args.command == "search":
            if not args.query_text:
                print("Error: Search query is required for 'search' command")
                sys.exit(1)
            run_search(args.query_text)
        elif args.command == "status":
            show_status()
        elif args.command == "sources":
            run_sources()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_query(query_text: str):
    """Run a single query and display results."""
    print(f"🔍 Query: {query_text}")
    print("=" * 50)
    
    # TODO: Initialize KnowledgeEngine and run query
    # engine = KnowledgeEngine()
    # results = engine.query(query_text)
    # display_results(results)
    
    print("Query functionality coming soon!")
    print("Make sure the StackGuide services are running with 'make dev'")


def run_interactive():
    """Start interactive CLI mode."""
    print("🚀 StackGuide Interactive Mode")
    print("Type 'quit' or 'exit' to end the session")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n💬 Ask a question: ").strip()
            
            if query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
                
            run_query(query)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


def run_ingestion():
    """Run data ingestion process."""
    print("📚 Starting data ingestion...")
    
    try:
        # Initialize ingestion engine (will load sources from config)
        engine = DataIngestionEngine()
        
        # Check if we have configured sources
        if not engine.sources:
            print("⚠️  No data sources configured")
            print("💡 Add sources to config/sources.json or use the CLI to configure them")
            return
        
        print(f"📁 Found {len(engine.sources)} configured sources")
        for source in engine.sources:
            print(f"   - {source['config'].name if 'config' in source else 'Unknown'}: {source['path']}")
        
        # Run ingestion
        print("🔄 Processing documents...")
        result = engine.ingest_all(force_reindex=True)
        
        print(f"✅ Ingestion complete!")
        print(f"📁 Files processed: {result.files_processed}")
        print(f"📄 Chunks created: {result.chunks_created}")
        print(f"⏱️  Processing time: {result.processing_time:.2f}s")
        
        if result.errors:
            print(f"⚠️  Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"   - {error}")
        
        if result.sources_updated:
            print(f"🔄 Sources updated: {len(result.sources_updated)}")
            for source in result.sources_updated:
                print(f"   - {source}")
                
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        print("Make sure the StackGuide services are running with 'make dev'")


def run_search(query_text: str):
    """Search ingested documents."""
    print(f"🔍 Searching for: {query_text}")
    print("=" * 50)
    
    try:
        # Initialize ingestion engine
        engine = DataIngestionEngine()
        
        # Search for relevant chunks
        results = engine.search_chunks(query_text, n_results=5)
        
        if not results:
            print("❌ No results found")
            print("Make sure you've run 'ingest' first to index documents")
            return
        
        print(f"✅ Found {len(results)} relevant chunks:")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"📄 Result {i}:")
            print(f"   File: {result['metadata']['source_file']}")
            print(f"   Section: {result['metadata']['section']}")
            print(f"   Content: {result['content'][:200]}...")
            if result.get('distance'):
                print(f"   Relevance: {1 - result['distance']:.2f}")
            print()
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        print("Make sure the StackGuide services are running with 'make dev'")


def show_status():
    """Show system status."""
    print("📊 StackGuide System Status")
    print("=" * 30)
    
    # TODO: Check service health and show status
    print("Status checking coming soon!")
    print("Make sure the StackGuide services are running with 'make dev'")


def run_sources():
    """Manage data sources."""
    print("🔧 Data Source Management")
    print("=" * 30)
    
    try:
        from core.config import ConfigManager
        
        config = ConfigManager()
        enabled_sources = config.get_enabled_sources()
        
        if not enabled_sources:
            print("⚠️  No data sources configured")
            print("💡 Add sources to config/sources.json or use the CLI to configure them")
            return
        
        print(f"📁 Found {len(enabled_sources)} enabled sources:")
        print()
        
        for source in enabled_sources:
            status = "✅ Enabled" if source.enabled else "❌ Disabled"
            print(f"{source.name} ({source.type})")
            print(f"   ID: {source.id}")
            print(f"   Path: {source.path}")
            print(f"   Description: {source.description}")
            print(f"   Status: {status}")
            if source.patterns:
                print(f"   Patterns: {', '.join(source.patterns)}")
            if source.exclude_patterns:
                print(f"   Exclude: {', '.join(source.exclude_patterns)}")
            print()
        
        print("💡 Use 'stackguide sources add <type> <path>' to add new sources")
        print("💡 Edit config/sources.json to modify source configurations")
        
    except Exception as e:
        print(f"❌ Error managing sources: {e}")
        print("Make sure the StackGuide services are running with 'make dev'")


if __name__ == "__main__":
    main()
