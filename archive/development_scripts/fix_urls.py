"""
Fix URL slug generation for Genesys courses
"""

import json
import csv
import requests
import time


def improved_title_to_slug(title):
    """Improved slug generation that keeps important prefixes"""
    import re

    # Clean up the title but keep important parts
    slug = title.lower()

    # Replace specific patterns more carefully
    slug = slug.replace("genesys cloud cx:", "genesys-cloud-cx")
    slug = slug.replace("genesys cloud:", "genesys-cloud")
    slug = slug.replace("cx cloud from genesys and salesforce", "cx-cloud-from-genesys-and-salesforce")
    slug = slug.replace("introduction to", "")

    # Handle special cases
    slug = slug.replace("ai/bots", "ai-bots")
    slug = slug.replace("/", "-")
    slug = slug.replace(":", "")
    slug = slug.replace("'s", "s")
    slug = slug.replace("'", "")

    # Convert to lowercase and replace special characters
    slug = re.sub(r'[^\w\s-]', '', slug)  # Keep only word chars, spaces, and hyphens
    slug = re.sub(r'\s+', '-', slug)      # Replace spaces with hyphens
    slug = re.sub(r'-+', '-', slug)       # Replace multiple hyphens with single
    slug = slug.strip('-')                # Remove leading/trailing hyphens

    return slug


def test_and_fix_urls():
    """Test existing URLs and create corrected versions"""

    # Load course titles
    with open('courses_titles.txt', 'r', encoding='utf-8') as f:
        titles = [line.strip() for line in f if line.strip()]

    base_url = "https://beyond.genesys.com/explore/course/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    results = []
    fixed_count = 0

    print("Testing and fixing course URLs...")

    for i, title in enumerate(titles, 1):
        print(f"\n[{i}/142] {title}")

        # Generate improved slug
        improved_slug = improved_title_to_slug(title)
        improved_url = base_url + improved_slug

        # Test the improved URL
        try:
            response = requests.head(improved_url, headers=headers, timeout=10, allow_redirects=True)

            course_data = {
                'original_title': title,
                'improved_slug': improved_slug,
                'improved_url': improved_url,
                'status_code': response.status_code,
                'working': response.status_code == 200,
                'final_url': response.url if response.history else improved_url
            }

            if response.status_code == 200:
                print(f"  ✓ WORKS: {improved_slug}")
                if response.history:
                    print(f"    Redirected to: {response.url}")
            else:
                print(f"  ✗ Status {response.status_code}: {improved_slug}")

                # Try alternative slug patterns for failed ones
                alternatives = generate_alternative_slugs(title)
                for alt_slug in alternatives[:3]:  # Try up to 3 alternatives
                    alt_url = base_url + alt_slug
                    try:
                        alt_response = requests.head(alt_url, headers=headers, timeout=5)
                        if alt_response.status_code == 200:
                            print(f"  ✓ FOUND ALTERNATIVE: {alt_slug}")
                            course_data['improved_slug'] = alt_slug
                            course_data['improved_url'] = alt_url
                            course_data['status_code'] = 200
                            course_data['working'] = True
                            course_data['final_url'] = alt_response.url if alt_response.history else alt_url
                            break
                    except:
                        continue

            results.append(course_data)

            if course_data['working']:
                fixed_count += 1

        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'original_title': title,
                'improved_slug': improved_slug,
                'improved_url': improved_url,
                'error': str(e),
                'working': False
            })

        time.sleep(0.5)  # Be respectful

    return results, fixed_count


def generate_alternative_slugs(title):
    """Generate alternative slug patterns for failed URLs"""
    alternatives = []

    # Keep more of the original structure
    alt1 = title.lower()
    alt1 = alt1.replace("genesys cloud cx:", "genesys-cloud-cx")
    alt1 = alt1.replace("genesys cloud:", "genesys-cloud")  # Keep the prefix
    alt1 = alt1.replace(":", "-")
    alt1 = alt1.replace(" - ", "-")
    alt1 = alt1.replace("/", "-")
    alt1 = alt1.replace("'", "")
    import re
    alt1 = re.sub(r'[^\w\s-]', '', alt1)
    alt1 = re.sub(r'\s+', '-', alt1)
    alt1 = re.sub(r'-+', '-', alt1)
    alt1 = alt1.strip('-')
    alternatives.append(alt1)

    # Try without any prefix removal
    alt2 = title.lower()
    alt2 = alt2.replace(" ", "-")
    alt2 = alt2.replace(":", "")
    alt2 = alt2.replace("/", "-")
    alt2 = alt2.replace("'", "")
    alt2 = re.sub(r'[^\w-]', '', alt2)
    alt2 = re.sub(r'-+', '-', alt2)
    alt2 = alt2.strip('-')
    alternatives.append(alt2)

    # Try with different prefix handling
    alt3 = title.lower()
    if alt3.startswith("genesys cloud cx:"):
        alt3 = alt3[17:].strip()
    elif alt3.startswith("genesys cloud:"):
        alt3 = alt3[14:].strip()
    alt3 = alt3.replace(" ", "-")
    alt3 = alt3.replace(":", "")
    alt3 = alt3.replace("/", "-")
    alt3 = alt3.replace("'", "")
    alt3 = re.sub(r'[^\w-]', '', alt3)
    alt3 = re.sub(r'-+', '-', alt3)
    alt3 = alt3.strip('-')
    alternatives.append(alt3)

    return list(dict.fromkeys(alternatives))  # Remove duplicates


def save_corrected_urls(results, fixed_count):
    """Save the corrected URLs"""

    # Save complete results
    with open('url_correction_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'correction_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_courses': len(results),
            'working_urls': fixed_count,
            'success_rate': f"{fixed_count/len(results)*100:.1f}%",
            'results': results
        }, f, indent=2, ensure_ascii=False)

    # Create corrected CSV with only working URLs
    working_courses = [r for r in results if r.get('working', False)]

    with open('corrected_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'url'])

        for course in working_courses:
            writer.writerow([course['original_title'], course['improved_url']])

    # Create corrected JSON
    clean_courses = []
    for course in working_courses:
        clean_courses.append({
            'title': course['original_title'],
            'url': course['improved_url'],
            'slug': course['improved_slug']
        })

    with open('corrected_courses.json', 'w', encoding='utf-8') as f:
        json.dump(clean_courses, f, indent=2, ensure_ascii=False)

    print(f"\n=== URL Correction Results ===")
    print(f"Total courses: {len(results)}")
    print(f"Working URLs: {fixed_count}")
    print(f"Success rate: {fixed_count/len(results)*100:.1f}%")
    print(f"\nFiles saved:")
    print(f"- corrected_courses.csv ({fixed_count} working courses)")
    print(f"- corrected_courses.json ({fixed_count} working courses)")
    print(f"- url_correction_results.json (complete details)")


if __name__ == "__main__":
    print("=== Fixing Genesys Course URLs ===")
    print("Testing improved slug generation...\n")

    results, fixed_count = test_and_fix_urls()
    save_corrected_urls(results, fixed_count)

    print(f"\nURL correction complete!")
    print(f"Use 'corrected_courses.csv' for the fixed URLs.")