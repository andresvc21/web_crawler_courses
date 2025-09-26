"""
Final comprehensive course extraction for Genesys Beyond platform
Based on discovered URL patterns and known course topics
"""

import json
import csv
import time
import requests
from datetime import datetime

def get_comprehensive_course_list():
    """Generate comprehensive list of Genesys courses based on research"""

    # Base URL pattern we discovered works
    base_url = "https://beyond.genesys.com/explore/course/"

    # Comprehensive list of Genesys Cloud course topics based on their platform features
    course_topics = [
        # Basic courses
        "genesys-cloud-basics",
        "genesys-cloud-introduction",
        "genesys-cloud-fundamentals",
        "getting-started-with-genesys-cloud",

        # Administration
        "genesys-cloud-admin-fundamentals",
        "genesys-cloud-administration",
        "genesys-cloud-user-management",
        "genesys-cloud-org-management",
        "genesys-cloud-security",
        "genesys-cloud-permissions",

        # Agent and Contact Center
        "genesys-cloud-agent-training",
        "genesys-cloud-contact-center",
        "genesys-cloud-agent-experience",
        "contact-center-basics",
        "agent-desktop-training",

        # Voice and Telephony
        "genesys-cloud-voice",
        "genesys-cloud-voice-configuration",
        "genesys-cloud-telephony",
        "voice-routing",
        "sip-trunking",

        # Digital and Messaging
        "genesys-cloud-digital",
        "genesys-cloud-digital-messaging",
        "digital-channels",
        "chat-messaging",
        "social-media-engagement",
        "web-messaging",

        # Routing and Flows
        "genesys-cloud-routing",
        "call-routing",
        "architect-basics",
        "architect-fundamentals",
        "call-flows",
        "interaction-flows",

        # Analytics and Reporting
        "genesys-cloud-analytics",
        "reporting-fundamentals",
        "real-time-reporting",
        "historical-reporting",
        "dashboard-creation",
        "performance-analytics",

        # Workforce Management
        "genesys-cloud-workforce-management",
        "workforce-optimization",
        "forecasting-scheduling",
        "wfm-configuration",

        # API and Integration
        "genesys-cloud-api-fundamentals",
        "genesys-cloud-integration",
        "rest-api-basics",
        "sdk-training",
        "platform-api",
        "webhooks",

        # Specialized Features
        "social-listening-setup-and-configuration",
        "predictive-engagement",
        "predictive-routing",
        "journey-orchestration",
        "ai-features",

        # Advanced Topics
        "genesys-cloud-cx",
        "customer-experience",
        "omnichannel-experience",
        "conversation-analytics",
        "speech-analytics",
        "quality-management",

        # Industry Specific
        "healthcare-solutions",
        "financial-services",
        "retail-solutions",
        "government-solutions",

        # Technical Implementation
        "deployment-planning",
        "migration-strategies",
        "troubleshooting",
        "best-practices",
        "optimization",

        # Certification Prep
        "certification-preparation",
        "exam-preparation",
        "professional-certification",

        # New Features (2024/2025)
        "ai-powered-features",
        "machine-learning",
        "automation",
        "intelligent-routing"
    ]

    print(f"Testing {len(course_topics)} potential course topics...")

    courses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for i, topic in enumerate(course_topics, 1):
        url = base_url + topic

        try:
            # Use HEAD request to check if course exists
            response = requests.head(url, headers=headers, timeout=10)

            print(f"{i}/{len(course_topics)}: {topic}", end=" ")

            if response.status_code == 200:
                print("FOUND")

                # Create course entry with available information
                course = {
                    "title": topic.replace("-", " ").title(),
                    "url": url,
                    "slug": topic,
                    "status": "accessible",
                    "discovered_date": datetime.now().isoformat(),
                    "category": categorize_course(topic),
                    "description": generate_description(topic),
                    "estimated_duration": estimate_duration(topic),
                    "difficulty_level": estimate_difficulty(topic)
                }

                courses.append(course)

            elif response.status_code == 404:
                print("Not Found")
            else:
                print(f"Status: {response.status_code}")

        except requests.RequestException as e:
            print(f"Error: {str(e)[:50]}")

        time.sleep(0.5)  # Be respectful to the server

    return courses

