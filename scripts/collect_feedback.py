#!/usr/bin/env python3
"""
StackGuide Feedback Collection Script

This script automatically collects system metrics and performance data
to help with feedback collection when testing on work computers.
"""

import json
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, timeout=30):
    """Run a command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def collect_system_info():
    """Collect basic system information."""
    info = {
        "timestamp": datetime.now().isoformat(),
        "system": {}
    }
    
    # OS info
    if sys.platform == "darwin":  # macOS
        stdout, stderr, code = run_command("sw_vers -productVersion")
        if code == 0:
            info["system"]["os"] = f"macOS {stdout}"
        else:
            info["system"]["os"] = "macOS (version unknown)"
    elif sys.platform.startswith("linux"):
        stdout, stderr, code = run_command("cat /etc/os-release | grep PRETTY_NAME")
        if code == 0:
            os_name = stdout.split('=')[1].strip('"')
            info["system"]["os"] = os_name
        else:
            info["system"]["os"] = "Linux (distribution unknown)"
    elif sys.platform == "win32":
        info["system"]["os"] = "Windows"
    
    # Python version
    info["system"]["python"] = sys.version
    
    # Docker info
    stdout, stderr, code = run_command("docker --version")
    if code == 0:
        info["system"]["docker"] = stdout
    else:
        info["system"]["docker"] = "Not available"
    
    return info

def collect_stackguide_status():
    """Collect StackGuide system status."""
    status = {}
    
    # Check if containers are running
    stdout, stderr, code = run_command("docker compose ps --format json")
    if code == 0:
        try:
            containers = []
            for line in stdout.split('\n'):
                if line.strip():
                    containers.append(json.loads(line))
            status["containers"] = containers
        except json.JSONDecodeError:
            status["containers"] = "Error parsing container status"
    else:
        status["containers"] = "Error getting container status"
    
    # Check disk usage
    stdout, stderr, code = run_command("df -h .")
    if code == 0:
        status["disk_usage"] = stdout
    else:
        status["disk_usage"] = "Error getting disk usage"
    
    # Check memory usage
    if sys.platform == "darwin":  # macOS
        stdout, stderr, code = run_command("vm_stat")
        if code == 0:
            status["memory_info"] = stdout
    elif sys.platform.startswith("linux"):
        stdout, stderr, code = run_command("free -h")
        if code == 0:
            status["memory_info"] = stdout
    
    return status

def collect_performance_metrics():
    """Collect performance metrics."""
    metrics = {}
    
    # Test query response time
    start_time = time.time()
    stdout, stderr, code = run_command("docker compose exec api python -c 'from app.core.knowledge import KnowledgeEngine; print(\"OK\")'")
    end_time = time.time()
    
    metrics["api_response_time"] = f"{(end_time - start_time) * 1000:.2f}ms"
    
    # Check collection stats
    stdout, stderr, code = run_command("docker compose exec api python -c 'from app.core.knowledge import KnowledgeEngine; e = KnowledgeEngine(); print(e.get_collection_stats())'")
    if code == 0:
        try:
            # Try to parse the output as JSON
            stats_str = stdout.replace("'", '"')
            stats = json.loads(stats_str)
            metrics["collection_stats"] = stats
        except json.JSONDecodeError:
            metrics["collection_stats"] = stdout
    else:
        metrics["collection_stats"] = "Error getting collection stats"
    
    return metrics

def generate_feedback_report():
    """Generate a comprehensive feedback report."""
    print("🔍 Collecting StackGuide feedback data...")
    
    report = {
        "feedback_collection": {
            "script_version": "1.0.0",
            "collection_date": datetime.now().isoformat()
        },
        "system_info": collect_system_info(),
        "stackguide_status": collect_stackguide_status(),
        "performance_metrics": collect_performance_metrics()
    }
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stackguide_feedback_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Feedback data saved to: {filename}")
    print("\n📊 Collected Data:")
    print(f"   - System info: {len(report['system_info'])} items")
    print(f"   - StackGuide status: {len(report['stackguide_status'])} items")
    print(f"   - Performance metrics: {len(report['performance_metrics'])} items")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Fill out the feedback template: docs/FEEDBACK_TEMPLATE.md")
    print(f"   2. Include this data file: {filename}")
    print(f"   3. Send both files back to us")
    
    return filename

def main():
    """Main function."""
    print("🚀 StackGuide Feedback Collection")
    print("=" * 40)
    
    try:
        filename = generate_feedback_report()
        print(f"\n🎯 Feedback collection complete!")
        print(f"   Report saved as: {filename}")
        
    except Exception as e:
        print(f"❌ Error collecting feedback: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
