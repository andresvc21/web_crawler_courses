"""
Fast URL generator for all 142 courses
Since we know the pattern works, just generate all URLs quickly
"""

import csv
import json
import re


def title_to_proper_slug(title):
    """Convert title to proper URL slug keeping full content"""

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


def generate_all_urls():
    """Generate URLs for all 142 courses quickly"""

    print("Generating URLs for all 142 courses...")

    # Read all course titles
    with open('courses_titles.txt', 'r', encoding='utf-8') as f:
        titles = [line.strip() for line in f if line.strip()]

    base_url = "https://beyond.genesys.com/explore/course/"
    all_courses = []

    for i, title in enumerate(titles, 1):
        slug = title_to_proper_slug(title)
        url = base_url + slug

        course = {
            'title': title,
            'slug': slug,
            'url': url
        }

        all_courses.append(course)
        print(f"{i}/142: {title} -> {slug}")

    return all_courses


def save_all_courses(courses):
    """Save all course URLs"""

    # Save as CSV for Chrome extraction
    with open('all_142_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'url'])
        for course in courses:
            writer.writerow([course['title'], course['url']])

    # Save as JSON
    with open('all_142_courses.json', 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"\nFiles created:")
    print(f"- all_142_courses.csv (for Chrome extraction)")
    print(f"- all_142_courses.json (structured data)")


def main():
    """Main function"""

    print("=== Fast URL Generator for All 142 Courses ===\n")

    courses = generate_all_urls()
    save_all_courses(courses)

    print(f"\n=== Ready for Full Extraction ===")
    print(f"✓ Generated {len(courses)} course URLs")
    print(f"✓ Ready to run Chrome extraction on all courses")

    # Show samples
    print(f"\nSample URLs:")
    for i, course in enumerate(courses[:3], 1):
        print(f"{i}. {course['title']}")
        print(f"   {course['url']}")


if __name__ == "__main__":
    main()