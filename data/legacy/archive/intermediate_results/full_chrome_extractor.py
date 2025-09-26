"""
Full Chrome Content Extractor for All 142 Genesys Courses
"""

import json
import time
import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


class FullGenesysExtractor:
    """Full extractor for all 142 courses"""

    def __init__(self, chromedriver_path="./chromedriver.exe"):
        self.chromedriver_path = chromedriver_path
        self.driver = None

    def setup_chrome_driver(self):
        """Setup Chrome with manual driver path"""

        if not os.path.exists(self.chromedriver_path):
            print(f"ChromeDriver not found at: {self.chromedriver_path}")
            return False

        print(f"Found ChromeDriver at: {self.chromedriver_path}")

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")  # Run headless for speed

        try:
            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome driver setup successful!")
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False

    def extract_course_content(self, url, title, course_num, total_courses, wait_time=12):
        """Extract course content with enhanced selectors"""

        print(f"[{course_num}/{total_courses}] Loading: {title}")
        print(f"  URL: {url}")

        try:
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 8).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            print(f"  Waiting {wait_time} seconds for dynamic content...")
            time.sleep(wait_time)

            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Enhanced content extraction
            course_info = {
                'title': title,
                'url': url,
                'page_length': len(page_source),
                'extracted_title': '',
                'description': '',
                'duration': '',
                'level': '',
                'objectives': [],
                'prerequisites': '',
                'extraction_timestamp': datetime.now().isoformat()
            }

            # Extract title with more selectors
            title_selectors = [
                'h1',
                '.course-title',
                '.title',
                '[class*="title"]',
                '.page-title',
                '.course-name',
                '[data-testid*="title"]'
            ]

            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 3 and text != title:
                        course_info['extracted_title'] = text
                        print(f"  Found page title: {text[:50]}...")
                        break

            # Extract description with enhanced selectors
            desc_selectors = [
                '.course-description',
                '.description',
                '.course-overview',
                '.overview',
                '.summary',
                '[class*="description"]',
                '[class*="overview"]',
                '.course-summary',
                '.about',
                '[data-testid*="description"]',
                '.content-description'
            ]

            for selector in desc_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 10:
                        course_info['description'] = text[:500]  # Limit length
                        print(f"  Found description: {text[:80]}...")
                        break

            # Extract objectives
            obj_selectors = [
                '.objectives li',
                '.learning-objectives li',
                '.outcomes li',
                '[class*="objective"] li',
                '.goals li',
                '[class*="learning"] li'
            ]

            for selector in obj_selectors:
                elements = soup.select(selector)
                if elements:
                    objectives = [elem.get_text().strip() for elem in elements[:5]]  # Limit to 5
                    if objectives:
                        course_info['objectives'] = objectives
                        print(f"  Found {len(objectives)} objectives")
                        break

            # Enhanced duration search
            import re
            page_text = soup.get_text()

            # Duration patterns
            duration_patterns = [
                r'(\d+)\s*(?:minute|min|hour|hr)s?\b',
                r'Duration:\s*([^\n\r,]+)',
                r'Time:\s*([^\n\r,]+)',
                r'Length:\s*([^\n\r,]+)',
                r'(?:Takes?|Lasts?)\s*(?:about\s*)?(\d+\s*(?:minute|min|hour|hr)s?)',
                r'Estimated\s*time:\s*([^\n\r,]+)',
                r'Course\s*length:\s*([^\n\r,]+)'
            ]

            for pattern in duration_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    duration_text = match.group(1 if '(' in pattern else 0).strip()
                    if duration_text:
                        course_info['duration'] = duration_text
                        print(f"  Found duration: {duration_text}")
                        break

            # Level extraction
            level_patterns = [
                r'Level:\s*([^\n\r,]+)',
                r'Difficulty:\s*([^\n\r,]+)',
                r'\b(Beginner|Intermediate|Advanced|Expert|Basic)\b'
            ]

            for pattern in level_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    course_info['level'] = match.group(1).strip()
                    print(f"  Found level: {course_info['level']}")
                    break

            # Prerequisites
            prereq_selectors = [
                '.prerequisites',
                '.requirements',
                '[class*="prerequisite"]',
                '[class*="requirement"]'
            ]

            for selector in prereq_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 5:
                        course_info['prerequisites'] = text[:200]  # Limit length
                        print(f"  Found prerequisites: {text[:50]}...")
                        break

            # Success indicator
            extracted_fields = sum([
                bool(course_info['extracted_title']),
                bool(course_info['description']),
                bool(course_info['duration']),
                bool(course_info['level']),
                bool(course_info['objectives']),
                bool(course_info['prerequisites'])
            ])

            print(f"  Extracted {extracted_fields}/6 fields")

            return course_info

        except Exception as e:
            print(f"  Error extracting content: {e}")
            return {
                'title': title,
                'url': url,
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def extract_all_courses(self):
        """Extract content from all 142 courses"""

        # Load all courses
        courses = []
        try:
            with open('all_142_courses.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                courses = list(reader)
        except Exception as e:
            print(f"Error loading courses: {e}")
            return []

        if not courses:
            print("No courses found!")
            return []

        if not self.setup_chrome_driver():
            return []

        print(f"\nStarting full extraction of {len(courses)} courses...")
        print("=" * 60)

        results = []
        successful_extractions = 0

        try:
            for i, course in enumerate(courses, 1):
                start_time = time.time()

                content = self.extract_course_content(
                    course['url'],
                    course['title'],
                    i,
                    len(courses)
                )

                if content and not content.get('error'):
                    results.append(content)

                    # Count successful extractions
                    if (content.get('description') or
                        content.get('duration') or
                        content.get('level') or
                        content.get('objectives')):
                        successful_extractions += 1

                extraction_time = time.time() - start_time
                print(f"  Time: {extraction_time:.1f}s")

                # Save intermediate results every 10 courses
                if i % 10 == 0:
                    self.save_intermediate_results(results, i, successful_extractions)

                print("-" * 60)
                time.sleep(2)  # Be respectful

        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed")

        return results, successful_extractions

    def save_intermediate_results(self, results, processed, successful):
        """Save intermediate results"""
        filename = f"extraction_progress_{processed}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'successful': successful,
                'results': results
            }, f, indent=2, ensure_ascii=False)
        print(f"  Saved progress to {filename}")

    def save_final_results(self, results, successful_count):
        """Save final comprehensive results"""

        final_data = {
            'extraction_date': datetime.now().isoformat(),
            'total_courses': len(results),
            'successful_extractions': successful_count,
            'success_rate': f"{successful_count/len(results)*100:.1f}%" if results else "0%",
            'courses': results
        }

        # Save complete results
        with open('final_course_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        # Create clean CSV with extracted data
        with open('final_courses_with_content.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'title', 'url', 'description', 'duration', 'level',
                'objectives', 'prerequisites', 'page_length'
            ])

            for course in results:
                writer.writerow([
                    course.get('title', ''),
                    course.get('url', ''),
                    course.get('description', ''),
                    course.get('duration', ''),
                    course.get('level', ''),
                    '; '.join(course.get('objectives', [])),
                    course.get('prerequisites', ''),
                    course.get('page_length', 0)
                ])

        print(f"\n=== Final Results ===")
        print(f"Total courses processed: {len(results)}")
        print(f"Successful content extractions: {successful_count}")
        print(f"Success rate: {successful_count/len(results)*100:.1f}%")
        print(f"\nFiles saved:")
        print(f"- final_course_extraction.json (complete data)")
        print(f"- final_courses_with_content.csv (spreadsheet format)")


def main():
    """Main function"""

    print("=== Full Genesys Course Content Extraction ===")
    print("Processing all 142 courses with Chrome automation")
    print("This will take approximately 30-45 minutes...")
    print("=" * 60)

    extractor = FullGenesysExtractor()

    # Run full extraction
    results, successful_count = extractor.extract_all_courses()

    if results:
        extractor.save_final_results(results, successful_count)
        print(f"\n🎉 Extraction complete!")
        print(f"Successfully extracted content from {successful_count}/{len(results)} courses")
    else:
        print(f"\n❌ Extraction failed - check ChromeDriver setup")


if __name__ == "__main__":
    main()