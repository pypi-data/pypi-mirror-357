"""
Selenium Auto Refresh - Automatically refresh Chrome tabs using Selenium WebDriver.
"""

__version__ = "1.1.0"
__author__ = "Lalit2206"
__email__ = "happytaak8@gmail.com"

from .refresher import ChromeRefresher, AsyncChromeRefresher

__all__ = ["ChromeRefresher", "AsyncChromeRefresher"]
