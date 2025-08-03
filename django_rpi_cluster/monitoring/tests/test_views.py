import pytest
from django.urls import reverse
from datetime import datetime

@pytest.mark.django_db
class TestDashboardView:
    """Tests for the dashboard view."""

    def test_dashboard_view_status_code(self, client):
        """Test that the dashboard view returns a 200 status code."""
        url = reverse('monitoring:dashboard')
        response = client.get(url)
        assert response.status_code == 200

    def test_dashboard_view_template(self, client):
        """Test that the dashboard view uses the correct template."""
        url = reverse('monitoring:dashboard')
        response = client.get(url)
        assert 'monitoring/dashboard.html' in [t.name for t in response.templates]

    def test_dashboard_view_context(self, client):
        """Test that the dashboard view provides the correct context."""
        url = reverse('monitoring:dashboard')
        response = client.get(url)
        assert 'page_title' in response.context
        assert response.context['page_title'] == 'Dashboard'

@pytest.mark.django_db
class TestSystemParametersView:
    """Tests for the system_parameters view."""

    def test_system_parameters_view_status_code(self, client, mock_psutil):
        """Test that the system_parameters view returns a 200 status code."""
        url = reverse('monitoring:system_parameters')
        response = client.get(url)
        assert response.status_code == 200

    def test_system_parameters_view_template(self, client, mock_psutil):
        """Test that the system_parameters view uses the correct template."""
        url = reverse('monitoring:system_parameters')
        response = client.get(url)
        assert 'monitoring/system_parameters.html' in [t.name for t in response.templates]

    def test_system_parameters_view_context(self, client, mock_psutil):
        """Test that the system_parameters view provides the correct context."""
        url = reverse('monitoring:system_parameters')
        response = client.get(url)

        # Check that all expected context variables are present
        expected_context_keys = [
            'page_title', 'cpu_percent', 'cpu_count', 'cpu_freq',
            'memory', 'disk', 'network', 'boot_time', 'load_avg', 'process_count'
        ]
        for key in expected_context_keys:
            assert key in response.context

        # Check specific values
        assert response.context['page_title'] == 'System Parameters'
        assert response.context['cpu_count'] == 4
        assert response.context['cpu_percent'] == [10.0, 20.0, 30.0, 40.0]
        assert response.context['cpu_freq'].current == 2000.0
        assert response.context['memory'].percent == 50.0
        assert response.context['disk'].percent == 30.0
        assert response.context['process_count'] == 100

        # Check that boot_time is formatted correctly
        # The mock returns July 22, 2021 00:00:00 UTC
        assert '2021-07-22' in response.context['boot_time']

# Note: We are intentionally not testing the remote_script_execution view
# as per the requirements
