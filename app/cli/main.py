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
    stackguide status
        """
    )
    
    parser.add_argument(
        "command",
        choices=["query", "interactive", "ingest", "status"],
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
        elif args.command == "status":
            show_status()
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
    
    # TODO: Initialize DataIngestionEngine and run ingestion
    # engine = DataIngestionEngine()
    # engine.ingest_all()
    
    print("Ingestion functionality coming soon!")
    print("Make sure the StackGuide services are running with 'make dev'")


def show_status():
    """Show system status."""
    print("📊 StackGuide System Status")
    print("=" * 30)
    
    # TODO: Check service health and show status
    print("Status checking coming soon!")
    print("Make sure the StackGuide services are running with 'make dev'")


if __name__ == "__main__":
    main()
