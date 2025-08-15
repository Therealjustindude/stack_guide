@echo off
REM StackGuide - Local-first AI Knowledge Assistant
REM Windows batch file for easy command execution

setlocal enabledelayedexpansion

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check command line arguments
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

if "%1"=="start" goto start_services
if "%1"=="start-gpu" goto start_services_gpu
if "%1"=="docker-build" goto build_containers
if "%1"=="docker-build-gpu" goto build_containers_gpu
if "%1"=="cli" goto open_cli
if "%1"=="ingest" goto run_ingestion
if "%1"=="ingest-url" goto open_cli
if "%1"=="query" goto run_query
if "%1"=="status" goto show_status
if "%1"=="logs" goto show_logs
if "%1"=="stop" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="clean" goto clean_up

echo ❌ Unknown command: %1
echo.
goto show_help

:show_help
echo 🚀 StackGuide - Local-first AI Knowledge Assistant
echo.
echo Available Commands:
echo   start           - Start development environment and open CLI
echo   start-gpu       - Start development environment with GPU support
echo   docker-build    - Build containers without starting them
echo   docker-build-gpu- Build containers with GPU support (no start)
echo   cli             - Open interactive CLI
echo   ingest          - Ingest data from local sources
echo   ingest-url      - Ingest specific URLs (Confluence, Notion, GitHub)
echo   query ^<text^>    - Run a specific query
echo   status          - Show system status and health
echo   logs            - View all service logs
echo   stop            - Stop all services
echo   restart         - Restart all services
echo   clean           - Clean up containers and images
echo   help            - Show this help message
echo.
echo Examples:
echo   stackguide start
echo   stackguide ingest-url
echo   stackguide query "How do I set up the database?"
echo   stackguide status
goto end

:start_services
echo 🚀 Starting StackGuide services...
if "%2"=="gpu" (
    echo 🔧 Using GPU profile...
    docker compose -f docker-compose.dev.yml --profile gpu up --build -d
) else (
    echo 🔧 Using CPU profile...
    docker compose -f docker-compose.dev.yml --profile cpu up --build -d
)

echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

docker compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Failed to start services. Check logs with 'stackguide logs'
    goto end
)

echo ✅ Services are running!
echo 🎉 StackGuide is ready!
echo 💡 Use 'stackguide cli' to open the interactive CLI
goto end

:start_services_gpu
echo 🚀 Starting StackGuide services with GPU support...
docker compose -f docker-compose.dev.yml --profile gpu up --build -d

echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

docker compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Failed to start services. Check logs with 'stackguide logs'
    goto end
)

echo ✅ Services are running!
echo 🎉 StackGuide is ready with GPU support!
echo 💡 Use 'stackguide cli' to open the interactive CLI
goto end

:build_containers
echo 📦 Building StackGuide containers...
docker compose -f docker-compose.dev.yml build
echo ✅ Containers built.
goto end

:build_containers_gpu
echo 📦 Building StackGuide containers with GPU support...
docker compose -f docker-compose.dev.yml --profile gpu build
echo ✅ Containers built.
goto end

:open_cli
echo 💻 Opening StackGuide CLI...
docker compose exec api python -m cli.main
goto end

:run_ingestion
echo 📚 Starting data ingestion...
docker compose exec api python -c "from cli.main import run_ingestion; run_ingestion()"
goto end

:run_query
if "%2"=="" (
    echo ❌ Please provide a query. Usage: stackguide query "your question here"
    goto end
)

echo 🔍 Running query: %2
docker compose exec api python -c "from core.knowledge import KnowledgeEngine; engine = KnowledgeEngine(); response = engine.query('%2'); print('📚 Answer:'); print(response.answer); print(f'🎯 Confidence: {response.confidence:.2f}'); print('📖 Sources:'); [print(f'{i}. {source.source} (Relevance: {source.score:.2f})') for i, source in enumerate(response.sources[:3], 1)]"
goto end

:show_status
echo 📊 StackGuide Status
echo ==================
docker compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Services are not running
    echo Use 'stackguide start' to start the services
    goto end
)

echo ✅ Services are running
echo.
echo 📋 Service Details:
docker compose ps
echo.
echo 🔍 Health Check:
docker compose exec api python -c "from cli.main import run_status; run_status()"
goto end

:show_logs
echo 📋 StackGuide Logs
docker compose logs -f
goto end

:stop_services
echo 🛑 Stopping StackGuide services...
docker compose down
echo ✅ Services stopped
goto end

:restart_services
echo 🔄 Restarting StackGuide services...
call :stop_services
timeout /t 2 /nobreak >nul
call :start_services
goto end

:clean_up
echo 🧹 Cleaning up StackGuide...
docker compose down -v --remove-orphans
docker system prune -f
echo ✅ Cleanup complete
goto end

:end
endlocal
