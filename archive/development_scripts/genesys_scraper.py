"""
Genesys Course Scraper
Extracts e-learning course information from beyond.genesys.com
"""

import json
import csv
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genesys_scraper.log'),
        logging.StreamHandler()
    ]
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
    objectives: List[str] = None
    prerequisites: str = ""

    def __post_init__(self):
        if self.objectives is None:
            self.objectives = []


class GenesysCourseScraper:
    """Scraper for Genesys e-learning courses"""

    BASE_URL = "https://beyond.genesys.com"
    SEARCH_URL = "https://beyond.genesys.com/explore/search;s=;p={page}"

    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode
            delay: Delay between requests (seconds)
        """
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.courses: List[Course] = []

    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome webdriver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Handle Windows architecture issues
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.info(f"First attempt failed: {e}. Trying with win32 driver...")
            # Try with win32 version
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager(version="140.0.7339.207", os_type="win32").install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """Wait for page to load completely"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(self.delay)  # Additional wait for dynamic content
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False

    def get_course_links_from_page(self, page_num: int) -> List[str]:
        """Extract course links from a search results page"""
        course_links = []
        url = self.SEARCH_URL.format(page=page_num)

        logger.info(f"Scraping page {page_num}: {url}")

        try:
            self.driver.get(url)
            self.wait_for_page_load()

            # Look for course links - these are common patterns for course listing sites
            # We'll try multiple selectors as we don't know the exact structure
            possible_selectors = [
                "a[href*='/explore/course/']",
                "a[href*='/course/']",
                ".course-item a",
                ".course-card a",
                ".course-link",
                "a[href*='genesys-cloud']"
            ]

            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} course links using selector: {selector}")
                        for element in elements:
                            href = element.get_attribute("href")
                            if href and "/explore/course/" in href:
                                full_url = urljoin(self.BASE_URL, href)
                                if full_url not in course_links:
                                    course_links.append(full_url)
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            # If no specific selectors work, try to find any links with course patterns
            if not course_links:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    href = link.get_attribute("href")
                    if href and "/explore/course/" in href:
                        full_url = urljoin(self.BASE_URL, href)
                        if full_url not in course_links:
                            course_links.append(full_url)

            logger.info(f"Found {len(course_links)} course links on page {page_num}")

        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")

        return course_links

    def extract_course_details(self, course_url: str) -> Optional[Course]:
        """Extract detailed information from a course page"""
        logger.info(f"Extracting details from: {course_url}")

        try:
            self.driver.get(course_url)
            self.wait_for_page_load()

            # Extract course information using multiple strategies
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract title
            title = ""
            title_selectors = ["h1", ".course-title", ".title", "h1.title"]
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    title = element.get_text().strip()
                    break

            # Extract description
            description = ""
            desc_selectors = [".course-description", ".description", ".overview", ".summary"]
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    description = element.get_text().strip()
                    break

            # Extract duration
            duration = ""
            duration_selectors = [".duration", ".course-duration", "*[class*='duration']"]
            for selector in duration_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    duration = element.get_text().strip()
                    break

            # Extract level
            level = ""
            level_selectors = [".level", ".difficulty", ".course-level"]
            for selector in level_selectors:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    level = element.get_text().strip()
                    break

            # Extract objectives
            objectives = []
            obj_selectors = [".objectives li", ".learning-objectives li", ".outcomes li"]
            for selector in obj_selectors:
                elements = soup.select(selector)
                if elements:
                    objectives = [elem.get_text().strip() for elem in elements]
                    break

            course = Course(
                title=title or "Title not found",
                url=course_url,
                description=description,
                duration=duration,
                level=level,
                objectives=objectives
            )

            logger.info(f"Successfully extracted: {course.title}")
            return course

        except Exception as e:
            logger.error(f"Error extracting course details from {course_url}: {e}")
            return None

    def scrape_all_courses(self, max_pages: int = 20) -> List[Course]:
        """Scrape all courses from the website"""
        logger.info("Starting course scraping...")

        self.driver = self.setup_driver()
        all_course_links = set()

        try:
            # Collect all course links from search pages
            for page_num in range(1, max_pages + 1):
                course_links = self.get_course_links_from_page(page_num)

                if not course_links:
                    logger.info(f"No courses found on page {page_num}, stopping pagination")
                    break

                all_course_links.update(course_links)
                time.sleep(self.delay)

            logger.info(f"Found {len(all_course_links)} unique course links")

            # Extract details from each course
            for i, course_url in enumerate(all_course_links, 1):
                logger.info(f"Processing course {i}/{len(all_course_links)}")

                course = self.extract_course_details(course_url)
                if course:
                    self.courses.append(course)

                time.sleep(self.delay)

        finally:
            if self.driver:
                self.driver.quit()

        logger.info(f"Scraping completed. Found {len(self.courses)} courses")
        return self.courses

    def save_to_json(self, filename: str = "genesys_courses.json"):
        """Save courses to JSON file"""
        data = [asdict(course) for course in self.courses]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.courses)} courses to {filename}")

    def save_to_csv(self, filename: str = "genesys_courses.csv"):
        """Save courses to CSV file"""
        if not self.courses:
            logger.warning("No courses to save")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Title', 'URL', 'Description', 'Duration',
                'Level', 'Category', 'Objectives', 'Prerequisites'
            ])

            # Data
            for course in self.courses:
                writer.writerow([
                    course.title,
                    course.url,
                    course.description,
                    course.duration,
                    course.level,
                    course.category,
                    '; '.join(course.objectives) if course.objectives else '',
                    course.prerequisites
                ])

        logger.info(f"Saved {len(self.courses)} courses to {filename}")


def main():
    """Main function to run the scraper"""
    scraper = GenesysCourseScraper(headless=False, delay=3.0)  # Set headless=False to see browser

    try:
        courses = scraper.scrape_all_courses(max_pages=10)  # Start with 10 pages

        if courses:
            scraper.save_to_json()
            scraper.save_to_csv()

            print(f"\nScraping completed!")
            print(f"Total courses found: {len(courses)}")
            print(f"Files saved: genesys_courses.json, genesys_courses.csv")

            # Show sample of first few courses
            print(f"\nFirst 3 courses:")
            for i, course in enumerate(courses[:3], 1):
                print(f"{i}. {course.title}")
                print(f"   URL: {course.url}")
                print(f"   Duration: {course.duration}")
                print()
        else:
            print("No courses were scraped. Check the logs for issues.")

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()