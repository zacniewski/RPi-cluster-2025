from datetime import datetime
from decouple import config
from django.shortcuts import render
import json
import psutil
from django.conf import settings

# Note: paramiko needs to be installed with: pip install paramiko
# or by running: uv pip install -e . (if using uv)
try:
    import paramiko
except ImportError:
    # This allows the code to be syntactically correct even if paramiko isn't installed
    # In a real environment, paramiko would need to be installed
    paramiko = None

# Create your views here.
def dashboard(request):
    """
    View function for the monitoring dashboard.
    Displays system status information using Bulma cards with chess icons.
    """
    context = {
        'page_title': 'Dashboard',
    }
    return render(request, 'monitoring/dashboard.html', context)

def system_parameters(request):
    """
    View a function that displays detailed system parameters using psutil.
    Shows CPU, memory, disk, network, and other system information.
    """
    # Get CPU information
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    
    # Get memory information
    memory = psutil.virtual_memory()
    
    # Get disk information
    disk = psutil.disk_usage('/')
    
    # Get network information
    network = psutil.net_io_counters()
    
    # Get boot time
    boot_time = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d, %H:%M:%S")
    
    # Get a system load
    load_avg = psutil.getloadavg()
    
    # Get process information
    process_count = len(psutil.pids())
    
    context = {
        "page_title": "System Parameters",
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq": cpu_freq,
        "memory": memory,
        "disk": disk,
        "network": network,
        "boot_time": boot_time,
        "load_avg": load_avg,
        "process_count": process_count,
    }

    return render(request, 'monitoring/system_parameters.html', context)

def remote_script_execution(request):
    """
    View a function that connects to a remote server via SSH,
    executes a Python script, and displays the results.
    """
    # SSH connection parameters
    ssh_host = '192.168.18.101'
    ssh_port = 22
    ssh_username = 'artur'
    ssh_password = config('SSH_PASSWORD')  # In production, use environment variables or settings
    remote_script = 'CLUSTER/psutil_data.py'
    
    script_output = ''
    error_message = ''
    connection_status = 'Not Connected'
    
    try:
        if paramiko is None:
            error_message = "Paramiko module is not installed. Please install it with 'pip install paramiko'."
        else:
            # Create an SSH client
            ssh_client = paramiko.SSHClient()
            # Automatically add the server's host key (this is insecure for production)
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to the remote server
            ssh_client.connect(
                hostname=ssh_host,
                port=ssh_port,
                username=ssh_username,
                password=ssh_password,
                timeout=10
            )
            connection_status = 'Connected'
            
            # Execute the Python script
            stdin, stdout, stderr = ssh_client.exec_command(f'python {remote_script}')
            # Get the output
            script_output = stdout.read().decode('utf-8')
            script_output = script_output.replace("'", '"')
            print(len(script_output))
            print(len(script_output.strip()))
            print(script_output[355:])
            y = json.loads(script_output)
            error_output = stderr.read().decode('utf-8')
            
            if error_output:
                error_message = f"Script execution error: {error_output}"
            
            # Close the connection
            ssh_client.close()
            connection_status = 'Disconnected'
            
    except Exception as e:
        error_message = f"Error: {str(e)}"
    
    # Prepare context for the template
    context = {
        'page_title': 'Remote Script Execution',
        'connection_status': connection_status,
        'script_output': script_output,
        'memory': y["memory"],
        'error_message': error_message,
        'ssh_host': ssh_host,
        'ssh_username': ssh_username,
        'remote_script': remote_script,
        'execution_time': datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
    }
    
    return render(request, 'monitoring/remote_script.html', context)
