"""
Create proper URLs for all 142 course titles
Keeps full title content, just converts to proper URL format
"""

import requests
import time
import csv
import json
import re


def title_to_proper_slug(title):
    """Convert title to proper URL slug without removing content"""

    # Start with the full title in lowercase
    slug = title.lower()

    # Replace common patterns
    slug = slug.replace(":", "")           # Remove colons
    slug = slug.replace(" - ", "-")        # Convert " - " to single hyphen
    slug = slug.replace("/", "-")          # Convert / to hyphen
    slug = slug.replace("'s", "s")         # Remove apostrophe s
    slug = slug.replace("'", "")           # Remove apostrophes
    slug = slug.replace("&", "and")        # Convert & to and

    # Remove other special characters but keep letters, numbers, spaces, hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Replace multiple spaces with single space
    slug = re.sub(r'\s+', ' ', slug)

    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")

    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def create_and_test_all_urls():
    """Create URLs for all 142 courses and test them"""

    print("Creating URLs for all 142 course titles...")

    # Read all course titles
    with open('courses_titles.txt', 'r', encoding='utf-8') as f:
        titles = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(titles)} course titles...")

    base_url = "https://beyond.genesys.com/explore/course/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    all_courses = []
    working_courses = []
    failed_courses = []

    for i, title in enumerate(titles, 1):
        print(f"\n[{i}/142] {title}")

        # Convert title to slug
        slug = title_to_proper_slug(title)
        url = base_url + slug

        print(f"  Slug: {slug}")
        print(f"  URL: {url}")

        # Test the URL
        try:
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)

            course_data = {
                'title': title,
                'slug': slug,
                'url': url,
                'status_code': response.status_code,
                'working': response.status_code == 200,
                'final_url': response.url if response.history else url
            }

            if response.status_code == 200:
                print(f"  Status: WORKING ({response.status_code})")
                working_courses.append(course_data)
            else:
                print(f"  Status: FAILED ({response.status_code})")
                failed_courses.append(course_data)

            all_courses.append(course_data)

        except Exception as e:
            print(f"  Status: ERROR - {str(e)[:50]}")
            course_data = {
                'title': title,
                'slug': slug,
                'url': url,
                'error': str(e),
                'working': False
            }
            all_courses.append(course_data)
            failed_courses.append(course_data)

        time.sleep(0.5)  # Be respectful to server

    return all_courses, working_courses, failed_courses


def save_results(all_courses, working_courses, failed_courses):
    """Save the URL generation results"""

    print(f"\n=== URL Generation Results ===")
    print(f"Total courses: {len(all_courses)}")
    print(f"Working URLs: {len(working_courses)}")
    print(f"Failed URLs: {len(failed_courses)}")
    print(f"Success rate: {len(working_courses)/len(all_courses)*100:.1f}%")

    # Save complete results
    complete_results = {
        'generation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_courses': len(all_courses),
        'working_courses': len(working_courses),
        'failed_courses': len(failed_courses),
        'success_rate': f"{len(working_courses)/len(all_courses)*100:.1f}%",
        'all_courses': all_courses,
        'working_courses': working_courses,
        'failed_courses': failed_courses
    }

    with open('complete_url_results.json', 'w', encoding='utf-8') as f:
        json.dump(complete_results, f, indent=2, ensure_ascii=False)

    # Save working courses CSV (for Chrome extraction)
    with open('all_working_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'url'])
        for course in working_courses:
            writer.writerow([course['title'], course['url']])

    # Save working courses JSON
    with open('all_working_courses.json', 'w', encoding='utf-8') as f:
        json.dump(working_courses, f, indent=2, ensure_ascii=False)

    # Save failed courses for analysis
    if failed_courses:
        with open('failed_courses.json', 'w', encoding='utf-8') as f:
            json.dump(failed_courses, f, indent=2, ensure_ascii=False)

    print(f"\nFiles created:")
    print(f"- all_working_courses.csv ({len(working_courses)} courses for extraction)")
    print(f"- all_working_courses.json ({len(working_courses)} courses)")
    print(f"- complete_url_results.json (full details)")
    if failed_courses:
        print(f"- failed_courses.json ({len(failed_courses)} failed URLs)")

    return len(working_courses)


def show_sample_urls(working_courses, num_samples=5):
    """Show sample working URLs"""

    print(f"\nSample working URLs:")
    for i, course in enumerate(working_courses[:num_samples], 1):
        print(f"{i}. {course['title']}")
        print(f"   {course['url']}")

    if len(working_courses) > num_samples:
        print(f"   ... and {len(working_courses) - num_samples} more")


def main():
    """Main function"""

    print("=== Genesys Course URL Generator ===")
    print("Converting all 142 course titles to proper URLs...\n")

    # Create and test all URLs
    all_courses, working_courses, failed_courses = create_and_test_all_urls()

    # Save results
    working_count = save_results(all_courses, working_courses, failed_courses)

    # Show samples
    if working_courses:
        show_sample_urls(working_courses)

    print(f"\n=== Ready for Content Extraction ===")
    if working_count > 0:
        print(f"✓ {working_count} working URLs ready for Chrome extraction")
        print(f"✓ Use 'all_working_courses.csv' with the Chrome extractor")
    else:
        print("✗ No working URLs found - check the slug generation logic")

    print(f"\nNext step: Run Chrome extraction on all working courses!")


if __name__ == "__main__":
    main()