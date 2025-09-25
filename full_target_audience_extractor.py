"""
Full Target Audience Extractor for All 142 Courses
Based on successful test pattern - Header Pattern Recognition
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
import re


class FullTargetAudienceExtractor:
    """Full target audience extractor for all 142 courses"""

    def __init__(self, chromedriver_path="./chromedriver.exe"):
        self.chromedriver_path = chromedriver_path
        self.driver = None

        # Known target audience types from Genesys
        self.target_audiences = [
            'admin', 'administrator', 'administrators',
            'agent', 'agents',
            'analyst', 'analysts',
            'business user', 'business users',
            'developer', 'developers',
            'IT', 'IT professional', 'IT professionals',
            'manager', 'managers',
            'supervisor', 'supervisors',
            'contact center administrator',
            'contact center manager',
            'contact center agent', 'contact center agents',
            'quality manager',
            'workforce manager',
            'system administrator', 'system administrators'
        ]

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

    def extract_target_audience_enhanced(self, page_text):
        """Enhanced target audience extraction using proven header pattern"""

        found_audiences = []
        extraction_method = ""

        # Strategy that worked in testing: Header pattern recognition
        header_patterns = [
            r'Target\s+Audience[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Intended\s+Audience[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Who\s+Should\s+Attend[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'This\s+(?:course|eLearning)\s+is\s+(?:for|intended\s+for)[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Designed\s+for[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Suitable\s+for[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))'
        ]

        for pattern in header_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                context = match.group(1).strip()
                if context and len(context) > 3:
                    # Clean up the context
                    context = re.sub(r'\s+', ' ', context)  # Remove extra whitespace
                    detected = self.detect_audiences_in_text(context)
                    if detected:
                        found_audiences.extend(detected)
                        extraction_method = f"Header pattern"
                        print(f"    Found: {', '.join(detected)}")
                        print(f"    Context: {context[:100]}...")
                        return found_audiences, extraction_method

        # Fallback: Look for prerequisite patterns
        if not found_audiences:
            prereq_patterns = [
                r'Prerequisites[:\s]*([^\.]+?)(?:Course\s+Objectives)',
                r'Course\s+Prerequisites[:\s]*([^\.]+?)(?:Course\s+Objectives)'
            ]

            for pattern in prereq_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    context = match.group(1).strip()
                    if context and len(context) > 10:
                        context = re.sub(r'\s+', ' ', context)
                        detected = self.detect_audiences_in_text(context)
                        if detected:
                            found_audiences.extend(detected)
                            extraction_method = f"Prerequisites pattern"
                            print(f"    Found: {', '.join(detected)}")
                            print(f"    Context: {context[:100]}...")
                            return found_audiences, extraction_method

        return found_audiences, extraction_method

    def detect_audiences_in_text(self, text):
        """Detect target audiences in a piece of text"""
        detected = []
        text_lower = text.lower()

        # Look for exact matches and common variations
        audience_mappings = {
            'developers': 'Developers',
            'developer': 'Developers',
            'system administrators': 'System Administrators',
            'system administrator': 'System Administrator',
            'administrators': 'Administrators',
            'administrator': 'Administrator',
            'contact center administrators': 'Contact Center Administrators',
            'contact center administrator': 'Contact Center Administrator',
            'agents': 'Agents',
            'agent': 'Agents',
            'contact center agents': 'Contact Center Agents',
            'contact center agent': 'Contact Center Agents',
            'supervisors': 'Supervisors',
            'supervisor': 'Supervisors',
            'managers': 'Managers',
            'manager': 'Managers',
            'contact center managers': 'Contact Center Managers',
            'contact center manager': 'Contact Center Managers',
            'quality managers': 'Quality Managers',
            'quality manager': 'Quality Managers',
            'workforce managers': 'Workforce Managers',
            'workforce manager': 'Workforce Managers',
            'business users': 'Business Users',
            'business user': 'Business Users',
            'analysts': 'Analysts',
            'analyst': 'Analysts',
            'it professionals': 'IT Professionals',
            'it professional': 'IT Professionals',
            'it': 'IT Professionals'
        }

        for key, value in audience_mappings.items():
            if key in text_lower:
                if value not in detected:
                    detected.append(value)

        return detected

    def extract_course_content(self, url, title, course_num, total_courses, wait_time=12):
        """Extract target audience from course content"""

        print(f"[{course_num}/{total_courses}] Loading: {title[:50]}...")

        try:
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 8).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            print(f"  Waiting {wait_time}s for content...")
            time.sleep(wait_time)

            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Remove footer elements
            for element in soup.find_all(['footer', 'nav']):
                element.decompose()

            # Get text for analysis
            page_text = soup.get_text()

            course_info = {
                'title': title,
                'url': url,
                'target_audience': [],
                'extraction_method': '',
                'extraction_timestamp': datetime.now().isoformat()
            }

            # Extract target audience
            print("  Searching for target audience...")
            audiences, method = self.extract_target_audience_enhanced(page_text)

            if audiences:
                course_info['target_audience'] = audiences
                course_info['extraction_method'] = method
                print(f"  ✓ Found: {', '.join(audiences)}")
            else:
                print(f"  - No target audience found")

            return course_info

        except Exception as e:
            print(f"  Error: {str(e)[:50]}...")
            return {
                'title': title,
                'url': url,
                'target_audience': [],
                'extraction_method': 'Error',
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def extract_all_courses(self):
        """Extract target audience from all 142 courses"""

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

        print(f"\\nStarting FULL TARGET AUDIENCE extraction of {len(courses)} courses...")
        print("=" * 70)

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

                results.append(content)

                if content.get('target_audience'):
                    successful_extractions += 1

                extraction_time = time.time() - start_time
                print(f"  Time: {extraction_time:.1f}s")

                # Save intermediate results every 20 courses
                if i % 20 == 0:
                    self.save_intermediate_results(results, i, successful_extractions)

                print("-" * 50)
                time.sleep(2)  # Be respectful

        finally:
            if self.driver:
                self.driver.quit()
                print("Browser closed")

        return results, successful_extractions

    def save_intermediate_results(self, results, processed, successful):
        """Save intermediate results"""
        filename = f"target_audience_progress_{processed}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'successful': successful,
                'extraction_date': datetime.now().isoformat(),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        print(f"  Saved progress to {filename}")

    def save_final_results(self, results, successful_count):
        """Save final target audience results"""

        final_data = {
            'extraction_date': datetime.now().isoformat(),
            'total_courses': len(results),
            'successful_extractions': successful_count,
            'success_rate': f"{successful_count/len(results)*100:.1f}%" if results else "0%",
            'courses': results
        }

        # Save complete results
        with open('final_target_audience_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        # Create CSV with target audience
        with open('final_courses_with_target_audience.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'title', 'url', 'target_audience', 'extraction_method'
            ])

            for course in results:
                writer.writerow([
                    course.get('title', ''),
                    course.get('url', ''),
                    '; '.join(course.get('target_audience', [])),
                    course.get('extraction_method', '')
                ])

        print(f"\\n=== Final Target Audience Results ===")
        print(f"Total courses processed: {len(results)}")
        print(f"Successful target audience extractions: {successful_count}")
        print(f"Success rate: {successful_count/len(results)*100:.1f}%")
        print(f"\\nFiles saved:")
        print(f"- final_target_audience_extraction.json")
        print(f"- final_courses_with_target_audience.csv")


def main():
    """Main function"""

    print("=== Full Target Audience Extraction for All 142 Courses ===")
    print("Using proven header pattern recognition from successful test")
    print("This will take approximately 45-60 minutes...")
    print("=" * 70)

    extractor = FullTargetAudienceExtractor()

    # Run full extraction
    results, successful_count = extractor.extract_all_courses()

    if results:
        extractor.save_final_results(results, successful_count)
        print(f"\\nFull target audience extraction complete!")
        print(f"Successfully extracted target audience from {successful_count}/{len(results)} courses")
    else:
        print(f"\\nExtraction failed - check ChromeDriver setup")


if __name__ == "__main__":
    main()