#!/usr/bin/env pwsh

# StackGuide - Local-first AI Knowledge Assistant
# PowerShell script for easy command execution

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Query
)

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# Function to show help
function Show-Help {
    Write-Host "$Blue🚀 StackGuide - Local-first AI Knowledge Assistant$Reset"
    Write-Host ""
    Write-Host "$GreenAvailable Commands:$Reset"
    Write-Host "  start           - Start development environment and open CLI"
    Write-Host "  start-gpu       - Start development environment with GPU support"
    Write-Host "  docker-build    - Build containers without starting them"
    Write-Host "  docker-build-gpu- Build containers with GPU support (no start)"
    Write-Host "  cli             - Open interactive CLI"
    Write-Host "  ingest          - Ingest data from local sources"
    Write-Host "  ingest-url      - Ingest specific URLs (Confluence, Notion, GitHub)"
    Write-Host "  query <text>    - Run a specific query"
    Write-Host "  status          - Show system status and health"
    Write-Host "  logs            - View all service logs"
    Write-Host "  stop            - Stop all services"
    Write-Host "  restart         - Restart all services"
    Write-Host "  clean           - Clean up containers and images"
    Write-Host "  help            - Show this help message"
    Write-Host ""
    Write-Host "$YellowExamples:$Reset"
    Write-Host "  stackguide start"
    Write-Host "  stackguide ingest-url"
    Write-Host "  stackguide query 'How do I set up the database?'"
    Write-Host "  stackguide status"
}

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-Host "$Red❌ Docker is not running. Please start Docker and try again.$Reset"
        exit 1
    }
}

# Function to check if services are running
function Test-Services {
    try {
        $result = docker compose ps | Select-String "Up"
        return $result -ne $null
    }
    catch {
        return $false
    }
}

# Function to build containers
function Build-Containers {
    param([string]$Profile = "cpu")
    
    Write-Host "$Blue🔧 Building StackGuide containers...$Reset"
    Set-Location $PSScriptRoot
    
    if ($Profile -eq "gpu") {
        Write-Host "$Blue🔧 Using GPU profile...$Reset"
        docker compose -f docker-compose.dev.yml --profile gpu build
    }
    else {
        Write-Host "$Blue🔧 Using CPU profile...$Reset"
        docker compose -f docker-compose.dev.yml build
    }
    
    Write-Host "$Green✅ Containers built successfully!$Reset"
    if ($Profile -eq "gpu") {
        Write-Host "$Blue💡 Use 'stackguide start-gpu' to start the services$Reset"
    }
    else {
        Write-Host "$Blue💡 Use 'stackguide start' to start the services$Reset"
    }
}

# Function to start services
function Start-Services {
    param([string]$Profile = "cpu")
    
    Write-Host "$Blue🚀 Starting StackGuide services...$Reset"
    Set-Location $PSScriptRoot
    
    if ($Profile -eq "gpu") {
        Write-Host "$Blue🔧 Using GPU profile...$Reset"
        docker compose -f docker-compose.dev.yml --profile gpu up --build -d
    }
    else {
        Write-Host "$Blue🔧 Using CPU profile...$Reset"
        docker compose -f docker-compose.dev.yml --profile cpu up --build -d
    }
    
    Write-Host "$Yellow⏳ Waiting for services to be ready...$Reset"
    Start-Sleep -Seconds 15
    
    if (Test-Services) {
        Write-Host "$Green✅ Services are running!$Reset"
        return $true
    }
    else {
        Write-Host "$Red❌ Failed to start services. Check logs with 'stackguide logs'$Reset"
        return $false
    }
}

# Function to open CLI
function Open-CLI {
    Write-Host "$Blue💻 Opening StackGuide CLI...$Reset"
    Set-Location $PSScriptRoot
    docker compose exec api python -m cli.main
}

