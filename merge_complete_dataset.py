"""
Merge Complete Dataset - Target Audience + Full Course Information
Combines the target audience data with the complete course dataset
"""

import json
import csv
from datetime import datetime

print("=== Merging Complete Genesys Course Dataset ===")

# Load the complete course dataset (descriptions, learning types, durations, etc.)
print("Loading complete course dataset...")
complete_courses = []
try:
    with open('final_processed_courses.json', 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
        complete_courses = complete_data.get('courses', [])
        print(f"  Loaded {len(complete_courses)} courses with full information")
except Exception as e:
    print(f"Error loading complete courses: {e}")
    exit(1)

# Load the target audience dataset
print("Loading target audience dataset...")
target_audience_courses = []
try:
    with open('final_target_audience_extraction_corrected.json', 'r', encoding='utf-8') as f:
        target_data = json.load(f)
        target_audience_courses = target_data.get('courses', [])
        print(f"  Loaded {len(target_audience_courses)} courses with target audience")
except Exception as e:
    print(f"Error loading target audience: {e}")
    exit(1)

# Create mapping of target audiences by URL for easy lookup
print("Creating target audience mapping...")
target_audience_map = {}
for course in target_audience_courses:
    url = course.get('url', '')
    if url and course.get('target_audience'):
        target_audience_map[url] = course['target_audience']

print(f"  Created mapping for {len(target_audience_map)} courses with target audiences")

# Merge the datasets
print("Merging datasets...")
merged_courses = []
courses_with_target_audience = 0
courses_without_target_audience = 0

for course in complete_courses:
    # Start with the complete course information
    merged_course = {
        'title': course.get('title', ''),
        'url': course.get('url', ''),
        'description': course.get('description', ''),
        'learning_type': course.get('learning_type', ''),
        'duration': course.get('duration', ''),
        'course_outline': course.get('course_outline', ''),
        'target_audience': [],  # Will be populated from target audience data
        'extraction_timestamp': datetime.now().isoformat()
    }

    # Add target audience if available
    url = course.get('url', '')
    if url in target_audience_map:
        merged_course['target_audience'] = target_audience_map[url]
        courses_with_target_audience += 1
    else:
        courses_without_target_audience += 1

    merged_courses.append(merged_course)

print(f"  Merged {len(merged_courses)} courses total")
print(f"  Courses with target audience: {courses_with_target_audience}")
print(f"  Courses without target audience: {courses_without_target_audience}")

# Create final merged dataset
final_merged_data = {
    'dataset_name': 'Complete Genesys Cloud Course Dataset',
    'creation_date': datetime.now().isoformat(),
    'total_courses': len(merged_courses),
    'courses_with_target_audience': courses_with_target_audience,
    'courses_with_descriptions': len([c for c in merged_courses if c.get('description')]),
    'courses_with_durations': len([c for c in merged_courses if c.get('duration')]),
    'courses_with_outlines': len([c for c in merged_courses if c.get('course_outline')]),
    'success_rate_target_audience': f"{courses_with_target_audience/len(merged_courses)*100:.1f}%",
    'fields': [
        'title', 'url', 'description', 'learning_type',
        'duration', 'course_outline', 'target_audience'
    ],
    'courses': merged_courses
}

# Save merged JSON dataset
print("Saving complete merged dataset...")
with open('complete_genesys_courses_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(final_merged_data, f, indent=2, ensure_ascii=False)

# Save merged CSV dataset
with open('complete_genesys_courses_dataset.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'title', 'url', 'description', 'learning_type',
        'duration', 'course_outline', 'target_audience'
    ])

    for course in merged_courses:
        writer.writerow([
            course.get('title', ''),
            course.get('url', ''),
            course.get('description', ''),
            course.get('learning_type', ''),
            course.get('duration', ''),
            course.get('course_outline', ''),
            '; '.join(course.get('target_audience', []))
        ])

print(f"Files saved:")
print(f"- complete_genesys_courses_dataset.json")
print(f"- complete_genesys_courses_dataset.csv")

# Generate summary statistics
print(f"\n=== Complete Dataset Summary ===")
print(f"Total courses: {len(merged_courses)}")
print(f"Courses with target audience: {courses_with_target_audience} ({courses_with_target_audience/len(merged_courses)*100:.1f}%)")
print(f"Courses with descriptions: {len([c for c in merged_courses if c.get('description')])}")
print(f"Courses with learning types: {len([c for c in merged_courses if c.get('learning_type')])}")
print(f"Courses with durations: {len([c for c in merged_courses if c.get('duration')])}")
print(f"Courses with outlines: {len([c for c in merged_courses if c.get('course_outline')])}")

# Target audience distribution
print(f"\n=== Target Audience Distribution ===")
audience_counts = {}
for course in merged_courses:
    for audience in course.get('target_audience', []):
        audience_counts[audience] = audience_counts.get(audience, 0) + 1

for audience, count in sorted(audience_counts.items()):
    print(f"{audience}: {count} courses")

# Learning type distribution
print(f"\n=== Learning Type Distribution ===")
learning_type_counts = {}
for course in merged_courses:
    learning_type = course.get('learning_type', 'Unknown')
    learning_type_counts[learning_type] = learning_type_counts.get(learning_type, 0) + 1

for learning_type, count in sorted(learning_type_counts.items()):
    print(f"{learning_type}: {count} courses")

print(f"\n🎉 Complete dataset merge successful!")
print(f"Your comprehensive Genesys Cloud course dataset is ready for analysis!")