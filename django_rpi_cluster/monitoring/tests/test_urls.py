import pytest
from django.urls import reverse, resolve

class TestUrls:
    """Tests for URL routing."""

    def test_dashboard_url_resolves(self):
        """Test that the dashboard URL resolves to the dashboard view."""
        url = reverse('monitoring:dashboard')
        assert url == '/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:dashboard'

    def test_system_parameters_url_resolves(self):
        """Test that the system_parameters URL resolves to the system_parameters view."""
        url = reverse('monitoring:system_parameters')
        assert url == '/system-parameters/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:system_parameters'

    # Test URL patterns for remote script execution
    # We're testing the URL routing but not the view functionality
    def test_remote_script_url_resolves(self):
        """Test that the remote_script URL resolves to the remote_script_execution view."""
        url = reverse('monitoring:remote_script')
        assert url == '/remote-script/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:remote_script'

    def test_remote_script_queen_url_resolves(self):
        """Test that the remote_script_queen URL resolves to the remote_script_execution view with Queen parameter."""
        url = reverse('monitoring:remote_script_queen')
        assert url == '/remote-script/queen/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:remote_script_queen'
        assert resolver.kwargs == {'machine': 'Queen'}

    def test_remote_script_rook_url_resolves(self):
        """Test that the remote_script_rook URL resolves to the remote_script_execution view with Rook parameter."""
        url = reverse('monitoring:remote_script_rook')
        assert url == '/remote-script/rook/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:remote_script_rook'
        assert resolver.kwargs == {'machine': 'Rook'}

    def test_remote_script_knight_url_resolves(self):
        """Test that the remote_script_knight URL resolves to the remote_script_execution view with Knight parameter."""
        url = reverse('monitoring:remote_script_knight')
        assert url == '/remote-script/knight/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:remote_script_knight'
        assert resolver.kwargs == {'machine': 'Knight'}

    def test_remote_script_pawn_url_resolves(self):
        """Test that the remote_script_pawn URL resolves to the remote_script_execution view with Pawn parameter."""
        url = reverse('monitoring:remote_script_pawn')
        assert url == '/remote-script/pawn/'
        resolver = resolve(url)
        assert resolver.view_name == 'monitoring:remote_script_pawn'
        assert resolver.kwargs == {'machine': 'Pawn'}
