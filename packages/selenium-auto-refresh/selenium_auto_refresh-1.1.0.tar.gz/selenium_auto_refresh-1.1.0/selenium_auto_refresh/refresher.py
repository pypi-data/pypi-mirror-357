import threading
import time
import asyncio
from typing import Optional, Any, List


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
        >>> # Single URL refresh
        >>> refresher = ChromeRefresher(driver, interval=60)
        >>> refresher.start()  # Refresh every 60 seconds
        >>> 
        >>> # Multiple URL rotation
        >>> urls = ["https://example.com", "https://google.com", "https://github.com"]
        >>> refresher = ChromeRefresher(driver, interval=60, urls=urls)
        >>> refresher.start()  # Rotate through URLs every 60 seconds
        >>> 
        >>> # Do your work...
        >>> 
        >>> refresher.stop()   # Stop auto-refresh
        >>> driver.quit()
    """
    
    def __init__(self, driver: Any, interval: int = 60, urls: Optional[List[str]] = None):
        """
        Initialize the ChromeRefresher.
        
        Args:
            driver: Selenium/WebDriver/undetected_chromedriver instance
                   Must have a .refresh() method
            interval: Time between refreshes in seconds (default: 60)
            urls: Optional list of URLs to rotate through. If provided, will navigate
                 to each URL instead of just refreshing current page
        
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
        
        # Multiple URL support
        self.urls = urls or []
        self.current_url_index = 0

    def add_url(self, url: str) -> None:
        """
        Add URL to rotation list.
        
        Args:
            url: URL to add to the rotation
        """
        self.urls.append(url)
        print(f"[{time.strftime('%H:%M:%S')}] Added URL to rotation: {url}")

    def remove_url(self, url: str) -> bool:
        """
        Remove URL from rotation list.
        
        Args:
            url: URL to remove from rotation
            
        Returns:
            bool: True if URL was removed, False if not found
        """
        try:
            self.urls.remove(url)
            print(f"[{time.strftime('%H:%M:%S')}] Removed URL from rotation: {url}")
            return True
        except ValueError:
            print(f"[{time.strftime('%H:%M:%S')}] URL not found in rotation: {url}")
            return False

    def get_urls(self) -> List[str]:
        """
        Get current list of URLs in rotation.
        
        Returns:
            List[str]: List of URLs
        """
        return self.urls.copy()

    def clear_urls(self) -> None:
        """Clear all URLs from rotation."""
        self.urls.clear()
        self.current_url_index = 0
        print(f"[{time.strftime('%H:%M:%S')}] Cleared all URLs from rotation")

    def _refresh_loop(self) -> None:
        """Internal method to handle the refresh loop."""
        if not self.running:
            return
            
        try:
            if self.urls:
                # Navigate to next URL in rotation
                url = self.urls[self.current_url_index]
                print(f"[{time.strftime('%H:%M:%S')}] Navigating to URL ({self.current_url_index + 1}/{len(self.urls)}): {url}")
                self.driver.get(url)
                self.current_url_index = (self.current_url_index + 1) % len(self.urls)
            else:
                # Standard refresh
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
            mode = "URL rotation" if self.urls else "page refresh"
            print(f"[{time.strftime('%H:%M:%S')}] Started auto-{mode} (interval: {self.interval}s)")
            if self.urls:
                print(f"[{time.strftime('%H:%M:%S')}] URLs in rotation: {len(self.urls)}")
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


class AsyncChromeRefresher:
    """
    Asynchronously refresh a Chrome tab every specified interval.
    
    Compatible with:
    - Selenium WebDriver
    - SeleniumBase Driver
    - undetected-chromedriver
    - Any driver with a .refresh() method
    
    Example:
        >>> import asyncio
        >>> from selenium import webdriver
        >>> from selenium_auto_refresh import AsyncChromeRefresher
        >>> 
        >>> async def main():
        ...     driver = webdriver.Chrome()
        ...     driver.get("https://example.com")
        ...     
        ...     # Single URL refresh
        ...     refresher = AsyncChromeRefresher(driver, interval=60)
        ...     await refresher.start()
        ...     
        ...     # Do your async work...
        ...     await asyncio.sleep(300)  # Run for 5 minutes
        ...     
        ...     await refresher.stop()
        ...     driver.quit()
        >>> 
        >>> asyncio.run(main())
    """
    
    def __init__(self, driver: Any, interval: int = 60, urls: Optional[List[str]] = None):
        """
        Initialize the AsyncChromeRefresher.
        
        Args:
            driver: Selenium/WebDriver/undetected_chromedriver instance
                   Must have a .refresh() method
            interval: Time between refreshes in seconds (default: 60)
            urls: Optional list of URLs to rotate through. If provided, will navigate
                 to each URL instead of just refreshing current page
        
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
        self._task: Optional[asyncio.Task] = None
        
        # Multiple URL support
        self.urls = urls or []
        self.current_url_index = 0

    def add_url(self, url: str) -> None:
        """
        Add URL to rotation list.
        
        Args:
            url: URL to add to the rotation
        """
        self.urls.append(url)
        print(f"[{time.strftime('%H:%M:%S')}] Added URL to rotation: {url}")

    def remove_url(self, url: str) -> bool:
        """
        Remove URL from rotation list.
        
        Args:
            url: URL to remove from rotation
            
        Returns:
            bool: True if URL was removed, False if not found
        """
        try:
            self.urls.remove(url)
            print(f"[{time.strftime('%H:%M:%S')}] Removed URL from rotation: {url}")
            return True
        except ValueError:
            print(f"[{time.strftime('%H:%M:%S')}] URL not found in rotation: {url}")
            return False

    def get_urls(self) -> List[str]:
        """
        Get current list of URLs in rotation.
        
        Returns:
            List[str]: List of URLs
        """
        return self.urls.copy()

    def clear_urls(self) -> None:
        """Clear all URLs from rotation."""
        self.urls.clear()
        self.current_url_index = 0
        print(f"[{time.strftime('%H:%M:%S')}] Cleared all URLs from rotation")

    async def _refresh_loop(self) -> None:
        """Async refresh loop."""
        while self.running:
            try:
                await asyncio.sleep(self.interval)
                if not self.running:
                    break
                    
                # Run refresh/navigation in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                
                if self.urls:
                    # Navigate to next URL in rotation
                    url = self.urls[self.current_url_index]
                    print(f"[{time.strftime('%H:%M:%S')}] Navigating to URL ({self.current_url_index + 1}/{len(self.urls)}): {url}")
                    await loop.run_in_executor(None, self.driver.get, url)
                    self.current_url_index = (self.current_url_index + 1) % len(self.urls)
                else:
                    # Standard refresh
                    print(f"[{time.strftime('%H:%M:%S')}] Auto-refreshing page...")
                    await loop.run_in_executor(None, self.driver.refresh)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Refresh error: {e}")

    async def start(self) -> None:
        """
        Start async refresh.
        
        Returns:
            None
        """
        if not self.running:
            self.running = True
            mode = "URL rotation" if self.urls else "page refresh"
            print(f"[{time.strftime('%H:%M:%S')}] Started async auto-{mode} (interval: {self.interval}s)")
            if self.urls:
                print(f"[{time.strftime('%H:%M:%S')}] URLs in rotation: {len(self.urls)}")
            self._task = asyncio.create_task(self._refresh_loop())

    async def stop(self) -> None:
        """
        Stop async refresh.
        
        Returns:
            None
        """
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        print(f"[{time.strftime('%H:%M:%S')}] Stopped async auto-refresh")

    def is_running(self) -> bool:
        """
        Check if async auto-refresh is currently running.
        
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

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
