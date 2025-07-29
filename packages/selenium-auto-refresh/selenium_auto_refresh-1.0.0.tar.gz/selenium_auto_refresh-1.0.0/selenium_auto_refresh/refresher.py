import threading
import time
from typing import Optional, Any


class ChromeRefresher:
    """
    Automatically refresh a Chrome tab every specified interval.
    
    Compatible with:
    - Selenium WebDriver
    - SeleniumBase Driver
    - undetected-chromedriver
    - Any driver with a .refresh() method
    
    Example:
        >>> from selenium import webdriver
        >>> from selenium_auto_refresh import ChromeRefresher
        >>> 
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://example.com")
        >>> 
        >>> refresher = ChromeRefresher(driver, interval=60)
        >>> refresher.start()  # Refresh every 60 seconds
        >>> 
        >>> # Do your work...
        >>> 
        >>> refresher.stop()   # Stop auto-refresh
        >>> driver.quit()
    """
    
    def __init__(self, driver: Any, interval: int = 60):
        """
        Initialize the ChromeRefresher.
        
        Args:
            driver: Selenium/WebDriver/undetected_chromedriver instance
                   Must have a .refresh() method
            interval: Time between refreshes in seconds (default: 60)
        
        Raises:
            AttributeError: If driver doesn't have a refresh method
            ValueError: If interval is not positive
        """
        if not hasattr(driver, 'refresh'):
            raise AttributeError("Driver must have a 'refresh' method")
        
        if interval <= 0:
            raise ValueError("Interval must be positive")
            
        self.driver = driver
        self.interval = interval
        self.running = False
        self._thread: Optional[threading.Timer] = None

    def _refresh_loop(self) -> None:
        """Internal method to handle the refresh loop."""
        if not self.running:
            return
            
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Auto-refreshing page...")
            self.driver.refresh()
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Refresh error: {e}")
        
        # Schedule next refresh
        if self.running:
            self._thread = threading.Timer(self.interval, self._refresh_loop)
            self._thread.start()

    def start(self) -> None:
        """
        Start the auto-refresh loop.
        
        Returns:
            None
        """
        if not self.running:
            self.running = True
            print(f"[{time.strftime('%H:%M:%S')}] Started auto-refresh (interval: {self.interval}s)")
            self._refresh_loop()

    def stop(self) -> None:
        """
        Stop the auto-refresh loop.
        
        Returns:
            None
        """
        self.running = False
        if self._thread:
            self._thread.cancel()
            self._thread = None
        print(f"[{time.strftime('%H:%M:%S')}] Stopped auto-refresh")

    def is_running(self) -> bool:
        """
        Check if auto-refresh is currently running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self.running

    def change_interval(self, new_interval: int) -> None:
        """
        Change the refresh interval. Takes effect on next refresh.
        
        Args:
            new_interval: New interval in seconds
            
        Raises:
            ValueError: If new_interval is not positive
        """
        if new_interval <= 0:
            raise ValueError("Interval must be positive")
            
        self.interval = new_interval
        print(f"[{time.strftime('%H:%M:%S')}] Changed interval to {new_interval}s")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

        