def categorize_course(topic):
    """Categorize course based on topic name"""

    if any(word in topic for word in ['basic', 'introduction', 'fundamental', 'getting-started']):
        return "Fundamentals"
    elif any(word in topic for word in ['admin', 'management', 'security', 'permission']):
        return "Administration"
    elif any(word in topic for word in ['agent', 'contact-center', 'desktop']):
        return "Contact Center"
    elif any(word in topic for word in ['voice', 'telephony', 'sip']):
        return "Voice & Telephony"
    elif any(word in topic for word in ['digital', 'messaging', 'chat', 'social']):
        return "Digital Channels"
    elif any(word in topic for word in ['routing', 'architect', 'flow']):
        return "Call Flows & Routing"
    elif any(word in topic for word in ['analytics', 'reporting', 'dashboard']):
        return "Analytics & Reporting"
    elif any(word in topic for word in ['workforce', 'wfm', 'forecasting', 'scheduling']):
        return "Workforce Management"
    elif any(word in topic for word in ['api', 'integration', 'sdk', 'webhook']):
        return "API & Integration"
    elif any(word in topic for word in ['ai', 'predictive', 'machine-learning', 'automation']):
        return "AI & Automation"
    elif any(word in topic for word in ['certification', 'exam', 'professional']):
        return "Certification"
    else:
        return "Specialized"

def generate_description(topic):
    """Generate likely description based on topic"""

    descriptions = {
        "basics": "Learn the fundamental concepts and features",
        "introduction": "Get started with core functionality",
        "fundamentals": "Master the essential skills and knowledge",
        "admin": "Configure and manage system settings",
        "agent": "Training for contact center agents",
        "voice": "Voice communication and telephony features",
        "digital": "Digital communication channels",
        "routing": "Call routing and flow management",
        "analytics": "Reporting and performance analysis",
        "api": "Developer integration and API usage",
        "workforce": "Workforce optimization and management"
    }

    for key, desc in descriptions.items():
        if key in topic:
            return f"{desc} for {topic.replace('-', ' ').title()}"

    return f"Training course covering {topic.replace('-', ' ')}"

def estimate_duration(topic):
    """Estimate course duration based on complexity"""

    if any(word in topic for word in ['basic', 'introduction', 'fundamental']):
        return "30-45 minutes"
    elif any(word in topic for word in ['api', 'integration', 'architect']):
        return "60-90 minutes"
    elif any(word in topic for word in ['certification', 'advanced']):
        return "2-3 hours"
    else:
        return "45-60 minutes"

def estimate_difficulty(topic):
    """Estimate difficulty level"""

    if any(word in topic for word in ['basic', 'introduction', 'fundamental', 'getting-started']):
        return "Beginner"
    elif any(word in topic for word in ['api', 'integration', 'advanced', 'architect']):
        return "Advanced"
    elif any(word in topic for word in ['certification', 'professional']):
        return "Expert"
    else:
        return "Intermediate"

def save_courses(courses):
    """Save courses to JSON and CSV files"""

    # Save to JSON
    output_data = {
        "extraction_date": datetime.now().isoformat(),
        "total_courses": len(courses),
        "extraction_method": "URL pattern discovery + content inference",
        "base_url": "https://beyond.genesys.com/explore/course/",
        "courses": courses
    }

    with open('genesys_courses_final.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Save to CSV
    if courses:
        with open('genesys_courses_final.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=courses[0].keys())
            writer.writeheader()
            writer.writerows(courses)

    print(f"\n=== Results Saved ===")
    print(f"Total courses found: {len(courses)}")
    print(f"JSON file: genesys_courses_final.json")
    print(f"CSV file: genesys_courses_final.csv")

    # Show categories breakdown
    categories = {}
    for course in courses:
        cat = course['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nCourses by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    print("=== Final Genesys Course Extraction ===")
    print("This will test comprehensive course topics and create a final dataset\n")

    courses = get_comprehensive_course_list()

    if courses:
        save_courses(courses)

        print(f"\nSample courses found:")
        for course in courses[:10]:
            print(f"- {course['title']} ({course['category']})")
            print(f"  {course['url']}")
            print(f"  Duration: {course['estimated_duration']}, Level: {course['difficulty_level']}")
            print()
    else:
        print("No courses found. The URL pattern may have changed.")