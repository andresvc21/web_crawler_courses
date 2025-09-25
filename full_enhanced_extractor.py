"""
Full Enhanced Chrome Content Extractor for All 142 Genesys Courses
Includes: Description, Target Audience, Course Objectives, Course Outline, Duration, Level, Prerequisites
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


class FullEnhancedGenesysExtractor:
    """Full enhanced extractor for all 142 courses"""

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

    def is_footer_content(self, text):
        """Check if text appears to be footer content"""
        footer_indicators = [
            "Genesys empowers more than 8,000 organizations",
            "organizations in over 100 countries",
            "improve loyalty and business outcomes",
            "customer experience transformation",
            "All rights reserved",
            "Copyright",
            "Privacy Policy",
            "Terms of Service"
        ]

        text_lower = text.lower()
        for indicator in footer_indicators:
            if indicator.lower() in text_lower:
                return True
        return False

    def extract_list_content(self, soup, selectors, field_name):
        """Extract list content (for objectives, outline, etc.)"""
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 0:
                items = []
                for elem in elements[:10]:  # Limit to 10 items
                    text = elem.get_text().strip()
                    if text and len(text) > 5 and not self.is_footer_content(text):
                        # Clean up text
                        text = text.replace('\n', ' ').replace('\r', ' ')
                        text = ' '.join(text.split())  # Remove extra spaces
                        items.append(text)

                if items:
                    print(f"  Found {len(items)} {field_name} items")
                    return items
        return []

    def extract_text_content(self, soup, selectors, field_name, min_length=10):
        """Extract text content (for target audience, description, etc.)"""
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text().strip()
                    if (text and len(text) > min_length and
                        not self.is_footer_content(text) and
                        len(text) < 2000):  # Reasonable upper limit
                        # Clean up text
                        text = text.replace('\n', ' ').replace('\r', ' ')
                        text = ' '.join(text.split())  # Remove extra spaces
                        print(f"  Found {field_name}: {text[:80]}...")
                        return text[:1000]  # Limit length
        return ""

    def extract_course_content(self, url, title, course_num, total_courses, wait_time=12):
        """Extract course content with enhanced fields - optimized for full run"""

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

            # Remove footer and navigation elements entirely
            for element in soup.find_all(['footer', 'nav']):
                element.decompose()

            # Remove elements with footer-like classes
            footer_classes = ['footer', 'site-footer', 'page-footer', 'global-footer', 'company-info']
            for class_name in footer_classes:
                for element in soup.find_all(class_=class_name):
                    element.decompose()

            # Enhanced content extraction
            course_info = {
                'title': title,
                'url': url,
                'page_length': len(page_source),
                'extracted_title': '',
                'description': '',
                'target_audience': '',
                'course_objectives': [],
                'course_outline': [],
                'duration': '',
                'level': '',
                'prerequisites': '',
                'extraction_timestamp': datetime.now().isoformat()
            }

            # Extract title
            title_selectors = [
                'h1.course-title',
                'h1.title',
                '.course-header h1',
                '.content-header h1',
                'h1',
                '.course-name',
                '.page-title'
            ]

            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    if text and len(text) > 3 and text != title:
                        course_info['extracted_title'] = text
                        print(f"  Found page title: {text[:50]}...")
                        break

            # Extract description
            desc_selectors = [
                '.course-content .description',
                '.content-body .description',
                '.course-overview',
                '.course-summary',
                '.course-details .description',
                'main .description',
                '.content .description',
                'article .description',
                '.course-intro',
                '.course-abstract',
                'div[class*="course"] div[class*="description"]',
                'div[class*="content"] p:first-of-type',
                '.overview-content',
                '.description:not([class*="footer"])'
            ]

            course_info['description'] = self.extract_text_content(soup, desc_selectors, "description", 50)

            # Extract Target Audience
            target_audience_selectors = [
                '.target-audience',
                '.audience',
                '[class*="target"] [class*="audience"]',
                '[class*="audience"]',
                '.intended-audience',
                '.for-whom',
                '.who-should-attend'
            ]

            course_info['target_audience'] = self.extract_text_content(soup, target_audience_selectors, "target audience", 20)

            # Extract Course Objectives
            objectives_selectors = [
                '.learning-objectives li',
                '.course-objectives li',
                '.objectives li',
                '.outcomes li',
                '.goals li',
                '.learning-outcomes li',
                'ul[class*="objective"] li',
                'ul[class*="outcome"] li',
                'ul[class*="goal"] li',
                '.objective-list li',
                '.learning-outcome li'
            ]

            course_info['course_objectives'] = self.extract_list_content(soup, objectives_selectors, "objectives")

            # Extract Course Outline
            outline_selectors = [
                '.course-outline li',
                '.outline li',
                '.curriculum li',
                '.course-curriculum li',
                '.syllabus li',
                '.course-content li',
                '.modules li',
                '.course-modules li',
                '.topics li',
                '.course-topics li',
                'ul[class*="outline"] li',
                'ul[class*="curriculum"] li',
                'ul[class*="syllabus"] li',
                'ul[class*="module"] li',
                'ul[class*="topic"] li'
            ]

            course_info['course_outline'] = self.extract_list_content(soup, outline_selectors, "outline")

            # Enhanced duration and level search in filtered text
            import re
            # Get text from main content areas only, excluding footer
            main_areas = soup.select('main, .main, .content, .course-content, article')
            main_text = ""
            for area in main_areas:
                main_text += " " + area.get_text()

            if not main_text:  # Fallback to full page if no main areas found
                main_text = soup.get_text()

            # Duration patterns
            duration_patterns = [
                r'Duration:\\s*([^\\n\\r,]+)',
                r'Time:\\s*([^\\n\\r,]+)',
                r'Length:\\s*([^\\n\\r,]+)',
                r'(\\d+)\\s*(?:minute|min|hour|hr)s?\\b',
                r'(?:Takes?|Lasts?)\\s*(?:about\\s*)?(\\d+\\s*(?:minute|min|hour|hr)s?)',
                r'Estimated\\s*time:\\s*([^\\n\\r,]+)',
                r'Course\\s*length:\\s*([^\\n\\r,]+)'
            ]

            for pattern in duration_patterns:
                match = re.search(pattern, main_text, re.IGNORECASE)
                if match:
                    duration_text = match.group(1 if '(' in pattern else 0).strip()
                    if duration_text and len(duration_text) < 100:
                        course_info['duration'] = duration_text
                        print(f"  Found duration: {duration_text}")
                        break

            # Level extraction from main content only
            level_patterns = [
                r'Level:\\s*([^\\n\\r,]+)',
                r'Difficulty:\\s*([^\\n\\r,]+)',
                r'\\b(Beginner|Intermediate|Advanced|Expert|Basic|Introductory)\\b'
            ]

            for pattern in level_patterns:
                match = re.search(pattern, main_text, re.IGNORECASE)
                if match:
                    level = match.group(1).strip()
                    if len(level) < 50:
                        course_info['level'] = level
                        print(f"  Found level: {course_info['level']}")
                        break

            # Prerequisites
            prereq_selectors = [
                '.prerequisites',
                '.requirements',
                '.pre-requisites',
                '.course-requirements',
                '[class*="prerequisite"]',
                '[class*="requirement"]'
            ]

            course_info['prerequisites'] = self.extract_text_content(soup, prereq_selectors, "prerequisites", 5)

            # Success indicator
            extracted_fields = sum([
                bool(course_info['extracted_title']),
                bool(course_info['description']),
                bool(course_info['target_audience']),
                bool(course_info['course_objectives']),
                bool(course_info['course_outline']),
                bool(course_info['duration']),
                bool(course_info['level']),
                bool(course_info['prerequisites'])
            ])

            print(f"  Extracted {extracted_fields}/8 fields")

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

        print(f"\\nStarting FULL ENHANCED extraction of {len(courses)} courses...")
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
                        content.get('target_audience') or
                        content.get('course_objectives') or
                        content.get('course_outline') or
                        content.get('duration') or
                        content.get('level')):
                        successful_extractions += 1

                extraction_time = time.time() - start_time
                print(f"  Time: {extraction_time:.1f}s")

                # Save intermediate results every 20 courses
                if i % 20 == 0:
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
        filename = f"enhanced_extraction_progress_{processed}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'successful': successful,
                'extraction_date': datetime.now().isoformat(),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        print(f"  Saved progress to {filename}")

    def save_final_results(self, results, successful_count):
        """Save final enhanced results"""

        final_data = {
            'extraction_date': datetime.now().isoformat(),
            'total_courses': len(results),
            'successful_extractions': successful_count,
            'success_rate': f"{successful_count/len(results)*100:.1f}%" if results else "0%",
            'courses': results
        }

        # Save complete enhanced results
        with open('final_enhanced_course_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        # Create enhanced CSV with all new fields
        with open('final_enhanced_courses_with_content.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'title', 'url', 'description', 'target_audience', 'course_objectives',
                'course_outline', 'duration', 'level', 'prerequisites', 'page_length'
            ])

            for course in results:
                writer.writerow([
                    course.get('title', ''),
                    course.get('url', ''),
                    course.get('description', ''),
                    course.get('target_audience', ''),
                    '; '.join(course.get('course_objectives', [])),
                    '; '.join(course.get('course_outline', [])),
                    course.get('duration', ''),
                    course.get('level', ''),
                    course.get('prerequisites', ''),
                    course.get('page_length', 0)
                ])

        print(f"\\n=== Final Enhanced Results ===")
        print(f"Total courses processed: {len(results)}")
        print(f"Successful content extractions: {successful_count}")
        print(f"Success rate: {successful_count/len(results)*100:.1f}%")
        print(f"\\nFinal enhanced files saved:")
        print(f"- final_enhanced_course_extraction.json (complete enhanced data)")
        print(f"- final_enhanced_courses_with_content.csv (enhanced spreadsheet format)")


def main():
    """Main function"""

    print("=== Full Enhanced Genesys Course Content Extraction ===")
    print("Processing ALL 142 courses with enhanced fields:")
    print("- Description, Target Audience, Course Objectives, Course Outline")
    print("- Duration, Level, Prerequisites")
    print("This will take approximately 45-60 minutes...")
    print("=" * 60)

    extractor = FullEnhancedGenesysExtractor()

    # Run full enhanced extraction
    results, successful_count = extractor.extract_all_courses()

    if results:
        extractor.save_final_results(results, successful_count)
        print(f"\\nFull enhanced extraction complete!")
        print(f"Successfully extracted enhanced content from {successful_count}/{len(results)} courses")
    else:
        print(f"\\nFull enhanced extraction failed - check ChromeDriver setup")


if __name__ == "__main__":
    main()