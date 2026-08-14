#!/usr/bin/env python3
"""
System Telemetry Exporter - Collects authorized performance metrics
directly from the Linux /proc pseudo-filesystem.
"""

import json
import sys
import time
from pathlib import Path


def get_cpu_stats():
    """Reads raw CPU utilization numbers from /proc/stat."""
    stat_file = Path("/proc/stat")
    if not stat_file.exists():
        return {}
    
    with open(stat_file, "r") as f:
        line = f.readline()  # The first line contains aggregate CPU stats
        if line.startswith("cpu "):
            parts = line.split()
            # Values: user, nice, system, idle, iowait, irq, softirq, steal, etc.
            values = [int(p) for p in parts[1:]]
            idle_time = values[3]
            total_time = sum(values)
            return {"idle": idle_time, "total": total_time}
    return {}


def calculate_cpu_percentage(prev_stats, curr_stats):
    """Computes CPU usage percentage between two snapshot intervals."""
    prev_idle = prev_stats.get("idle", 0)
    prev_total = prev_stats.get("total", 0)
    curr_idle = curr_stats.get("idle", 0)
    curr_total = curr_stats.get("total", 0)
    
    total_delta = curr_total - prev_total
    idle_delta = curr_idle - prev_idle
    
    if total_delta == 0:
        return 0.0
    
    cpu_usage = 100.0 * (1.0 - (idle_delta / total_delta))
    return round(cpu_usage, 2)


def get_memory_stats():
    """Parses /proc/meminfo for memory usage metrics."""
    meminfo_path = Path("/proc/meminfo")
    if not meminfo_path.exists():
        return {}
    
    mem_stats = {}
    with open(meminfo_path, "r") as f:
        for line in f:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]  # Grab numeric value in kB
                mem_stats[key] = int(val)
                
    total = mem_stats.get("MemTotal", 0)
    free = mem_stats.get("MemFree", 0)
    available = mem_stats.get("MemAvailable", free)
    used = total - available
    
    usage_percent = round(100.0 * used / total, 2) if total > 0 else 0.0
    
    return {
        "total_mb": round(total / 1024, 2),
        "used_mb": round(used / 1024, 2),
        "available_mb": round(available / 1024, 2),
        "usage_percent": usage_percent
    }


def main():
    print("Starting System Telemetry Exporter (Press Ctrl+C to stop)...", file=sys.stderr)
    prev_cpu = get_cpu_stats()
    time.sleep(1)
    
    try:
        while True:
            curr_cpu = get_cpu_stats()
            cpu_pct = calculate_cpu_percentage(prev_cpu, curr_cpu)
            prev_cpu = curr_cpu
            
            mem_data = get_memory_stats()
            
            telemetry_payload = {
                "timestamp": time.time(),
                "cpu_percent": cpu_pct,
                "memory": mem_data
            }
            
            # Print structured JSON line to standard output
            print(json.dumps(telemetry_payload))
            sys.stdout.flush()
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("Telemetry collection stopped.", file=sys.stderr)


if __name__ == "__main__":
    main()
