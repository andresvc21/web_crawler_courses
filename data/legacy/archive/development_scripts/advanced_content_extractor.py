"""
Advanced Content Extractor for Genesys Courses
Uses multiple approaches to extract course descriptions and durations
"""

import json
import time
import re
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


class AdvancedGenesysExtractor:
    """Advanced extractor that tries multiple methods to get course content"""

    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

    def setup_chrome_driver(self):
        """Setup Chrome with optimal settings for content extraction"""
        print("Setting up Chrome driver with advanced options...")

        chrome_options = Options()

        # Essential options for content loading
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Allow JavaScript and dynamic content
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")

        # Network optimizations
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        # User agent and headers
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            # Try with current Chrome version
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome driver setup successful!")
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False

    def wait_for_content_loading(self, url, max_wait=30):
        """Wait for dynamic content to load with multiple strategies"""
        print(f"Loading: {url}")

        try:
            self.driver.get(url)

            # Wait for basic page load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Additional wait strategies
            wait_strategies = [
                # Wait for content containers to appear
                lambda: self.driver.find_elements(By.CSS_SELECTOR, "[class*='content'], [class*='course'], [class*='description']"),

                # Wait for text content to be non-empty
                lambda: len(self.driver.page_source) > 5000,

                # Wait for potential loading spinners to disappear
                lambda: not self.driver.find_elements(By.CSS_SELECTOR, "[class*='loading'], [class*='spinner']"),
            ]

            # Progressive waiting
            for i in range(max_wait):
                time.sleep(1)

                # Check if any wait strategy indicates content is ready
                content_ready = any(strategy() for strategy in wait_strategies)

                if content_ready and len(self.driver.page_source) > 4000:
                    print(f"  Content detected after {i+1} seconds")
                    time.sleep(3)  # Extra buffer
                    return True

                if i % 5 == 0:
                    print(f"  Waiting for content... ({i}/{max_wait}s)")

            print(f"  Timeout after {max_wait} seconds")
            return False

        except Exception as e:
            print(f"  Error loading page: {e}")
            return False

    def extract_with_multiple_selectors(self, soup, selectors_map):
        """Try multiple CSS selectors to find content"""
        results = {}

        for field, selectors in selectors_map.items():
            results[field] = ""

            for selector in selectors:
                try:
                    if selector.startswith('meta['):
                        # Handle meta tags
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            results[field] = element.get('content').strip()
                            break
                    else:
                        # Handle regular elements
                        elements = soup.select(selector)
                        if elements:
                            text = ' '.join([elem.get_text().strip() for elem in elements if elem.get_text().strip()])
                            if text:
                                results[field] = text
                                break
                except Exception as e:
                    continue

        return results

    def extract_course_details_advanced(self, url):
        """Extract course details using advanced techniques"""

        if not self.wait_for_content_loading(url):
            return None

        print("  Extracting content...")

        # Get the page source after JavaScript execution
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        print(f"  Page source length: {len(page_source)} bytes")

        # Comprehensive selector mapping
        selectors_map = {
            'title': [
                'h1.course-title',
                'h1[class*="title"]',
                '.course-header h1',
                '.page-title',
                'h1',
                'title',
                '[data-testid*="title"]',
                '[aria-label*="title"]'
            ],
            'description': [
                '.course-description',
                '.course-overview',
                '.description',
                '.overview',
                '.summary',
                '[class*="description"]',
                '[class*="overview"]',
                'meta[name="description"]',
                'meta[property="og:description"]',
                '[data-testid*="description"]'
            ],
            'duration': [
                '.duration',
                '.course-duration',
                '[class*="duration"]',
                '[data-testid*="duration"]',
                '.time',
                '.length',
                '[class*="time"]'
            ],
            'level': [
                '.level',
                '.difficulty',
                '.course-level',
                '[class*="level"]',
                '[class*="difficulty"]'
            ],
            'objectives': [
                '.objectives li',
                '.learning-objectives li',
                '.outcomes li',
                '[class*="objective"] li',
                '.goals li'
            ],
            'prerequisites': [
                '.prerequisites',
                '.requirements',
                '[class*="prerequisite"]',
                '[class*="requirement"]'
            ]
        }

        # Extract using selectors
        details = self.extract_with_multiple_selectors(soup, selectors_map)

        # Additional extraction techniques
        page_text = soup.get_text()

        # Look for duration patterns in text
        if not details['duration']:
            duration_patterns = [
                r'(\d+)\s*(?:minute|min|hour|hr)s?\b',
                r'Duration:\s*([^\n\r,]+)',
                r'Time:\s*([^\n\r,]+)',
                r'Length:\s*([^\n\r,]+)',
                r'(?:Takes?|Lasts?)\s*(?:about\s*)?(\d+\s*(?:minute|min|hour|hr)s?)'
            ]

            for pattern in duration_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['duration'] = match.group(1 if '(' in pattern else 0).strip()
                    break

        # Look for level indicators
        if not details['level']:
            level_patterns = [
                r'Level:\s*([^\n\r,]+)',
                r'Difficulty:\s*([^\n\r,]+)',
                r'\b(Beginner|Intermediate|Advanced|Expert)\b'
            ]

            for pattern in level_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['level'] = match.group(1).strip()
                    break

        # Try to find JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'name' in data and not details['title']:
                        details['title'] = data['name']
                    if 'description' in data and not details['description']:
                        details['description'] = data['description']
                    if 'duration' in data and not details['duration']:
                        details['duration'] = data['duration']
            except:
                continue

        # Look for any React/Vue component data
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Look for course data in JavaScript
                if 'course' in script.string.lower() and 'description' in script.string.lower():
                    # Try to extract JSON objects
                    json_matches = re.findall(r'\{[^{}]*"description"[^{}]*\}', script.string)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if 'description' in data and not details['description']:
                                details['description'] = data['description']
                        except:
                            continue

        return details

    def process_sample_courses(self, num_courses=10):
        """Process a sample of courses to test content extraction"""

        # Load our course list
        try:
            with open('found_courses_clean.json', 'r', encoding='utf-8') as f:
                courses = json.load(f)
        except:
            print("Could not load course list!")
            return []

        if not self.setup_chrome_driver():
            print("Failed to setup Chrome driver")
            return []

        sample_courses = courses[:num_courses]
        results = []

        print(f"\n=== Testing Content Extraction on {len(sample_courses)} Courses ===\n")

        try:
            for i, course in enumerate(sample_courses, 1):
                print(f"[{i}/{len(sample_courses)}] {course['title']}")

                details = self.extract_course_details_advanced(course['url'])

                result = {
                    'original_title': course['title'],
                    'url': course['url'],
                    'slug': course['slug'],
                    'extracted_details': details,
                    'extraction_success': bool(details and (details.get('description') or details.get('duration')))
                }

                results.append(result)

                if details:
                    print(f"  ✓ Title: {details.get('title', 'Not found')[:50]}...")
                    print(f"  ✓ Description: {details.get('description', 'Not found')[:100]}...")
                    print(f"  ✓ Duration: {details.get('duration', 'Not found')}")
                    print(f"  ✓ Level: {details.get('level', 'Not found')}")
                else:
                    print(f"  ✗ No details extracted")

                print()
                time.sleep(3)  # Be respectful

        finally:
            if self.driver:
                self.driver.quit()

        return results

    def save_sample_results(self, results):
        """Save sample extraction results"""

        # Summary
        successful = sum(1 for r in results if r['extraction_success'])

        output = {
            'extraction_date': datetime.now().isoformat(),
            'total_tested': len(results),
            'successful_extractions': successful,
            'success_rate': f"{successful/len(results)*100:.1f}%" if results else "0%",
            'results': results
        }

        with open('sample_content_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n=== Sample Extraction Results ===")
        print(f"Courses tested: {len(results)}")
        print(f"Successful extractions: {successful}")
        print(f"Success rate: {successful/len(results)*100:.1f}%")
        print(f"Results saved to: sample_content_extraction.json")

        return successful > 0


def main():
    """Main function to test advanced content extraction"""

    extractor = AdvancedGenesysExtractor()

    print("=== Advanced Genesys Content Extraction Test ===")
    print("This will test advanced techniques to extract course descriptions and durations")

    # Test with a small sample first
    results = extractor.process_sample_courses(5)

    if results:
        success = extractor.save_sample_results(results)

        if success:
            print("\n🎉 Success! We can extract content.")
            print("Would you like to process all 142 courses? (This would take ~30-45 minutes)")
        else:
            print("\n⚠️ No content extracted. The site might require different techniques.")
            print("Consider trying:")
            print("- Different browser settings")
            print("- Longer wait times")
            print("- API endpoint discovery")
            print("- Partnership with Genesys for official data")

    return results


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Check sample_content_extraction.json for any partial results")