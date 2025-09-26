# Genesys Cloud Complete Course Dataset

Comprehensive extraction and processing of all 142 Genesys Cloud e-learning courses with complete information including target audiences, descriptions, durations, and course outlines.

## 🎯 Project Overview

This project successfully extracts comprehensive information from all 142 Genesys Cloud e-learning courses available on the Beyond Genesys platform using advanced browser automation and pattern recognition. The solution overcomes JavaScript-heavy single-page application challenges to deliver a complete, structured dataset with target audience information.

## 📊 Final Results

- **Total Courses Processed**: 142/142 (100%)
- **Courses with Target Audience**: 122/142 (85.9%)
- **Courses with Descriptions**: 129/142 (90.8%)
- **Courses with Durations**: 129/142 (90.8%)
- **Courses with Outlines**: 126/142 (88.7%)
- **Data Quality**: High-quality extraction with footer content filtering
- **Processing Time**: ~5 hours total execution time

## 📁 Main Deliverables

### Primary Output Files

- **`complete_genesys_courses_dataset.csv`** - Complete dataset ready for analysis
- **`complete_genesys_courses_dataset.json`** - Structured complete data for programmatic access

### Source Data
- **`courses_titles.txt`** - Original list of 142 course titles
- **`all_142_courses.csv`** - Course titles with generated URLs
- **`CLAUDE.md`** - Development guidance and project notes

### Core Scripts
- **`full_enhanced_extractor.py`** - Main course content extraction script
- **`full_target_audience_extractor.py`** - Target audience extraction script
- **`merge_complete_dataset.py`** - Final dataset merger
- **`fast_url_generator.py`** - URL generation from course titles

## 🗂️ Complete Data Schema

The final complete dataset contains the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Course title | "Genesys Cloud: API - Workforce Management" |
| `url` | Course URL | https://beyond.genesys.com/explore/course/... |
| `description` | Course description (footer-free) | "This course introduces you to Genesys Cloud..." |
| `learning_type` | Type of learning | "Elearning" |
| `duration` | Course duration | "30 mins" |
| `course_outline` | Course modules/sections | "Introduction; API Basics; Advanced Topics" |
| `target_audience` | Who should take the course | "Developers; System Administrators" |

## 🎯 Target Audience Distribution

The dataset includes 10 distinct target audience types:

| Audience | Courses | Description |
|----------|---------|-------------|
| **Administrators** | 59 | General system administrators |
| **System Administrators** | 44 | Technical system administrators |
| **Supervisors** | 33 | Contact center supervisors |
| **Business Users** | 32 | End-users and business stakeholders |
| **Agents** | 31 | Contact center agents |
| **Developers** | 30 | Software developers and integrators |
| **Managers** | 23 | Management and leadership roles |
| **Analysts** | 8 | Business and data analysts |
| **IT Professionals** | 3 | IT specialists |
| **Contact Center Managers** | 1 | Contact center management |

## 🔧 Technical Implementation

### Key Challenges Solved

1. **JavaScript Rendering** - Used Selenium Chrome WebDriver for SPA handling
2. **URL Generation** - Created intelligent slug generation from course titles
3. **Content Quality** - Implemented footer content filtering
4. **Data Extraction** - Advanced CSS selectors for precise content targeting
5. **Target Audience Extraction** - Header pattern recognition for audience identification
6. **Processing Scale** - Optimized for 142 courses with progress tracking

### Architecture

```
Browser Automation (Selenium Chrome)
    ↓
JavaScript-Rendered Content Extraction
    ↓
BeautifulSoup HTML Parsing
    ↓
Advanced CSS Selector Targeting
    ↓
Footer Content Filtering
    ↓
Data Processing & Cleaning
    ↓
Structured Output (CSV/JSON)
```

### Enhanced Features

- **Target Audience Extraction**: Pattern recognition for audience identification
- **Learning Type Extraction**: Automatically extracted from course outlines
- **Duration Parsing**: Smart parsing of time information
- **Content Cleaning**: Removed website footer and metadata
- **Progress Tracking**: Intermediate saves every 20 courses
- **Error Handling**: Robust error handling and recovery

## 🚀 Key Achievements

