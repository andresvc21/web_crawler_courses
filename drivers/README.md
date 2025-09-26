# Browser Drivers

This directory contains browser drivers needed for web automation.

## ChromeDriver

The included `chromedriver.exe` is compatible with Chrome browsers and is required for the extraction process.

### Setup

1. The ChromeDriver is already included and configured
2. Make sure you have Chrome browser installed
3. The extractor will automatically use the driver from this location

### Manual Updates

If you need to update ChromeDriver:

1. Download from: https://chromedriver.chromium.org/
2. Replace the existing `chromedriver.exe`
3. Ensure it matches your Chrome browser version

### Troubleshooting

- **Driver not found**: Check that `chromedriver.exe` exists in this directory
- **Version mismatch**: Download ChromeDriver matching your Chrome version
- **Permissions**: Ensure the driver has execute permissions