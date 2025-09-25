# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping project that extracts e-learning course information from the Genesys Beyond platform (beyond.genesys.com). The scraper uses Selenium to handle JavaScript-rendered content and exports data to JSON/CSV formats.

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python genesys_scraper.py

# Run with custom settings (edit main() function)
python genesys_scraper.py
```

## Architecture

- `genesys_scraper.py`: Main scraper class with Selenium automation
- `GenesysCourseScraper`: Core class handling browser automation, pagination, and data extraction
- `Course`: Dataclass for structured course information
- Output files: `genesys_courses.json`, `genesys_courses.csv`, `genesys_scraper.log`

## Key Features

- Selenium WebDriver with Chrome for JavaScript handling
- Pagination support for 142+ courses across multiple pages
- Robust CSS selector fallbacks for changing website structure
- Configurable delays and headless/visible browser modes
- Comprehensive error handling and logging
- Export to multiple formats (JSON/CSV)

## Development Notes

- Uses webdriver-manager for automatic Chrome driver management
- Implements respectful scraping with configurable delays
- Multiple CSS selector strategies handle website structure changes
- BeautifulSoup for HTML parsing after Selenium page load
- Comprehensive logging for debugging and monitoring