✅ **100% Course Coverage** - Successfully processed all 142 courses
✅ **Target Audience Identification** - 85.9% success rate with 10 distinct audience types
✅ **Quality Data Extraction** - No footer content contamination
✅ **Smart Content Parsing** - Extracted learning types and durations from course outlines
✅ **Robust Architecture** - Handled JavaScript rendering and complex SPA structure
✅ **Clean Output** - Production-ready CSV and JSON formats
✅ **Complete Dataset** - Descriptions, outlines, durations, and target audiences

## 📈 Data Quality Improvements

### Before vs After
- **Before**: Footer content extracted ("Genesys empowers more than 8,000 organizations...")
- **After**: Real course content ("This course introduces you to Genesys Cloud...")

### Enhancements Made
- Intelligent CSS selector targeting
- Footer content detection and filtering
- Learning type extraction from course outlines
- Duration parsing and standardization
- Course outline cleaning and structuring

## 🛠️ Requirements

### System Requirements
- Python 3.8+
- Chrome Browser
- ChromeDriver (included in project)
- Windows/macOS/Linux

### Python Dependencies
- selenium
- beautifulsoup4
- pandas (optional, for data analysis)
- requests (optional, for additional features)

## 📖 Usage Examples

### Load Data in Python
```python
import pandas as pd
import json

# Load complete dataset
courses_df = pd.read_csv('complete_genesys_courses_dataset.csv')
print(f"Total courses: {len(courses_df)}")

# Load JSON data
with open('complete_genesys_courses_dataset.json', 'r') as f:
    data = json.load(f)
    courses = data['courses']

# Filter by target audience
developers_courses = courses_df[courses_df['target_audience'].str.contains('Developers', na=False)]
print(f"Courses for developers: {len(developers_courses)}")
```

### Excel Analysis
Simply open `complete_genesys_courses_dataset.csv` in Excel for immediate analysis, filtering, and visualization with full target audience information.

## 📂 Project Structure

```
genesys_courses/
├── README.md                                # This file
├── complete_genesys_courses_dataset.csv    # Complete CSV dataset
├── complete_genesys_courses_dataset.json   # Complete JSON dataset
├── courses_titles.txt                      # Original course list
├── all_142_courses.csv                     # Courses with URLs
├── full_enhanced_extractor.py              # Main extraction script
├── full_target_audience_extractor.py       # Target audience extraction
├── merge_complete_dataset.py               # Dataset merger
├── fast_url_generator.py                   # URL generation script
├── chromedriver.exe                        # Chrome WebDriver
├── CLAUDE.md                              # Development notes
└── requirements.txt                        # Python dependencies
```

## 🔍 Sample Data

```csv
title,url,description,learning_type,duration,course_outline,target_audience
"Genesys Cloud: API - Workforce Management","https://beyond.genesys.com/explore/course/genesys-cloud-api-workforce-management","This course introduces you to Genesys Cloud Workforce Management (WFM) features through APIs...","Elearning","30 mins","Introduction to API and Workforce Management; Workforce Management Reports","Developers"
```

## 🎉 Project Success Metrics

- **Completeness**: 142/142 courses processed (100%)
- **Target Audience Coverage**: 122/142 courses with audience data (85.9%)
- **Data Quality**: Footer content eliminated, real course content extracted
- **Efficiency**: ~21 seconds average per course including target audience extraction
- **Reliability**: Robust error handling and recovery
- **Usability**: Clean CSV/JSON formats with complete information ready for analysis

## 📝 Development History

This project evolved through several phases:
1. **Initial Setup** - Project structure and URL discovery
2. **Content Extraction** - Browser automation implementation
3. **Quality Enhancement** - Footer content filtering
4. **Field Enhancement** - Learning type and duration extraction
5. **Target Audience Enhancement** - Pattern recognition for audience identification
6. **Data Integration** - Merging all datasets into complete dataset
7. **Final Cleanup** - Repository organization and documentation

## 📄 License

This project is for educational and research purposes. Please respect Genesys's terms of service when using their platform.

---

**Project Completed**: September 2025
**Total Processing Time**: ~5 hours
**Final Dataset**: 142 courses, 7 fields including target audiences, complete and production-ready