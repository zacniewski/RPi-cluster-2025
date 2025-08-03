# Remote Script Execution Feature

This document describes the implementation of the Remote Script Execution feature in the RPi Cluster Monitoring application.

## Overview

The Remote Script Execution feature allows users to connect to a remote server via SSH, execute a Python script, and view the results. This feature is useful for running diagnostic or monitoring scripts on remote Raspberry Pi devices in the cluster.

## Implementation Details

### Dependencies

The feature requires the `paramiko` package for SSH connectivity. It has been added to the project dependencies in `pyproject.toml`:

```python
dependencies = [
    "django>=5.2.4",
    "psutil>=7.0.0",
    "python-decouple>=3.8",
    "paramiko>=3.3.1",
]
```

To install the dependencies, run:

```bash
# If using pip
pip install -e .

# If using uv
uv pip install -e .
```

### View Implementation

The feature is implemented in the `remote_script_execution` view function in `monitoring/views.py`. This function:

1. Establishes an SSH connection to the remote server (192.168.18.101) with username 'artur'
2. Executes the 'test_python.py' script on the remote server
3. Retrieves the output and any error messages
4. Renders a template with the results

### URL Configuration

The view is accessible at the URL path `/remote-script/` and is named 'remote_script' in the URL configuration:

```python
urlpatterns = [
    # ...
    path('remote-script/', views.remote_script_execution, name='remote_script'),
]
```

### Template

The feature uses a template file `monitoring/templates/monitoring/remote_script.html` that displays:

1. Connection information (host, username, script, status, execution time)
2. Script output or error messages
3. Navigation buttons to return to the dashboard or run the script again

### Navigation

The feature is accessible from:

1. The navigation menu in the base template
2. A card on the dashboard

## Security Considerations

In the current implementation, the SSH password is hardcoded in the view function. In a production environment, this should be replaced with:

1. Environment variables
2. Django settings with proper security measures
3. A secure key management system

Additionally, the current implementation automatically accepts the server's host key, which is insecure for production. In a production environment, known host keys should be verified.

## Future Improvements

Potential improvements to the feature include:

1. Adding a form to allow users to specify the remote server, username, and script
2. Supporting SSH key-based authentication
3. Adding the ability to upload and execute custom scripts
4. Implementing a job queue for long-running scripts
5. Adding error handling and retry mechanisms for failed connections
