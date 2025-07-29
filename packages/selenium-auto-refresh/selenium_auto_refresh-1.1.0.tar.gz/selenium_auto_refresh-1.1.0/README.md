# Selenium Auto Refresh

Automatically refresh Selenium Chrome tabs at specified intervals. Perfect for keeping sessions alive during long-running automation tasks.

## Features

- 🔄 Automatic page refresh at customizable intervals
- 🛡️ Error handling for failed refreshes
- 🎯 Compatible with all Selenium-based drivers
- 🔧 Context manager support
- 📊 Runtime interval changes
- 🪶 Lightweight with no dependencies

## Installation

```bash
pip install selenium-auto-refresh
```

## Quick Start

```python
from selenium import webdriver
from selenium_auto_refresh import ChromeRefresher

# Setup your driver
driver = webdriver.Chrome()
driver.get("https://example.com")

# Start auto-refresh every 60 seconds
refresher = ChromeRefresher(driver, interval=60)
refresher.start()

# Your automation code here...
time.sleep(300)  # Run for 5 minutes

# Stop auto-refresh
refresher.stop()
driver.quit()
```

## Context Manager Usage

```python
with ChromeRefresher(driver, interval=30) as refresher:
    # Auto-refresh starts automatically
    # Your automation code here...
    pass
# Auto-refresh stops automatically
```

## Compatible Drivers

- ✅ Selenium WebDriver
- ✅ SeleniumBase Driver  
- ✅ undetected-chromedriver
- ✅ Any driver with `.refresh()` method

## API Reference

### ChromeRefresher(driver, interval=60)

**Parameters:**
- `driver`: WebDriver instance with `.refresh()` method
- `interval`: Refresh interval in seconds (default: 60)

**Methods:**
- `start()`: Start auto-refresh
- `stop()`: Stop auto-refresh  
- `is_running()`: Check if running
- `change_interval(seconds)`: Change refresh interval

## License

MIT License
```

## 5. Create tests:

```python:tests/test_refresher.py
import unittest
from unittest.mock import Mock, patch
import time
from selenium_auto_refresh import ChromeRefresher


class TestChromeRefresher(unittest.TestCase):
    
    def setUp(self):
        self.mock_driver = Mock()
        self.mock_driver.refresh = Mock()
    
    def test_init_valid_driver(self):
        refresher = ChromeRefresher(self.mock_driver, 30)
        self.assertEqual(refresher.interval, 30)
        self.assertFalse(refresher.running)
    
    def test_init_invalid_driver(self):
        invalid_driver = Mock()
        del invalid_driver.refresh
        
        with self.assertRaises(AttributeError):
            ChromeRefresher(invalid_driver)
    
    def test_init_invalid_interval(self):
        with self.assertRaises(ValueError):
            ChromeRefresher(self.mock_driver, -1)
    
    def test_start_stop(self):
        refresher = ChromeRefresher(self.mock_driver, 1)
        
        refresher.start()
        self.assertTrue(refresher.is_running())
        
        refresher.stop()
        self.assertFalse(refresher.is_running())
    
    def test_context_manager(self):
        with ChromeRefresher(self.mock_driver, 1) as refresher:
            self.assertTrue(refresher.is_running())
        self.assertFalse(refresher.is_running())


if __name__ == '__main__':
    unittest.main()
```

## 6. Publish to PyPI:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (test first)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*