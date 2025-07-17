from datetime import datetime
from django.shortcuts import render
import psutil

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
    View function that displays detailed system parameters using psutil.
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
    
    # Get system load
    load_avg = psutil.getloadavg()
    
    # Get process information
    process_count = len(psutil.pids())
    
    context = {
        'page_title': 'System Parameters',
        'cpu_percent': cpu_percent,
        'cpu_count': cpu_count,
        'cpu_freq': cpu_freq,
        'memory': memory,
        'disk': disk,
        'network': network,
        'boot_time': boot_time,
        'load_avg': load_avg,
        'process_count': process_count,
    }
    
    return render(request, 'monitoring/system_parameters.html', context)
