"""Tests for the utilities module."""

import ssl
from unittest.mock import MagicMock, patch

from requests.adapters import HTTPAdapter
from requests.sessions import Session

from mcp_atlassian.utils import (
    SSLIgnoreAdapter,
    configure_ssl_verification,
    is_atlassian_cloud_url,
)


def test_ssl_ignore_adapter_cert_verify():
    """Test that SSLIgnoreAdapter overrides cert verification."""
    # Arrange
    adapter = SSLIgnoreAdapter()
    connection = MagicMock()
    url = "https://example.com"
    cert = None

    # Mock the super class's cert_verify method
    with patch.object(HTTPAdapter, "cert_verify") as mock_super_cert_verify:
        # Act
        adapter.cert_verify(
            connection, url, verify=True, cert=cert
        )  # Pass True, but expect False to be used

        # Assert
        mock_super_cert_verify.assert_called_once_with(
            connection, url, verify=False, cert=cert
        )


def test_ssl_ignore_adapter_init_poolmanager():
    """Test that SSLIgnoreAdapter properly initializes the connection pool with SSL verification disabled."""
    # Arrange
    adapter = SSLIgnoreAdapter()

    # Mock PoolManager
    with patch("mcp_atlassian.utils.PoolManager") as mock_pool_manager:
        # Mock ssl.create_default_context
        with patch(
            "mcp_atlassian.utils.ssl.create_default_context"
        ) as mock_create_context:
            mock_context = MagicMock()
            mock_create_context.return_value = mock_context

            # Act
            adapter.init_poolmanager(5, 10, block=True)

            # Assert
            mock_create_context.assert_called_once()
            assert mock_context.check_hostname is False
            assert mock_context.verify_mode == ssl.CERT_NONE

            # Verify PoolManager was called with our context
            mock_pool_manager.assert_called_once()
            _, kwargs = mock_pool_manager.call_args
            assert kwargs["num_pools"] == 5
            assert kwargs["maxsize"] == 10
            assert kwargs["block"] is True
            assert kwargs["ssl_context"] == mock_context


def test_configure_ssl_verification_disabled():
    """Test configure_ssl_verification when SSL verification is disabled."""
    # Arrange
    service_name = "TestService"
    url = "https://test.example.com/path"
    session = MagicMock()  # Use MagicMock instead of actual Session
    ssl_verify = False

    with patch("mcp_atlassian.utils.SSLIgnoreAdapter") as mock_adapter_class:
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter

        # Act
        configure_ssl_verification(service_name, url, session, ssl_verify)

        # Assert
        mock_adapter_class.assert_called_once()
        # Verify the adapter is mounted for both http and https
        assert session.mount.call_count == 2
        session.mount.assert_any_call("https://test.example.com", mock_adapter)
        session.mount.assert_any_call("http://test.example.com", mock_adapter)


def test_configure_ssl_verification_enabled():
    """Test configure_ssl_verification when SSL verification is enabled."""
    # Arrange
    service_name = "TestService"
    url = "https://test.example.com/path"
    session = MagicMock()  # Use MagicMock instead of actual Session
    ssl_verify = True

    with patch("mcp_atlassian.utils.SSLIgnoreAdapter") as mock_adapter_class:
        # Act
        configure_ssl_verification(service_name, url, session, ssl_verify)

        # Assert
        mock_adapter_class.assert_not_called()
        assert session.mount.call_count == 0


def test_is_atlassian_cloud_url():
    """Test the is_atlassian_cloud_url function correctly identifies cloud vs server URLs."""
    # Test Cloud URLs
    assert is_atlassian_cloud_url("https://example.atlassian.net") is True
    assert is_atlassian_cloud_url("https://company.atlassian.net/wiki") is True

    # Test Server/Data Center URLs
    assert is_atlassian_cloud_url("https://jira.example.com") is False
    assert is_atlassian_cloud_url("https://confluence.company.com") is False

    # Test localhost URLs
    assert is_atlassian_cloud_url("http://localhost:8080") is False
    assert is_atlassian_cloud_url("http://localhost:8090/wiki") is False

    # Test IP-based localhost URLs
    assert is_atlassian_cloud_url("http://127.0.0.1:8080") is False
    assert is_atlassian_cloud_url("https://127.0.0.1:8090") is False


def test_configure_ssl_verification_enabled_with_real_session():
    """Test SSL verification configuration when verification is enabled using a real Session."""
    session = Session()
    original_adapters_count = len(session.adapters)

    # Configure with SSL verification enabled
    configure_ssl_verification(
        service_name="Test",
        url="https://example.com",
        session=session,
        ssl_verify=True,
    )

    # No adapters should be added when SSL verification is enabled
    assert len(session.adapters) == original_adapters_count


def test_configure_ssl_verification_disabled_with_real_session():
    """Test SSL verification configuration when verification is disabled using a real Session."""
    session = Session()
    original_adapters_count = len(session.adapters)

    # Configure with SSL verification disabled
    configure_ssl_verification(
        service_name="Test",
        url="https://example.com",
        session=session,
        ssl_verify=False,
    )

    # Should add custom adapters for http and https protocols
    assert len(session.adapters) == original_adapters_count + 2
    assert "https://example.com" in session.adapters
    assert "http://example.com" in session.adapters
    assert isinstance(session.adapters["https://example.com"], SSLIgnoreAdapter)
    assert isinstance(session.adapters["http://example.com"], SSLIgnoreAdapter)


def test_ssl_ignore_adapter():
    """Test the SSLIgnoreAdapter overrides the cert_verify method."""
    # Mock objects
    adapter = SSLIgnoreAdapter()
    conn = MagicMock()
    url = "https://example.com"
    cert = None

    # Test with verify=True - the adapter should still bypass SSL verification
    with patch.object(HTTPAdapter, "cert_verify") as mock_cert_verify:
        adapter.cert_verify(conn, url, verify=True, cert=cert)
        mock_cert_verify.assert_called_once_with(conn, url, verify=False, cert=cert)

    # Test with verify=False - same behavior
    with patch.object(HTTPAdapter, "cert_verify") as mock_cert_verify:
        adapter.cert_verify(conn, url, verify=False, cert=cert)
        mock_cert_verify.assert_called_once_with(conn, url, verify=False, cert=cert)
