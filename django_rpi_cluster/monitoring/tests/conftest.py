import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_psutil():
    """
    Fixture to mock psutil functions used in the views.
    """
    with patch('monitoring.views.psutil') as mock_psutil:
        # Mock CPU information
        mock_psutil.cpu_percent.return_value = [10.0, 20.0, 30.0, 40.0]
        mock_psutil.cpu_count.return_value = 4

        # Mock CPU frequency
        cpu_freq_mock = MagicMock()
        cpu_freq_mock.current = 2000.0
        cpu_freq_mock.min = 1000.0
        cpu_freq_mock.max = 3000.0
        mock_psutil.cpu_freq.return_value = cpu_freq_mock

        # Mock memory information
        memory_mock = MagicMock()
        memory_mock.total = 8589934592  # 8 GB
        memory_mock.available = 4294967296  # 4 GB
        memory_mock.used = 4294967296  # 4 GB
        memory_mock.free = 4294967296  # 4 GB
        memory_mock.percent = 50.0
        mock_psutil.virtual_memory.return_value = memory_mock

        # Mock disk information
        disk_mock = MagicMock()
        disk_mock.total = 107374182400  # 100 GB
        disk_mock.used = 32212254720  # 30 GB
        disk_mock.free = 75161927680  # 70 GB
        disk_mock.percent = 30.0
        mock_psutil.disk_usage.return_value = disk_mock

        # Mock network information
        network_mock = MagicMock()
        network_mock.bytes_sent = 1000000
        network_mock.bytes_recv = 2000000
        network_mock.packets_sent = 1000
        network_mock.packets_recv = 2000
        network_mock.errin = 0
        network_mock.errout = 0
        network_mock.dropin = 0
        network_mock.dropout = 0
        mock_psutil.net_io_counters.return_value = network_mock

        # Mock boot time
        mock_psutil.boot_time.return_value = 1626912000  # July 22, 2021 00:00:00 UTC

        # Mock load average
        mock_psutil.getloadavg.return_value = (1.0, 1.5, 2.0)

        # Mock process count
        mock_psutil.pids.return_value = list(range(100))

        yield mock_psutil
