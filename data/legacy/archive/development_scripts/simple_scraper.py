"""
Simplified Genesys Course Scraper using Edge WebDriver
"""

import json
import csv
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from bs4 import BeautifulSoup
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Course:
    """Data class to represent a course"""
    title: str
    url: str
    description: str = ""
    duration: str = ""
    level: str = ""
    category: str = ""

def scrape_with_edge():
    """Try scraping with Edge WebDriver"""
    if not SELENIUM_AVAILABLE:
        print("Selenium not available")
        return []

    print("Setting up Edge WebDriver...")

    try:
        # Setup Edge options
        edge_options = Options()
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-gpu")

        # Try to use Edge
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)

        print("Edge WebDriver setup successful!")

        # Test navigation
        print("Navigating to Genesys search page...")
        driver.get("https://beyond.genesys.com/explore/search;s=;p=1")

        # Wait for page to load
        time.sleep(5)

        print(f"Page title: {driver.title}")
        print(f"Page URL: {driver.current_url}")

        # Check page source length
        print(f"Page source length: {len(driver.page_source)}")

        # Look for any course-related content
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try different selectors
        selectors_to_try = [
            "a[href*='/explore/course/']",
            "a[href*='/course/']",
            ".course",
            "[class*='course']",
            "a[href*='genesys-cloud']"
        ]

        found_courses = []

        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Selector '{selector}' found {len(elements)} elements")

                for element in elements:
                    try:
                        href = element.get_attribute("href")
                        text = element.get_attribute("textContent") or element.text
                        if href and "/explore/course/" in href:
                            found_courses.append({
                                "title": text.strip()[:100],
                                "url": href,
                                "selector": selector
                            })
                            print(f"Found course: {text.strip()[:50]}...")
                    except Exception as e:
                        continue

            except Exception as e:
                print(f"Error with selector {selector}: {e}")

        print(f"\nTotal unique courses found: {len(set(c['url'] for c in found_courses))}")

        # Save what we found
        if found_courses:
            unique_courses = {c['url']: c for c in found_courses}.values()

            with open('found_courses.json', 'w') as f:
                json.dump(list(unique_courses), f, indent=2)
            print(f"Saved {len(unique_courses)} courses to found_courses.json")

        # Take a screenshot for debugging
        try:
            driver.save_screenshot("genesys_page.png")
            print("Screenshot saved as genesys_page.png")
        except Exception as e:
            print(f"Could not save screenshot: {e}")

        driver.quit()
        return found_courses

    except Exception as e:
        print(f"Error with Edge WebDriver: {e}")
        return []

def manual_url_approach():
    """Try to manually construct course URLs based on patterns"""

    print("\nTrying manual URL approach...")

    # Common course topics based on Genesys Cloud features
    potential_courses = [
        "genesys-cloud-social-listening-setup-and-configuration",
        "genesys-cloud-basics",
        "genesys-cloud-contact-center",
        "genesys-cloud-routing",
        "genesys-cloud-workforce-management",
        "genesys-cloud-analytics",
        "genesys-cloud-admin",
        "genesys-cloud-agent-training",
        "genesys-cloud-integration",
        "genesys-cloud-voice",
        "genesys-cloud-digital"
    ]

    base_url = "https://beyond.genesys.com/explore/course/"
    found_courses = []

    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for course_slug in potential_courses:
        url = base_url + course_slug
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Found: {url}")
                found_courses.append({
                    "title": course_slug.replace("-", " ").title(),
                    "url": url,
                    "status_code": response.status_code
                })
            else:
                print(f"❌ Not found: {url} ({response.status_code})")
        except Exception as e:
            print(f"❌ Error checking {url}: {e}")

        time.sleep(1)  # Be respectful

    return found_courses

if __name__ == "__main__":
    print("=== Simplified Genesys Course Scraper ===\n")

    # Try Edge WebDriver first
    courses = scrape_with_edge()

    if not courses:
        print("WebDriver approach failed, trying manual URL approach...")
        courses = manual_url_approach()

    print(f"\n=== Final Results ===")
    print(f"Found {len(courses)} courses")

    if courses:
        print("\nSample courses:")
        for course in courses[:5]:
            print(f"- {course.get('title', 'No title')}")
            print(f"  {course.get('url', 'No URL')}")
            print()
    else:
        print("No courses found. The website might have changed or requires different access methods.")