# Function to run a query
function Run-Query {
    param([string]$QueryText)
    
    if ([string]::IsNullOrEmpty($QueryText)) {
        Write-Host "$Red❌ Please provide a query. Usage: stackguide query 'your question here'$Reset"
        exit 1
    }
    
    Write-Host "$Blue🔍 Running query: $QueryText$Reset"
    Set-Location $PSScriptRoot
    
    # Check if services are running, start if needed
    if (-not (Test-Services)) {
        Start-Services
    }
    
    # Run the query
    $pythonCode = @"
from core.knowledge import KnowledgeEngine
engine = KnowledgeEngine()
response = engine.query('$QueryText')
print('\n📚 Answer:')
print(response.answer)
print(f'\n🎯 Confidence: {response.confidence:.2f}')
if response.sources:
    print('\n📖 Sources:')
    for i, source in enumerate(response.sources[:3], 1):
        print(f'{i}. {source.source} (Relevance: {source.score:.2f})')
"@
    
    docker compose exec api python -c $pythonCode
}

# Function to show status
function Show-Status {
    Write-Host "$Blue📊 StackGuide Status$Reset"
    Write-Host "=================="
    Set-Location $PSScriptRoot
    
    # Check if services are running
    if (Test-Services) {
        Write-Host "$Green✅ Services are running$Reset"
        Write-Host ""
        Write-Host "$Blue📋 Service Details:$Reset"
        docker compose ps
        Write-Host ""
        Write-Host "$Blue🔍 Health Check:$Reset"
        docker compose exec api python -c "from cli.main import run_status; run_status()"
    }
    else {
        Write-Host "$Red❌ Services are not running$Reset"
        Write-Host "Use 'stackguide start' to start the services"
    }
}

# Function to show logs
function Show-Logs {
    Write-Host "$Blue📋 StackGuide Logs$Reset"
    Set-Location $PSScriptRoot
    docker compose logs -f
}

# Function to stop services
function Stop-Services {
    Write-Host "$Yellow🛑 Stopping StackGuide services...$Reset"
    Set-Location $PSScriptRoot
    docker compose down
    Write-Host "$Green✅ Services stopped$Reset"
}

# Function to restart services
function Restart-Services {
    Write-Host "$Yellow🔄 Restarting StackGuide services...$Reset"
    Stop-Services
    Start-Sleep -Seconds 2
    Start-Services
}

# Function to clean up
function Clean-Up {
    Write-Host "$Yellow🧹 Cleaning up StackGuide...$Reset"
    Set-Location $PSScriptRoot
    docker compose down -v --remove-orphans
    docker system prune -f
    Write-Host "$Green✅ Cleanup complete$Reset"
}

# Main script logic
function Main {
    # Check if Docker is running
    Test-Docker
    
    switch ($Command) {
        "start" {
            $success = Start-Services
            if ($success) {
                Write-Host "$Green🎉 StackGuide is ready!$Reset"
                Write-Host "$Blue💡 Use 'stackguide cli' to open the interactive CLI$Reset"
            }
        }
        "start-gpu" {
            $success = Start-Services "gpu"
            if ($success) {
                Write-Host "$Green🎉 StackGuide is ready with GPU support!$Reset"
                Write-Host "$Blue💡 Use 'stackguide cli' to open the interactive CLI$Reset"
            }
        }
        "docker-build" {
            Build-Containers
        }
        "docker-build-gpu" {
            Build-Containers "gpu"
        }
        "cli" {
            if (-not (Test-Services)) {
                Write-Host "$Yellow⚠️  Starting services first...$Reset"
                Start-Services
            }
            Open-CLI
        }
        "ingest" {
            if (-not (Test-Services)) {
                Write-Host "$Yellow⚠️  Starting services first...$Reset"
                Start-Services
            }
            Write-Host "$Blue📚 Starting data ingestion...$Reset"
            Set-Location $PSScriptRoot
            docker compose exec api python -c "from cli.main import run_ingestion; run_ingestion()"
        }
        "ingest-url" {
            if (-not (Test-Services)) {
                Write-Host "$Yellow⚠️  Starting services first...$Reset"
                Start-Services
            }
            Open-CLI
        }
        "query" {
            Run-Query $Query
        }
        "status" {
            Show-Status
        }
        "logs" {
            Show-Logs
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "clean" {
            Clean-Up
        }
        "help" {
            Show-Help
        }
        default {
            Write-Host "$Red❌ Unknown command: $Command$Reset"
            Write-Host ""
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main
