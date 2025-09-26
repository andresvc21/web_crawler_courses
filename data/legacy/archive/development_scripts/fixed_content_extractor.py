"""
Fixed Content Extractor using Manual ChromeDriver
"""

import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class FixedGenesysExtractor:
    """Fixed extractor using manual ChromeDriver"""

    def __init__(self, chromedriver_path="./chromedriver.exe"):
        self.chromedriver_path = chromedriver_path
        self.driver = None

    def setup_chrome_driver(self):
        """Setup Chrome with manual driver path"""

        # Check if ChromeDriver exists
        if not os.path.exists(self.chromedriver_path):
            print(f"❌ ChromeDriver not found at: {self.chromedriver_path}")
            print(f"Please download ChromeDriver and place it in the project folder")
            return False

        print(f"Found ChromeDriver at: {self.chromedriver_path}")

        chrome_options = Options()

        # Essential options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Optional: Run headless (set to False to see the browser)
        # chrome_options.add_argument("--headless")

        try:
            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome driver setup successful!")
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False

    def extract_course_content(self, url, wait_time=15):
        """Extract course content with extended wait"""

        print(f"📄 Loading: {url}")

        try:
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            print(f"⏳ Waiting {wait_time} seconds for dynamic content...")
            time.sleep(wait_time)  # Extended wait for JavaScript

            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            print(f"📏 Page source length: {len(page_source):,} bytes")

            # Try to extract course information
            course_info = {
                'url': url,
                'page_length': len(page_source),
                'title': '',
                'description': '',
                'duration': '',
                'level': '',
                'extraction_timestamp': datetime.now().isoformat()
            }

            # Try multiple title selectors
            title_selectors = [
                'h1',
                '.course-title',
                '.title',
                '[class*="title"]',
                'title'
            ]

            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 3:
                        course_info['title'] = text
                        print(f"📝 Found title: {text[:50]}...")
                        break

            # Try to find description
            desc_selectors = [
                '.description',
                '.course-description',
                '.overview',
                '[class*="description"]',
                '.summary'
            ]

            for selector in desc_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 10:
                        course_info['description'] = text
                        print(f"📄 Found description: {text[:100]}...")
                        break

            # Look for duration in text
            import re
            page_text = soup.get_text()
            duration_patterns = [
                r'(\d+)\s*(?:minute|min|hour|hr)s?\b',
                r'Duration:\s*([^\n\r,]+)',
                r'Time:\s*([^\n\r,]+)'
            ]

            for pattern in duration_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    course_info['duration'] = match.group(1 if '(' in pattern else 0).strip()
                    print(f"⏰ Found duration: {course_info['duration']}")
                    break

            # Check if we found any meaningful content
            has_content = bool(course_info['title'] or course_info['description'] or course_info['duration'])

            if not has_content:
                print("⚠️  No specific course content found - may still be JavaScript-rendered")
                # Save a sample of page content for analysis
                course_info['page_sample'] = page_text[:500]
            else:
                print("✅ Successfully extracted course information!")

            return course_info

        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            return None

    def test_extraction(self, num_courses=3):
        """Test extraction on a few sample courses"""

        # Load course list
        try:
            with open('found_courses_clean.json', 'r', encoding='utf-8') as f:
                courses = json.load(f)
        except:
            print("❌ Could not load course list")
            return []

        if not self.setup_chrome_driver():
            return []

        sample_courses = courses[:num_courses]
        results = []

        print(f"\n🧪 Testing content extraction on {len(sample_courses)} courses...\n")

        try:
            for i, course in enumerate(sample_courses, 1):
                print(f"[{i}/{len(sample_courses)}] {course['title']}")

                content = self.extract_course_content(course['url'])
                if content:
                    results.append(content)

                print("─" * 60)
                time.sleep(2)  # Be respectful

        finally:
            if self.driver:
                self.driver.quit()
                print("🚗 Browser closed")

        return results

    def save_test_results(self, results):
        """Save test results"""
        output = {
            'test_date': datetime.now().isoformat(),
            'total_tested': len(results),
            'results': results
        }

        with open('manual_extraction_test.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: manual_extraction_test.json")

        # Summary
        successful = sum(1 for r in results if r and (r.get('title') or r.get('description') or r.get('duration')))
        print(f"\n📊 Test Summary:")
        print(f"Courses tested: {len(results)}")
        print(f"Content extracted: {successful}")
        print(f"Success rate: {successful/len(results)*100:.1f}%" if results else "0%")


def main():
    """Main function"""

    print("Fixed ChromeDriver Content Extractor")
    print("=" * 50)

    # Check if ChromeDriver exists
    chromedriver_path = "./chromedriver.exe"
    if not os.path.exists(chromedriver_path):
        print(f"\n❌ ChromeDriver not found!")
        print(f"Please follow these steps:")
        print(f"1. Open Chrome and go to: chrome://version/")
        print(f"2. Note your Chrome version (e.g., 140.0.7339.207)")
        print(f"3. Go to: https://googlechromelabs.github.io/chrome-for-testing/")
        print(f"4. Download the matching 'chromedriver-win64.zip'")
        print(f"5. Extract chromedriver.exe to this folder:")
        print(f"   {os.path.abspath(chromedriver_path)}")
        print(f"\nThen run this script again.")
        return

    extractor = FixedGenesysExtractor(chromedriver_path)

    # Test with 3 courses
    results = extractor.test_extraction(3)

    if results:
        extractor.save_test_results(results)

        # Check if we got meaningful content
        successful = sum(1 for r in results if r and (r.get('title') or r.get('description') or r.get('duration')))

        if successful > 0:
            print(f"\n🎉 Success! We extracted content from {successful} course(s)!")
            print(f"Ready to process all 142 courses if needed.")
        else:
            print(f"\n⚠️  No course content extracted.")
            print(f"The site may require different techniques or longer wait times.")

    print(f"\n✅ Test complete!")


if __name__ == "__main__":
    main()