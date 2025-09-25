"""
Post-Processing Script for Enhanced Course Data
- Extract learning type and duration from course outline
- Remove unwanted fields: target_audience, level, prerequisites
- Clean up course outline to only include actual course modules
"""

import csv
import json
import re
from datetime import datetime


def extract_learning_info_from_outline(course_outline):
    """Extract learning type and duration from course outline"""

    if not course_outline:
        return "", "", course_outline

    # Split the outline into parts
    outline_parts = [part.strip() for part in course_outline.split(';')]

    learning_type = ""
    duration = ""
    cleaned_outline_parts = []

    for part in outline_parts:
        # Check if this part contains learning type and duration pattern
        # Pattern: "eLearning 30 mins" or "eLearning 1 hour" etc.
        learning_match = re.match(r'(eLearning|Webinar|Workshop|Course)\s+(\d+(?:\.\d+)?)\s*(mins?|minutes?|hours?|hrs?)', part, re.IGNORECASE)

        if learning_match and not learning_type:  # Only capture first match
            learning_type = learning_match.group(1).title()  # eLearning -> ELearning
            duration_value = learning_match.group(2)
            duration_unit = learning_match.group(3).lower()

            # Standardize duration format
            if duration_unit in ['min', 'mins', 'minute', 'minutes']:
                duration = f"{duration_value} mins"
            elif duration_unit in ['hour', 'hours', 'hr', 'hrs']:
                duration = f"{duration_value} hours"
            else:
                duration = f"{duration_value} {duration_unit}"

            print(f"  Extracted: {learning_type}, {duration}")
            continue  # Skip adding this part to cleaned outline

        # Skip common non-content parts
        skip_patterns = [
            r'^Course Outline$',
            r'^The following sections are covered',
            r'^Course Prerequisites$',
            r'^Course Objectives$',
            r'^At the end of this course',
            r'^This course',
            r'^eLearning \d+',
            r'^\s*$'  # Empty parts
        ]

        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, part, re.IGNORECASE):
                should_skip = True
                break

        if not should_skip and len(part) > 3:  # Keep meaningful content
            cleaned_outline_parts.append(part)

    # Join cleaned outline parts
    cleaned_outline = '; '.join(cleaned_outline_parts) if cleaned_outline_parts else ""

    return learning_type, duration, cleaned_outline


def post_process_csv():
    """Post-process the enhanced CSV file"""

    print("=== Post-Processing Enhanced Course Data ===")
    print("Reading final_enhanced_courses_with_content.csv...")

    # Read the enhanced data
    courses = []
    try:
        with open('final_enhanced_courses_with_content.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            courses = list(reader)
    except Exception as e:
        print(f"Error reading enhanced data: {e}")
        return

    print(f"Loaded {len(courses)} courses for post-processing...")

    # Post-process each course
    processed_courses = []
    stats = {
        'learning_type_extracted': 0,
        'duration_extracted': 0,
        'outline_cleaned': 0
    }

    for i, course in enumerate(courses, 1):
        print(f"[{i}/{len(courses)}] Processing: {course['title'][:50]}...")

        # Extract learning info from course outline
        learning_type, extracted_duration, cleaned_outline = extract_learning_info_from_outline(
            course.get('course_outline', '')
        )

        # Update statistics
        if learning_type:
            stats['learning_type_extracted'] += 1
        if extracted_duration:
            stats['duration_extracted'] += 1
        if cleaned_outline != course.get('course_outline', ''):
            stats['outline_cleaned'] += 1

        # Create cleaned course data
        processed_course = {
            'title': course['title'],
            'url': course['url'],
            'description': course['description'],
            'learning_type': learning_type,
            'duration': extracted_duration or course.get('duration', ''),  # Use extracted or fallback
            'course_objectives': course['course_objectives'],
            'course_outline': cleaned_outline,
            'page_length': course['page_length']
        }

        processed_courses.append(processed_course)

    # Save processed data
    output_csv = 'final_processed_courses.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'title', 'url', 'description', 'learning_type', 'duration',
            'course_objectives', 'course_outline', 'page_length'
        ])

        for course in processed_courses:
            writer.writerow([
                course['title'],
                course['url'],
                course['description'],
                course['learning_type'],
                course['duration'],
                course['course_objectives'],
                course['course_outline'],
                course['page_length']
            ])

    print(f"\\n=== Post-Processing Complete ===")
    print(f"Processed courses: {len(processed_courses)}")
    print(f"Learning types extracted: {stats['learning_type_extracted']}")
    print(f"Durations extracted: {stats['duration_extracted']}")
    print(f"Outlines cleaned: {stats['outline_cleaned']}")
    print(f"\\nOutput file: {output_csv}")

    return processed_courses


