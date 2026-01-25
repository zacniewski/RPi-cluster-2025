# RPi Cluster Monitoring Application

This is a Django-based web application for monitoring the Raspberry Pi cluster.

## Overview

The application provides:
- A dashboard with an overview of all machines in the cluster.
- Detailed system parameters for the local machine.
- Remote script execution to gather system parameters from other machines in the cluster.

## Getting Started

1. Ensure you have `uv` installed.
2. Install dependencies:
   ```bash
   uv pip install -e .
   ```
3. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Documentation

For more detailed information, see the [main documentation](../docs/README.md).
Specific details about the remote script execution can be found in [README_REMOTE_SCRIPT.md](README_REMOTE_SCRIPT.md).
