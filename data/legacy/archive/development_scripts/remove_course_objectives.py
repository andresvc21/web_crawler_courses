"""
Quick script to remove course_objectives field from processed data
"""

import csv
import json
from datetime import datetime


def remove_objectives_from_csv():
    """Remove course_objectives from CSV file"""

    print("Removing course_objectives from CSV...")

    # Read processed CSV
    courses = []
    with open('final_processed_courses.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        courses = list(reader)

    # Write new CSV without course_objectives
    with open('final_processed_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'title', 'url', 'description', 'learning_type', 'duration',
            'course_outline', 'page_length'
        ])

        for course in courses:
            writer.writerow([
                course['title'],
                course['url'],
                course['description'],
                course['learning_type'],
                course['duration'],
                course['course_outline'],
                course['page_length']
            ])

    print(f"Updated CSV: {len(courses)} courses processed")


def remove_objectives_from_json():
    """Remove course_objectives from JSON file"""

    print("Removing course_objectives from JSON...")

    # Read processed JSON
    with open('final_processed_courses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Remove course_objectives from each course
    for course in data.get('courses', []):
        if 'course_objectives' in course:
            del course['course_objectives']

    # Update processing info
    data['last_updated'] = datetime.now().isoformat()
    data['fields_removed'] = ['target_audience', 'level', 'prerequisites', 'course_objectives']

    # Write updated JSON
    with open('final_processed_courses.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated JSON: {data.get('total_courses', 0)} courses processed")


def main():
    """Main function"""

    print("=== Removing course_objectives field ===")

    remove_objectives_from_csv()
    remove_objectives_from_json()

    print("\nDone! course_objectives field removed from both files.")
    print("Final schema: title, url, description, learning_type, duration, course_outline, page_length")


if __name__ == "__main__":
    main()