"""
Universal Genesys Learning Content Extractor
Configurable extraction system for e-learning, webinars, and self-study materials
"""

import json
import csv
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional
import os

@dataclass
class LearningContent:
    """Data structure for learning content"""
    title: str
    url: str
    content_type: str  # e-learning, webinar, self-study
    description: str = ""
    learning_type: str = ""
    duration: str = ""
    course_outline: List[str] = None
    target_audience: List[str] = None
    extraction_timestamp: str = ""
    page_length: int = 0

    def __post_init__(self):
        if self.course_outline is None:
            self.course_outline = []
        if self.target_audience is None:
            self.target_audience = []

class UniversalGenesysExtractor:
    """Universal extractor for different types of Genesys learning content"""

    def __init__(self, config_file="config.json"):
        """Initialize with configuration file"""
        self.config = self.load_config(config_file)
        self.driver = None
        self.results = []

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None

    def setup_driver(self):
        """Setup Chrome driver with configured options"""
        chrome_options = Options()
        browser_settings = self.config.get('global_settings', {}).get('browser_settings', {})

        if browser_settings.get('headless', False):
            chrome_options.add_argument('--headless')
        if browser_settings.get('disable_gpu', True):
            chrome_options.add_argument('--disable-gpu')
        if browser_settings.get('no_sandbox', True):
            chrome_options.add_argument('--no-sandbox')

        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')

        window_size = browser_settings.get('window_size', '1920,1080')
        chrome_options.add_argument(f'--window-size={window_size}')

        driver_path = self.config.get('global_settings', {}).get('chrome_driver_path', './chromedriver.exe')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"Chrome driver setup successful!")
            return True
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return False

    def load_course_list(self, content_type):
        """Load course list for specific content type"""
        content_config = self.config['course_types'].get(content_type)
        if not content_config:
            print(f"No configuration found for content type: {content_type}")
            return []

        input_file = content_config['input_file']

        if not os.path.exists(input_file):
            print(f"Input file not found: {input_file}")
            print(f"Please create {input_file} with list of {content_type} titles")
            return []

        courses = []
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    title = line.strip()
                    if title and not title.startswith('#'):  # Skip empty lines and comments
                        # Generate URL from title
                        url_base = content_config['url_base']
                        slug = self.generate_slug(title)
                        url = f"{url_base}{slug}"
                        courses.append({'title': title, 'url': url})

            print(f"Loaded {len(courses)} {content_type} items from {input_file}")
            return courses
        except Exception as e:
            print(f"Error loading {input_file}: {e}")
            return []

    def generate_slug(self, title):
        """Generate URL slug from title"""
        # Remove common prefixes
        prefixes_to_remove = [
            "Genesys Cloud CX: ",
            "Genesys Cloud: ",
            "Introduction to ",
            "CX Cloud from Genesys and Salesforce: ",
            "CX Cloud from Genesys and Salesforce - "
        ]

        slug = title
        for prefix in prefixes_to_remove:
            if slug.startswith(prefix):
                slug = slug[len(prefix):]
                break

        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')

        return slug

    def extract_target_audience_enhanced(self, page_text):
        """Enhanced target audience extraction using proven header pattern"""
        # Standardized audience types
        audience_types = {
            'developer': 'Developers',
            'system administrator': 'System Administrators',
            'administrator': 'Administrators',
            'supervisor': 'Supervisors',
            'manager': 'Managers',
            'agent': 'Agents',
            'business user': 'Business Users',
            'analyst': 'Analysts',
            'contact center manager': 'Contact Center Managers',
            'it professional': 'IT Professionals'
        }

        # Header patterns that worked in our previous extraction
        header_patterns = [
            r'Target\s+Audience[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Intended\s+Audience[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'This\s+course\s+is\s+for[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Designed\s+for[:\s]*([^\.]+?)(?:Course\s+(?:Objectives|Prerequisites))',
            r'Target\s+Audience[:\s]*([^\.]+?)(?:Overview|Introduction)',
            r'Intended\s+Audience[:\s]*([^\.]+?)(?:Overview|Introduction)'
        ]

        def detect_audiences_in_text(text):
            detected = []
            text_lower = text.lower()

            for key, standard_name in audience_types.items():
                if key in text_lower and standard_name not in detected:
                    detected.append(standard_name)

            return detected

        # Try header patterns first
        for pattern in header_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                context = match.group(1).strip()
                detected = detect_audiences_in_text(context)
                if detected:
                    return detected, "Header pattern"

        return [], "Not found"

    def extract_content_info(self, content_type, course_data):
        """Extract information for a specific course"""
        content_config = self.config['course_types'][content_type]
        extraction_settings = content_config['extraction_settings']

        print(f"Loading: {course_data['title'][:60]}...")

        try:
            # Load the page
            self.driver.get(course_data['url'])

            # Wait for content to load
            wait_time = extraction_settings.get('wait_time', 10)
            print(f"  Waiting {wait_time}s for content...")
            time.sleep(wait_time)

            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = soup.get_text()

            # Create content object
            content = LearningContent(
                title=course_data['title'],
                url=course_data['url'],
                content_type=content_type,
                extraction_timestamp=datetime.now().isoformat(),
                page_length=len(page_text)
            )

            # Extract description
            if extraction_settings.get('extract_descriptions', True):
                content.description = self.extract_description(soup, content_config['css_selectors'])

            # Extract target audience
            if extraction_settings.get('extract_target_audience', True):
                print(f"  Searching for target audience...")
                audiences, method = self.extract_target_audience_enhanced(page_text)
                content.target_audience = audiences
                if audiences:
                    print(f"    Found: {', '.join(audiences)}")
                else:
                    print(f"  - No target audience found")

            # Extract duration
            if extraction_settings.get('extract_duration', True):
                content.duration = self.extract_duration(page_text)

            # Extract course outline
            if extraction_settings.get('extract_course_outline', True):
                content.course_outline = self.extract_course_outline(soup, content_config['css_selectors'])

            # Set learning type based on content type
            content.learning_type = content_config['name']

            return content

        except Exception as e:
            print(f"  Error extracting {course_data['title']}: {e}")
            # Return minimal content object
            return LearningContent(
                title=course_data['title'],
                url=course_data['url'],
                content_type=content_type,
                extraction_timestamp=datetime.now().isoformat()
            )

    def extract_description(self, soup, css_selectors):
        """Extract description using CSS selectors"""
        selectors = css_selectors.get('description', [])

        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) > 50:  # Minimum length for valid description
                        # Clean up the text
                        text = re.sub(r'\s+', ' ', text)
                        return text
            except:
                continue

        return ""

    def extract_duration(self, page_text):
        """Extract duration from page text"""
        duration_patterns = [
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:hours?|hrs?)\s*(\d+)\s*(?:minutes?|mins?)',
            r'Duration[:\s]*(\d+\s*(?:hours?|hrs?|minutes?|mins?))',
            r'Time[:\s]*(\d+\s*(?:hours?|hrs?|minutes?|mins?))'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Hours and minutes
                    hours, minutes = match.groups()
                    return f"{hours} hrs {minutes} mins"
                else:
                    return match.group(1)

        return ""

    def extract_course_outline(self, soup, css_selectors):
        """Extract course outline using CSS selectors"""
        selectors = css_selectors.get('course_outline', [])

        for selector in selectors:
            try:
                elements = soup.select(selector)
                outline = []
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) > 10:
                        outline.append(text)

                if outline:
                    return outline
            except:
                continue

        return []

    def save_results(self, content_type, results):
        """Save results for specific content type"""
        content_config = self.config['course_types'][content_type]
        output_files = content_config['output_files']

        # Prepare data for saving
        results_data = {
            'extraction_info': {
                'content_type': content_type,
                'extraction_date': datetime.now().isoformat(),
                'total_items': len(results),
                'successful_extractions': len([r for r in results if r.description or r.target_audience]),
                'content_type_config': content_config['name']
            },
            'items': []
        }

        for content in results:
            item_data = {
                'title': content.title,
                'url': content.url,
                'content_type': content.content_type,
                'description': content.description,
                'learning_type': content.learning_type,
                'duration': content.duration,
                'course_outline': content.course_outline,
                'target_audience': content.target_audience,
                'extraction_timestamp': content.extraction_timestamp
            }
            results_data['items'].append(item_data)

        # Save JSON
        json_file = output_files['json']
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        # Save CSV
        csv_file = output_files['csv']
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'title', 'url', 'content_type', 'description', 'learning_type',
                'duration', 'course_outline', 'target_audience'
            ])

            for content in results:
                writer.writerow([
                    content.title,
                    content.url,
                    content.content_type,
                    content.description,
                    content.learning_type,
                    content.duration,
                    ' | '.join(content.course_outline) if content.course_outline else '',
                    ' | '.join(content.target_audience) if content.target_audience else ''
                ])

        print(f"Results saved:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")

        return results_data

    def extract_content_type(self, content_type):
        """Extract all content for a specific type"""
        print(f"\n=== Extracting {content_type.upper()} Content ===")

        # Load course list
        courses = self.load_course_list(content_type)
        if not courses:
            return []

        # Setup driver if needed
        if not self.driver:
            if not self.setup_driver():
                return []

        results = []
        total_courses = len(courses)

        for i, course_data in enumerate(courses, 1):
            print(f"\n[{i}/{total_courses}] ", end="")

            start_time = time.time()
            content = self.extract_content_info(content_type, course_data)
            end_time = time.time()

            results.append(content)

            print(f"  Time: {end_time - start_time:.1f}s")

            # Save progress periodically
            save_interval = self.config.get('global_settings', {}).get('progress_save_interval', 20)
            if i % save_interval == 0:
                print(f"  Saved progress to {content_type}_progress_{i}.json")
                temp_data = self.save_results(f"{content_type}_temp", results)

        # Save final results
        final_data = self.save_results(content_type, results)

        print(f"\n=== {content_type.upper()} Extraction Complete ===")
        print(f"Total items processed: {len(results)}")
        print(f"Items with descriptions: {len([r for r in results if r.description])}")
        print(f"Items with target audiences: {len([r for r in results if r.target_audience])}")

        return results

    def create_combined_dataset(self, all_results):
        """Create combined dataset from all content types"""
        if not self.config.get('combined_output', {}).get('create_combined_dataset', False):
            return

        print("\n=== Creating Combined Dataset ===")

        combined_files = self.config['combined_output']['combined_files']
        all_items = []

        # Combine all results
        for content_type, results in all_results.items():
            all_items.extend(results)

        # Create combined data structure
        combined_data = {
            'dataset_info': {
                'name': self.config['project_info']['name'],
                'version': self.config['project_info']['version'],
                'creation_date': datetime.now().isoformat(),
                'total_items': len(all_items),
                'content_types': list(all_results.keys())
            },
            'statistics': {
                'by_content_type': {
                    ct: len(results) for ct, results in all_results.items()
                },
                'with_target_audience': len([item for item in all_items if item.target_audience]),
                'with_descriptions': len([item for item in all_items if item.description])
            },
            'items': []
        }

        # Add all items
        for item in all_items:
            combined_data['items'].append({
                'title': item.title,
                'url': item.url,
                'content_type': item.content_type,
                'description': item.description,
                'learning_type': item.learning_type,
                'duration': item.duration,
                'course_outline': item.course_outline,
                'target_audience': item.target_audience,
                'extraction_timestamp': item.extraction_timestamp
            })

        # Save combined JSON
        with open(combined_files['json'], 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        # Save combined CSV
        with open(combined_files['csv'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'title', 'url', 'content_type', 'description', 'learning_type',
                'duration', 'course_outline', 'target_audience'
            ])

            for item in all_items:
                writer.writerow([
                    item.title,
                    item.url,
                    item.content_type,
                    item.description,
                    item.learning_type,
                    item.duration,
                    ' | '.join(item.course_outline) if item.course_outline else '',
                    ' | '.join(item.target_audience) if item.target_audience else ''
                ])

        print(f"Combined dataset created:")
        print(f"  JSON: {combined_files['json']}")
        print(f"  CSV: {combined_files['csv']}")
        print(f"  Total items: {len(all_items)}")

        return combined_data

    def run_extraction(self, content_types=None):
        """Run extraction for specified content types"""
        if content_types is None:
            content_types = list(self.config['course_types'].keys())

        print(f"=== Universal Genesys Learning Content Extractor ===")
        print(f"Content types to extract: {', '.join(content_types)}")

        all_results = {}

        try:
            for content_type in content_types:
                if content_type in self.config['course_types']:
                    results = self.extract_content_type(content_type)
                    all_results[content_type] = results
                else:
                    print(f"Warning: Unknown content type '{content_type}'")

            # Create combined dataset if configured
            self.create_combined_dataset(all_results)

        finally:
            if self.driver:
                self.driver.quit()
                print("\nBrowser closed.")

        print(f"\n🎉 Extraction complete for all content types!")
        return all_results

def main():
    """Main execution function"""
    extractor = UniversalGenesysExtractor()

    # For now, just extract e-learning (existing data)
    # In the future, add 'webinars', 'self-study' when lists are provided
    content_types = ['e-learning']

    results = extractor.run_extraction(content_types)

    print(f"\nExtraction Summary:")
    for content_type, items in results.items():
        print(f"  {content_type}: {len(items)} items extracted")

if __name__ == "__main__":
    main()