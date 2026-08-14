# System Telemetry Exporter

A clean, metrics collector that polls Linux kernel telemetry directly via the `/proc` filesystem and streams formatted JSON records.

## Features
- **Kernel-Level Scanning**: Parses `/proc/stat` and `/proc/meminfo` without requiring root privileges or heavy external dependencies.
- **JSON Streaming**: Outputs line-delimited performance logs suitable for ingestion by log shippers or local dashboards.

