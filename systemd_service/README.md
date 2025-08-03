# Cluster Virtual Environment Service

This directory contains a systemd service file that helps make the Python virtual environment at `/home/artur/CLUSTER/.venv` accessible at system boot.

## What the Service Does

The `cluster-venv.service` file:

1. Creates a symbolic link to the virtual environment's activate script at `/home/artur/.local/bin/activate-cluster-venv`
2. Verifies the virtual environment is accessible by running a simple Python command
3. Runs at system boot after the network is available

## Installation Instructions

To install and enable the service:

1. Copy the service file to the systemd directory:
   ```bash
   sudo cp ./systemd_service/cluster-venv.service /etc/systemd/system/
   ```

2. Reload the systemd daemon to recognize the new service:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable the service to start at boot:
   ```bash
   sudo systemctl enable cluster-venv.service
   ```

4. Start the service immediately (optional):
   ```bash
   sudo systemctl start cluster-venv.service
   ```

5. Check the status of the service:
   ```bash
   sudo systemctl status cluster-venv.service
   ```

## Using the Virtual Environment

After the service has run, you can source the virtual environment in your scripts using:

```bash
source /home/artur/.local/bin/activate-cluster-venv
```

Or directly:

```bash
source /home/artur/CLUSTER/.venv/bin/activate
```

## Troubleshooting

If the service fails to start:

1. Check the service logs:
   ```bash
   journalctl -u cluster-venv.service
   ```

2. Verify that the virtual environment exists at `/home/artur/CLUSTER/.venv`

3. Ensure the user 'artur' has permission to access the virtual environment
