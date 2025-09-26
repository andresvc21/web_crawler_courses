"""
API Discovery Script for Genesys Course Data
Tests potential API endpoints that might serve course information
"""

import requests
import json
import time


def test_api_endpoints():
    """Test various potential API endpoints for course data"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://beyond.genesys.com',
        'Referer': 'https://beyond.genesys.com/explore/search'
    }

    # Potential API endpoints
    api_endpoints = [
        'https://beyond.genesys.com/api/explore/courses',
        'https://beyond.genesys.com/api/courses',
        'https://beyond.genesys.com/api/v1/courses',
        'https://beyond.genesys.com/api/catalog',
        'https://beyond.genesys.com/api/search',
        'https://beyond.genesys.com/explore/api/courses',
        'https://beyond.genesys.com/explore/api/search',
        'https://beyond.genesys.com/api/content/courses',
        'https://beyond.genesys.com/beyond/api/courses',
        'https://beyond.genesys.com/api/training/courses'
    ]

    # Test specific course endpoints
    sample_course_slugs = [
        'edge-troubleshooting',
        'gamification-concepts',
        'api-workforce-management'
    ]

    course_api_patterns = [
        'https://beyond.genesys.com/api/course/{}',
        'https://beyond.genesys.com/api/explore/course/{}',
        'https://beyond.genesys.com/api/courses/{}',
        'https://beyond.genesys.com/explore/api/course/{}',
        'https://beyond.genesys.com/api/content/course/{}'
    ]

    results = {
        'discovery_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'general_endpoints': [],
        'course_specific_endpoints': [],
        'successful_endpoints': []
    }

    print("=== Testing General API Endpoints ===")

    for endpoint in api_endpoints:
        print(f"Testing: {endpoint}")

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            result = {
                'url': endpoint,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': len(response.content),
                'is_json': False,
                'data_preview': None
            }

            if response.status_code == 200:
                print(f"  ✓ SUCCESS! Status: {response.status_code}")
                print(f"    Content-Type: {result['content_type']}")
                print(f"    Content-Length: {result['content_length']}")

                # Try to parse as JSON
                if 'application/json' in result['content_type']:
                    try:
                        data = response.json()
                        result['is_json'] = True
                        result['data_preview'] = str(data)[:500] + "..." if len(str(data)) > 500 else str(data)
                        print(f"    JSON Data: {result['data_preview'][:100]}...")

                        results['successful_endpoints'].append(endpoint)
                    except:
                        result['data_preview'] = response.text[:200] + "..." if len(response.text) > 200 else response.text

                else:
                    result['data_preview'] = response.text[:200] + "..." if len(response.text) > 200 else response.text

            else:
                print(f"  Status: {response.status_code}")

            results['general_endpoints'].append(result)

        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
            results['general_endpoints'].append({
                'url': endpoint,
                'error': str(e)
            })

        time.sleep(1)  # Be respectful

    print(f"\n=== Testing Course-Specific API Endpoints ===")

    for slug in sample_course_slugs:
        print(f"\nTesting course: {slug}")

        for pattern in course_api_patterns:
            url = pattern.format(slug)
            print(f"  Testing: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=10)
                result = {
                    'url': url,
                    'course_slug': slug,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_length': len(response.content),
                    'is_json': False,
                    'data_preview': None
                }

                if response.status_code == 200:
                    print(f"    ✓ SUCCESS! Status: {response.status_code}")

                    # Try to parse as JSON
                    if 'application/json' in result['content_type']:
                        try:
                            data = response.json()
                            result['is_json'] = True
                            result['data_preview'] = str(data)[:300] + "..." if len(str(data)) > 300 else str(data)
                            print(f"    JSON Data: {result['data_preview'][:50]}...")

                            results['successful_endpoints'].append(url)
                        except:
                            result['data_preview'] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    else:
                        result['data_preview'] = response.text[:200] + "..." if len(response.text) > 200 else response.text

                else:
                    print(f"    Status: {response.status_code}")

                results['course_specific_endpoints'].append(result)

            except Exception as e:
                print(f"    Error: {str(e)[:50]}")
                results['course_specific_endpoints'].append({
                    'url': url,
                    'course_slug': slug,
                    'error': str(e)
                })

            time.sleep(0.5)

    return results


def test_search_api():
    """Test if there's a search API that returns course data"""

    print(f"\n=== Testing Search API Endpoints ===")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://beyond.genesys.com',
        'Referer': 'https://beyond.genesys.com/explore/search'
    }

    search_endpoints = [
        'https://beyond.genesys.com/api/search?q=genesys+cloud',
        'https://beyond.genesys.com/explore/api/search?query=course',
        'https://beyond.genesys.com/api/explore/search?s=&p=1',
        'https://beyond.genesys.com/search?q=training',
        'https://beyond.genesys.com/api/training/search'
    ]

    search_results = []

    for endpoint in search_endpoints:
        print(f"Testing search: {endpoint}")

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"  ✓ SUCCESS! Content length: {len(response.content)}")

                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        print(f"  JSON response with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        search_results.append({
                            'endpoint': endpoint,
                            'status': 'success',
                            'data': data
                        })
                    except:
                        print(f"  Non-JSON response: {response.text[:100]}")
            else:
                print(f"  Status: {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(1)

    return search_results


if __name__ == "__main__":
    print("=== Genesys API Discovery ===")
    print("Testing potential API endpoints for course data...\n")

    # Test API endpoints
    api_results = test_api_endpoints()

    # Test search endpoints
    search_results = test_search_api()

    # Combine results
    all_results = {
        **api_results,
        'search_results': search_results
    }

    # Save results
    with open('api_discovery_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n=== API Discovery Results ===")
    print(f"General endpoints tested: {len(api_results['general_endpoints'])}")
    print(f"Course-specific endpoints tested: {len(api_results['course_specific_endpoints'])}")
    print(f"Successful endpoints found: {len(api_results['successful_endpoints'])}")

    if api_results['successful_endpoints']:
        print(f"\nSuccessful endpoints:")
        for endpoint in api_results['successful_endpoints']:
            print(f"  - {endpoint}")
    else:
        print(f"\nNo direct API endpoints found.")

    print(f"\nResults saved to: api_discovery_results.json")