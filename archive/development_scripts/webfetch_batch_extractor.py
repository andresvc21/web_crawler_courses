"""
Batch WebFetch Content Extractor for Genesys Courses
Uses WebFetch API to try extracting course information
"""

import json
import time
from datetime import datetime


def load_courses():
    """Load the course list"""
    try:
        with open('found_courses_clean.json', 'r', encoding='utf-8') as f:
            courses = json.load(f)
        return courses
    except Exception as e:
        print(f"Error loading courses: {e}")
        return []


def test_webfetch_extraction():
    """Test WebFetch on sample courses with detailed prompts"""

    courses = load_courses()
    if not courses:
        print("No courses to test!")
        return

    # Test on first 5 courses
    sample_courses = courses[:5]

    print(f"Testing WebFetch extraction on {len(sample_courses)} courses...")

    # Since I can't directly call WebFetch here, I'll provide the URLs and prompts
    # that should be used

    extraction_plan = {
        'method': 'WebFetch API calls',
        'courses_to_test': [],
        'extraction_prompts': {
            'detailed_course_info': "Extract comprehensive course information including: course title, detailed description, duration/length, difficulty level, learning objectives, prerequisites, target audience, and any other educational metadata. Look for any structured data, JSON-LD, or course catalog information embedded in the page.",
            'duration_focused': "Focus specifically on finding the course duration, length, or time commitment. Look for patterns like '30 minutes', '1 hour', 'Duration:', 'Time:', or similar time indicators anywhere in the content.",
            'description_focused': "Extract the main course description, overview, summary, or learning objectives. Look for structured course information, educational content descriptions, or any text that explains what the course covers."
        }
    }

    for course in sample_courses:
        extraction_plan['courses_to_test'].append({
            'title': course['title'],
            'url': course['url'],
            'slug': course['slug']
        })

    # Save the extraction plan
    with open('webfetch_extraction_plan.json', 'w', encoding='utf-8') as f:
        json.dump(extraction_plan, f, indent=2, ensure_ascii=False)

    print("Created WebFetch extraction plan: webfetch_extraction_plan.json")
    return extraction_plan


def create_comprehensive_extraction_approach():
    """Create a comprehensive plan for content extraction"""

    approaches = {
        'approach_1_webfetch': {
            'method': 'WebFetch with detailed prompts',
            'description': 'Use WebFetch API with comprehensive extraction prompts',
            'sample_urls': [
                'https://beyond.genesys.com/explore/course/edge-troubleshooting',
                'https://beyond.genesys.com/explore/course/api-workforce-management',
                'https://beyond.genesys.com/explore/course/social-listening-setup-and-configuration',
                'https://beyond.genesys.com/explore/course/aibots-virtual-agent-setup-and-configuration',
                'https://beyond.genesys.com/explore/course/gamification-concepts'
            ],
            'prompts': [
                "Extract all available course information from this Genesys training page. Include: course title, description, duration, difficulty level, learning objectives, prerequisites, target audience, and any structured educational data. Look for JSON-LD, metadata, or embedded course catalog information.",
                "Focus on finding the course duration, time commitment, or length. Search for patterns like '30 minutes', '1-2 hours', 'Duration:', 'Estimated time:', or any time-related information.",
                "Extract the main course description, summary, or overview. Look for detailed explanations of what the course covers, learning outcomes, or educational objectives."
            ]
        },
        'approach_2_api_discovery': {
            'method': 'API endpoint discovery',
            'description': 'Look for hidden API endpoints that serve course data',
            'test_urls': [
                'https://beyond.genesys.com/api/courses',
                'https://beyond.genesys.com/api/explore/courses',
                'https://beyond.genesys.com/api/v1/courses',
                'https://beyond.genesys.com/api/catalog',
                'https://beyond.genesys.com/explore/api/courses'
            ]
        },
        'approach_3_pattern_analysis': {
            'method': 'URL pattern analysis for direct course data',
            'description': 'Test if course data is available through direct API calls',
            'sample_patterns': [
                'https://beyond.genesys.com/api/course/{slug}',
                'https://beyond.genesys.com/api/explore/course/{slug}',
                'https://beyond.genesys.com/data/course/{slug}.json'
            ]
        },
        'approach_4_browser_automation': {
            'method': 'Browser automation with extended waits',
            'description': 'Use Selenium with longer wait times and specific element detection',
            'requirements': 'Fix Chrome driver architecture issue or use alternative browser'
        }
    }

    # Save comprehensive approach
    with open('extraction_approaches.json', 'w', encoding='utf-8') as f:
        json.dump(approaches, f, indent=2, ensure_ascii=False)

    print("Created comprehensive extraction approaches: extraction_approaches.json")
    return approaches


if __name__ == "__main__":
    print("=== Batch WebFetch Content Extraction Setup ===\n")

    # Create extraction plan
    plan = test_webfetch_extraction()

    # Create comprehensive approaches
    approaches = create_comprehensive_extraction_approach()

    print("\n=== Next Steps ===")
    print("1. Use the WebFetch extraction plan to test sample courses")
    print("2. Try API endpoint discovery")
    print("3. Fix browser automation if needed")
    print("4. Consider reaching out to Genesys for official API access")

    print(f"\nFiles created:")
    print("- webfetch_extraction_plan.json")
    print("- extraction_approaches.json")