def post_process_json():
    """Post-process the enhanced JSON file"""

    print("\\n=== Post-Processing JSON Data ===")
    print("Reading final_enhanced_course_extraction.json...")

    try:
        with open('final_enhanced_course_extraction.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading enhanced JSON: {e}")
        return

    courses = data.get('courses', [])
    print(f"Loaded {len(courses)} courses from JSON...")

    # Process each course in JSON
    processed_courses = []
    stats = {
        'learning_type_extracted': 0,
        'duration_extracted': 0,
        'outline_cleaned': 0
    }

    for i, course in enumerate(courses, 1):
        print(f"[{i}/{len(courses)}] Processing JSON: {course.get('title', 'Unknown')[:50]}...")

        # Extract learning info from course outline
        outline_text = '; '.join(course.get('course_outline', []))
        learning_type, extracted_duration, cleaned_outline = extract_learning_info_from_outline(outline_text)

        # Update statistics
        if learning_type:
            stats['learning_type_extracted'] += 1
        if extracted_duration:
            stats['duration_extracted'] += 1
        if cleaned_outline != outline_text:
            stats['outline_cleaned'] += 1

        # Create cleaned course data
        processed_course = {
            'title': course.get('title', ''),
            'url': course.get('url', ''),
            'description': course.get('description', ''),
            'learning_type': learning_type,
            'duration': extracted_duration or course.get('duration', ''),
            'course_objectives': course.get('course_objectives', []),
            'course_outline': cleaned_outline.split('; ') if cleaned_outline else [],
            'page_length': course.get('page_length', 0),
            'extraction_timestamp': course.get('extraction_timestamp', '')
        }

        processed_courses.append(processed_course)

    # Create processed JSON structure
    processed_data = {
        'processing_date': datetime.now().isoformat(),
        'original_extraction_date': data.get('extraction_date', ''),
        'total_courses': len(processed_courses),
        'successful_extractions': data.get('successful_extractions', 0),
        'success_rate': data.get('success_rate', '0%'),
        'processing_stats': stats,
        'courses': processed_courses
    }

    # Save processed JSON
    output_json = 'final_processed_courses.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    print(f"\\nJSON processing complete!")
    print(f"Output file: {output_json}")

    return processed_courses


def main():
    """Main post-processing function"""

    print("=== Enhanced Course Data Post-Processing ===")
    print("Tasks:")
    print("1. Extract learning type and duration from course outline")
    print("2. Remove unwanted fields: target_audience, level, prerequisites")
    print("3. Clean up course outline content")
    print("=" * 60)

    # Process CSV
    csv_courses = post_process_csv()

    # Process JSON
    json_courses = post_process_json()

    if csv_courses and json_courses:
        print(f"\\n🎉 Post-processing completed successfully!")
        print(f"✅ Created: final_processed_courses.csv")
        print(f"✅ Created: final_processed_courses.json")
        print(f"✅ Removed fields: target_audience, level, prerequisites")
        print(f"✅ Extracted learning types and durations from course outlines")
        print(f"✅ Cleaned course outline content")

        # Show sample of extracted data
        print(f"\\n📊 Sample of processed data:")
        for i, course in enumerate(csv_courses[:3], 1):
            print(f"{i}. {course['title'][:40]}...")
            print(f"   Type: {course['learning_type']}")
            print(f"   Duration: {course['duration']}")
            print(f"   Outline: {course['course_outline'][:80]}...")
            print()
    else:
        print("❌ Post-processing failed")


if __name__ == "__main__":
    main()