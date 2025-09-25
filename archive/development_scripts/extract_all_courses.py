"""
Complete Genesys Course Extractor
Processes the 142 actual course titles and extracts full course information
"""

import json
import csv
import time
import re
import requests
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup


def read_course_titles(filename):
    """Read course titles from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            titles = [line.strip() for line in f if line.strip()]
        print(f"Read {len(titles)} course titles from {filename}")
        return titles
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []


def title_to_slug(title):
    """Convert course title to URL slug"""
    # Remove special prefixes and clean up
    title = title.replace("Genesys Cloud:", "").replace("Genesys Cloud CX:", "").replace("CX Cloud from Genesys and Salesforce", "")
    title = title.replace("Introduction to", "").strip()

    # Convert to lowercase and replace special characters
    slug = title.lower()

    # Remove extra spaces and special characters
    slug = re.sub(r'[^\w\s-]', '', slug)  # Keep only word chars, spaces, and hyphens
    slug = re.sub(r'\s+', '-', slug)      # Replace spaces with hyphens
    slug = re.sub(r'-+', '-', slug)       # Replace multiple hyphens with single
    slug = slug.strip('-')                # Remove leading/trailing hyphens

    return slug


def generate_slug_variations(title):
    """Generate multiple slug variations to try"""
    variations = []

    # Primary slug
    primary = title_to_slug(title)
    variations.append(primary)

    # Try without common prefixes
    no_prefix_patterns = [
        r'^genesys-cloud-cx-?',
        r'^genesys-cloud-?',
        r'^introduction-to-?',
        r'^cx-cloud-from-genesys-and-salesforce-?'
    ]

    for pattern in no_prefix_patterns:
        variation = re.sub(pattern, '', primary)
        if variation and variation != primary:
            variations.append(variation)

    # Try with simplified versions
    simplified = primary.replace('genesys-cloud-cx', 'genesys-cloud')
    if simplified != primary:
        variations.append(simplified)

    # Try with different common word replacements
    replacements = [
        ('configuration', 'config'),
        ('management', 'mgmt'),
        ('administration', 'admin'),
        ('supervisor', 'sup'),
        ('development', 'dev')
    ]

    for old, new in replacements:
        if old in primary:
            variation = primary.replace(old, new)
            variations.append(variation)

    return list(dict.fromkeys(variations))  # Remove duplicates while preserving order


def test_url_exists(url, headers, timeout=10):
    """Test if URL exists and is accessible"""
    try:
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False


def extract_course_details(url, headers, timeout=15):
    """Extract course details from the course page using WebFetch-style approach"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Since the site is JavaScript-heavy, we might get minimal content
        # But let's try to extract what we can from the HTML
        details = {
            'title_from_page': '',
            'description': '',
            'duration': '',
            'level': '',
            'objectives': [],
            'prerequisites': '',
            'page_content_length': len(response.content)
        }

        # Try to extract title from various sources
        title_selectors = [
            'title',
            'h1',
            '.course-title',
            '.title',
            '[class*="title"]'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                details['title_from_page'] = element.get_text().strip()
                break

        # Try to extract description
        desc_selectors = [
            '.description',
            '.course-description',
            '.overview',
            '.summary',
            '[class*="description"]',
            'meta[name="description"]'
        ]

        for selector in desc_selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    details['description'] = element.get('content').strip()
                    break
            else:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    details['description'] = element.get_text().strip()
                    break

        # Try to extract duration
        duration_patterns = [
            r'(\d+)\s*(?:minute|min|hour|hr)s?',
            r'Duration:\s*([^\n\r]+)',
            r'Time:\s*([^\n\r]+)'
        ]

        page_text = soup.get_text()
        for pattern in duration_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                details['duration'] = match.group(0)
                break

        # Look for course metadata in JSON-LD or other structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'name' in data and not details['title_from_page']:
                        details['title_from_page'] = data['name']
                    if 'description' in data and not details['description']:
                        details['description'] = data['description']
                    if 'duration' in data and not details['duration']:
                        details['duration'] = data['duration']
            except:
                continue

        return details

    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None


def process_all_courses():
    """Process all 142 courses"""
    print("=== Processing All 142 Genesys Courses ===\n")

    # Read course titles
    titles = read_course_titles('courses_titles.txt')
    if not titles:
        print("No course titles found!")
        return

    base_url = "https://beyond.genesys.com/explore/course/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    results = []
    found_courses = []
    not_found_courses = []

    for i, title in enumerate(titles, 1):
        print(f"\n[{i}/142] Processing: {title}")

        # Generate slug variations
        variations = generate_slug_variations(title)
        print(f"  Trying {len(variations)} URL variations...")

        course_data = {
            'original_title': title,
            'course_number': i,
            'slug': '',
            'url': '',
            'found': False,
            'details': None,
            'variations_tried': variations
        }

        # Try each variation
        for j, slug in enumerate(variations, 1):
            url = base_url + slug
            print(f"    {j}. Testing: {slug[:50]}{'...' if len(slug) > 50 else ''}")

            if test_url_exists(url, headers):
                print(f"    SUCCESS! Found working URL")
                course_data['slug'] = slug
                course_data['url'] = url
                course_data['found'] = True

                # Extract course details
                print(f"    Extracting course details...")
                details = extract_course_details(url, headers)
                course_data['details'] = details

                found_courses.append(course_data)
                break
            else:
                print(f"    Not found")

            time.sleep(0.3)  # Small delay between requests

        if not course_data['found']:
            print(f"    No working URL found for: {title}")
            not_found_courses.append(course_data)

        results.append(course_data)
        time.sleep(1)  # Delay between courses to be respectful

        # Save intermediate results every 10 courses
        if i % 10 == 0:
            save_intermediate_results(results, i)

    # Final summary
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total courses processed: {len(results)}")
    print(f"Successfully found: {len(found_courses)}")
    print(f"Not found: {len(not_found_courses)}")

    # Save final results
    save_final_results(results, found_courses, not_found_courses)

    return results


def save_intermediate_results(results, processed_count):
    """Save intermediate results"""
    filename = f"intermediate_results_{processed_count}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"    Saved intermediate results to {filename}")


def save_final_results(all_results, found_courses, not_found_courses):
    """Save final comprehensive results"""

    # Complete dataset
    final_data = {
        'extraction_date': datetime.now().isoformat(),
        'total_courses_in_list': 142,
        'successfully_found': len(found_courses),
        'not_found': len(not_found_courses),
        'success_rate': f"{len(found_courses)/142*100:.1f}%",
        'base_url': 'https://beyond.genesys.com/explore/course/',
        'all_results': all_results
    }

    # Save complete results
    with open('complete_course_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    # Save just the found courses in a clean format
    clean_found_courses = []
    for course in found_courses:
        clean_course = {
            'title': course['original_title'],
            'url': course['url'],
            'slug': course['slug'],
            'found': True
        }

        # Add details if available
        if course['details']:
            clean_course.update({
                'title_from_page': course['details'].get('title_from_page', ''),
                'description': course['details'].get('description', ''),
                'duration': course['details'].get('duration', ''),
                'level': course['details'].get('level', ''),
                'page_content_length': course['details'].get('page_content_length', 0)
            })

        clean_found_courses.append(clean_course)

    # Save found courses to JSON
    with open('found_courses_clean.json', 'w', encoding='utf-8') as f:
        json.dump(clean_found_courses, f, indent=2, ensure_ascii=False)

    # Save found courses to CSV
    if clean_found_courses:
        with open('found_courses_clean.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=clean_found_courses[0].keys())
            writer.writeheader()
            writer.writerows(clean_found_courses)

    # Save not found courses for analysis
    with open('not_found_courses.json', 'w', encoding='utf-8') as f:
        json.dump([course['original_title'] for course in not_found_courses], f, indent=2)

    print(f"\nFiles saved:")
    print(f"- complete_course_extraction.json (full details)")
    print(f"- found_courses_clean.json ({len(found_courses)} courses)")
    print(f"- found_courses_clean.csv ({len(found_courses)} courses)")
    print(f"- not_found_courses.json ({len(not_found_courses)} courses)")


if __name__ == "__main__":
    try:
        results = process_all_courses()
        print("\n=== Extraction Complete! ===")

    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user")
        print("Partial results may be saved in intermediate files")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Check intermediate result files for partial data")