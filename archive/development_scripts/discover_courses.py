"""
Course discovery script for Genesys Beyond platform
"""

import requests
import json
import time
from bs4 import BeautifulSoup

def discover_genesys_structure():
    """Discover how Genesys courses are structured"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    print("=== Discovering Genesys Course Structure ===")

    # Test different endpoints
    test_urls = [
        "https://beyond.genesys.com/explore/search;s=;p=1",
        "https://beyond.genesys.com/explore/course/genesys-cloud-social-listening-setup-and-configuration",
        "https://beyond.genesys.com/api/explore/search",  # Potential API
        "https://beyond.genesys.com/explore",
        "https://beyond.genesys.com"
    ]

    results = {}

    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content-Length: {len(response.content)}")

            # Check if redirect occurred
            if response.history:
                print(f"Redirected from: {response.history[0].url}")
                print(f"Final URL: {response.url}")

            results[url] = {
                'status_code': response.status_code,
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', 'unknown'),
                'final_url': response.url
            }

            # Look for JavaScript frameworks or API calls in the HTML
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for script tags that might load course data
                scripts = soup.find_all('script', src=True)
                print(f"External scripts: {len(scripts)}")

                # Look for inline scripts that might have API endpoints
                inline_scripts = soup.find_all('script', src=False)
                print(f"Inline scripts: {len(inline_scripts)}")

                # Check for common SPA frameworks
                frameworks = []
                content = response.text.lower()
                if 'angular' in content:
                    frameworks.append('Angular')
                if 'react' in content:
                    frameworks.append('React')
                if 'vue' in content:
                    frameworks.append('Vue')
                if 'next' in content:
                    frameworks.append('Next.js')

                if frameworks:
                    print(f"Detected frameworks: {', '.join(frameworks)}")

        except requests.RequestException as e:
            print(f"Error: {e}")
            results[url] = {'error': str(e)}

        time.sleep(2)  # Be respectful

    return results

def try_known_course_patterns():
    """Try to find courses using known URL patterns"""

    print("\n=== Trying Known Course Patterns ===")

    # Based on the provided sample URL, try variations
    base_patterns = [
        "https://beyond.genesys.com/explore/course/",
        "https://beyond.genesys.com/course/",
        "https://beyond.genesys.com/learn/",
        "https://beyond.genesys.com/training/"
    ]

    # Common Genesys Cloud course topics
    course_topics = [
        "genesys-cloud-basics",
        "genesys-cloud-introduction",
        "genesys-cloud-admin-fundamentals",
        "genesys-cloud-agent-training",
        "genesys-cloud-contact-center",
        "genesys-cloud-routing",
        "genesys-cloud-analytics",
        "genesys-cloud-workforce-management",
        "genesys-cloud-voice-configuration",
        "genesys-cloud-digital-messaging",
        "genesys-cloud-integration",
        "genesys-cloud-api-fundamentals",
        "social-listening-setup-and-configuration",
        "workforce-optimization",
        "predictive-engagement"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    found_courses = []

    for base in base_patterns:
        print(f"\nTrying base pattern: {base}")

        for topic in course_topics:
            url = base + topic
            try:
                response = requests.head(url, headers=headers, timeout=10)  # Use HEAD to be faster

                if response.status_code == 200:
                    print(f"  FOUND: {topic}")
                    found_courses.append({
                        'title': topic.replace('-', ' ').title(),
                        'url': url,
                        'pattern': base
                    })
                elif response.status_code == 404:
                    print(f"  Not found: {topic}")
                else:
                    print(f"  Status {response.status_code}: {topic}")

            except requests.RequestException as e:
                print(f"  Error {topic}: {e}")

            time.sleep(0.5)  # Small delay

    return found_courses

def save_discovery_results(structure_results, course_results):
    """Save discovery results to files"""

    discovery_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'structure_analysis': structure_results,
        'found_courses': course_results,
        'total_courses_found': len(course_results)
    }

    # Save to JSON
    with open('genesys_discovery.json', 'w', encoding='utf-8') as f:
        json.dump(discovery_data, f, indent=2, ensure_ascii=False)

    print(f"\nDiscovery results saved to 'genesys_discovery.json'")
    print(f"Found {len(course_results)} potential courses")

if __name__ == "__main__":
    print("Starting Genesys course discovery...\n")

    # Discover site structure
    structure_results = discover_genesys_structure()

    # Try to find courses with known patterns
    course_results = try_known_course_patterns()

    # Save results
    save_discovery_results(structure_results, course_results)

    print("\n=== Discovery Complete ===")
    print(f"Check 'genesys_discovery.json' for detailed results")

    if course_results:
        print(f"\nFound {len(course_results)} courses:")
        for course in course_results[:10]:  # Show first 10
            print(f"- {course['title']}")
            print(f"  {course['url']}")
    else:
        print("\nNo courses found with standard URL patterns")
        print("The site likely uses JavaScript rendering and requires browser automation")