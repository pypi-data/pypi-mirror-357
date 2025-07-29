"""Tests for ChromeRefresher and AsyncChromeRefresher classes."""

import asyncio
import time
import threading
from unittest.mock import Mock, patch, call, AsyncMock
import pytest

from selenium_auto_refresh.refresher import ChromeRefresher, AsyncChromeRefresher


class TestChromeRefresher:
    """Test cases for ChromeRefresher class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_driver = Mock()
        self.mock_driver.refresh = Mock()
        self.mock_driver.get = Mock()

    def test_init_valid_driver(self):
        """Test initialization with valid driver."""
        refresher = ChromeRefresher(self.mock_driver, interval=30)
        
        assert refresher.driver == self.mock_driver
        assert refresher.interval == 30
        assert refresher.running is False
        assert refresher.urls == []
        assert refresher.current_url_index == 0
        assert refresher._thread is None

    def test_init_with_urls(self):
        """Test initialization with URLs."""
        urls = ["https://example.com", "https://google.com"]
        refresher = ChromeRefresher(self.mock_driver, interval=30, urls=urls)
        
        assert refresher.urls == urls
        assert refresher.current_url_index == 0

    def test_init_invalid_driver(self):
        """Test initialization with invalid driver (no refresh method)."""
        mock_driver = Mock(spec=[])  # No refresh method
        
        with pytest.raises(AttributeError, match="Driver must have a 'refresh' method"):
            ChromeRefresher(mock_driver)

    def test_init_invalid_interval_zero(self):
        """Test initialization with zero interval."""
        with pytest.raises(ValueError, match="Interval must be positive"):
            ChromeRefresher(self.mock_driver, interval=0)

    def test_init_invalid_interval_negative(self):
        """Test initialization with negative interval."""
        with pytest.raises(ValueError, match="Interval must be positive"):
            ChromeRefresher(self.mock_driver, interval=-5)

    def test_add_url(self):
        """Test adding URL to rotation."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with patch('builtins.print') as mock_print:
            refresher.add_url("https://example.com")
        
        assert "https://example.com" in refresher.urls
        assert len(refresher.urls) == 1
        mock_print.assert_called_once()

    def test_add_multiple_urls(self):
        """Test adding multiple URLs."""
        refresher = ChromeRefresher(self.mock_driver)
        
        refresher.add_url("https://example.com")
        refresher.add_url("https://google.com")
        
        assert len(refresher.urls) == 2
        assert "https://example.com" in refresher.urls
        assert "https://google.com" in refresher.urls

    def test_remove_url_success(self):
        """Test removing existing URL."""
        urls = ["https://example.com", "https://google.com"]
        refresher = ChromeRefresher(self.mock_driver, urls=urls.copy())
        
        with patch('builtins.print') as mock_print:
            result = refresher.remove_url("https://example.com")
        
        assert result is True
        assert "https://example.com" not in refresher.urls
        assert len(refresher.urls) == 1
        mock_print.assert_called_once()

    def test_remove_url_not_found(self):
        """Test removing non-existent URL."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with patch('builtins.print') as mock_print:
            result = refresher.remove_url("https://nonexistent.com")
        
        assert result is False
        mock_print.assert_called_once()

    def test_get_urls(self):
        """Test getting URLs list."""
        urls = ["https://example.com", "https://google.com"]
        refresher = ChromeRefresher(self.mock_driver, urls=urls)
        
        result = refresher.get_urls()
        
        assert result == urls
        assert result is not refresher.urls  # Should be a copy

    def test_get_urls_empty(self):
        """Test getting empty URLs list."""
        refresher = ChromeRefresher(self.mock_driver)
        
        result = refresher.get_urls()
        
        assert result == []

    def test_clear_urls(self):
        """Test clearing URLs."""
        urls = ["https://example.com", "https://google.com"]
        refresher = ChromeRefresher(self.mock_driver, urls=urls)
        refresher.current_url_index = 1
        
        with patch('builtins.print') as mock_print:
            refresher.clear_urls()
        
        assert refresher.urls == []
        assert refresher.current_url_index == 0
        mock_print.assert_called_once()

    def test_change_interval_valid(self):
        """Test changing interval with valid value."""
        refresher = ChromeRefresher(self.mock_driver, interval=30)
        
        with patch('builtins.print') as mock_print:
            refresher.change_interval(60)
        
        assert refresher.interval == 60
        mock_print.assert_called_once()

    def test_change_interval_invalid(self):
        """Test changing interval with invalid value."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with pytest.raises(ValueError, match="Interval must be positive"):
            refresher.change_interval(0)
        
        with pytest.raises(ValueError, match="Interval must be positive"):
            refresher.change_interval(-10)

    def test_is_running_false(self):
        """Test is_running method when not running."""
        refresher = ChromeRefresher(self.mock_driver)
        assert refresher.is_running() is False

    def test_is_running_true(self):
        """Test is_running method when running."""
        refresher = ChromeRefresher(self.mock_driver)
        refresher.running = True
        assert refresher.is_running() is True

    @patch('threading.Timer')
    def test_start(self, mock_timer_class):
        """Test start method."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        refresher = ChromeRefresher(self.mock_driver, interval=1)
        
        with patch('builtins.print') as mock_print:
            refresher.start()
        
        assert refresher.running is True
        mock_print.assert_called()

    def test_stop_when_not_running(self):
        """Test stop method when not running."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with patch('builtins.print') as mock_print:
            refresher.stop()
        
        assert refresher.running is False
        mock_print.assert_called_once()

    def test_stop_when_running(self):
        """Test stop method when running."""
        refresher = ChromeRefresher(self.mock_driver)
        refresher.running = True
        mock_thread = Mock()
        refresher._thread = mock_thread
        
        with patch('builtins.print') as mock_print:
            refresher.stop()
        
        assert refresher.running is False
        assert refresher._thread is None
        mock_thread.cancel.assert_called_once()
        mock_print.assert_called_once()

    def test_refresh_loop_not_running(self):
        """Test refresh loop when not running."""
        refresher = ChromeRefresher(self.mock_driver)
        refresher.running = False
        
        refresher._refresh_loop()
        
        self.mock_driver.refresh.assert_not_called()
        self.mock_driver.get.assert_not_called()

    @patch('threading.Timer')
    def test_refresh_loop_standard_refresh(self, mock_timer_class):
        """Test refresh loop with standard refresh."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        refresher = ChromeRefresher(self.mock_driver)
        refresher.running = True
        
        with patch('builtins.print') as mock_print:
            refresher._refresh_loop()
        
        self.mock_driver.refresh.assert_called_once()
        mock_timer_class.assert_called_once()
        mock_timer.start.assert_called_once()

    @patch('threading.Timer')
    def test_refresh_loop_with_urls(self, mock_timer_class):
        """Test refresh loop with URL rotation."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        urls = ["https://example.com", "https://google.com"]
        refresher = ChromeRefresher(self.mock_driver, urls=urls)
        refresher.running = True
        
        with patch('builtins.print') as mock_print:
            # First call
            refresher._refresh_loop()
        
        self.mock_driver.get.assert_called_with("https://example.com")
        assert refresher.current_url_index == 1
        
        with patch('builtins.print') as mock_print:
            # Second call
            refresher._refresh_loop()
        
        self.mock_driver.get.assert_called_with("https://google.com")
        assert refresher.current_url_index == 0  # Should wrap around

    @patch('threading.Timer')
    def test_refresh_loop_exception_handling(self, mock_timer_class):
        """Test refresh loop exception handling."""
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer
        
        self.mock_driver.refresh.side_effect = Exception("Test error")
        refresher = ChromeRefresher(self.mock_driver)
        refresher.running = True
        
        with patch('builtins.print') as mock_print:
            refresher._refresh_loop()
        
        # Should still schedule next refresh despite error
        mock_timer_class.assert_called_once()
        mock_timer.start.assert_called_once()

    def test_context_manager(self):
        """Test context manager functionality."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with patch.object(refresher, 'start') as mock_start, \
             patch.object(refresher, 'stop') as mock_stop:
            
            with refresher as r:
                assert r is refresher
                mock_start.assert_called_once()
            
            mock_stop.assert_called_once()

    def test_context_manager_with_exception(self):
        """Test context manager with exception."""
        refresher = ChromeRefresher(self.mock_driver)
        
        with patch.object(refresher, 'start') as mock_start, \
             patch.object(refresher, 'stop') as mock_stop:
            
            try:
                with refresher:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            mock_start.assert_called_once()
            mock_stop.assert_called_once()


class TestAsyncChromeRefresher:
    """Test cases for AsyncChromeRefresher class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_driver = Mock()
        self.mock_driver.refresh = Mock()
        self.mock_driver.get = Mock()

    def test_init_valid_driver(self):
        """Test initialization with valid driver."""
        refresher = AsyncChromeRefresher(self.mock_driver, interval=30)
        
        assert refresher.driver == self.mock_driver
        assert refresher.interval == 30
        assert refresher.running is False
        assert refresher.urls == []
        assert refresher.current_url_index == 0
        assert refresher._task is None

    def test_init_with_urls(self):
        """Test initialization with URLs."""
        urls = ["https://example.com", "https://google.com"]
        refresher = AsyncChromeRefresher(self.mock_driver, interval=30, urls=urls)
        
        assert refresher.urls == urls

    def test_init_invalid_driver(self):
        """Test initialization with invalid driver."""
        mock_driver = Mock(spec=[])
        
        with pytest.raises(AttributeError, match="Driver must have a 'refresh' method"):
            AsyncChromeRefresher(mock_driver)

    def test_init_invalid_interval(self):
        """Test initialization with invalid interval."""
        with pytest.raises(ValueError, match="Interval must be positive"):
            AsyncChromeRefresher(self.mock_driver, interval=-1)

    def test_add_url(self):
        """Test adding URL to rotation."""
        refresher = AsyncChromeRefresher(self.mock_driver)
        
        with patch('builtins.print') as mock_print:
            refresher.add_url("https://example.com")
        
        assert "https://example.com" in refresher.urls
        mock_print.assert_called_once()

    def test_remove_url_success(self):
        """Test removing existing URL."""
        urls = ["https://example.com", "https://google.com"]
        refresher = AsyncChromeRefresher(self.mock_driver, urls=urls.copy())
        
        with patch('builtins.print') as mock_print:
            result = refresher.remove_url("https://example.com")
        
        assert result is True
        assert "https://example.com" not in refresher.urls

    def test_get_urls(self):
        """Test getting URLs list."""
        urls = ["https://example.com", "https://google.com"]
        refresher = AsyncChromeRefresher(self.mock_driver, urls=urls)
        
        result = refresher.get_urls()
        
        assert result == urls
        assert result is not refresher.urls

    def test_clear_urls(self):
        """Test clearing URLs."""
        urls = ["https://example.com", "https://google.com"]
        refresher = AsyncChromeRefresher(self.mock_driver, urls=urls)
        
        with patch('builtins.print') as mock_print:
            refresher.clear_urls()
        
        assert refresher.urls == []
        assert refresher.current_url_index == 0

    def test_change_interval(self):
        """Test changing interval."""
        refresher = AsyncChromeRefresher(self.mock_driver, interval=30)
        
        with patch('builtins.print') as mock_print:
            refresher.change_interval(60)