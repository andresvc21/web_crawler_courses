# Genesys Learning Content Extractor

Universal extraction system for Genesys learning content including e-learning courses, webinars, and self-study materials. Features configurable extraction settings and support for multiple content types with comprehensive target audience identification.

## 🎯 Project Overview

This project provides a comprehensive, configurable solution for extracting learning content from the Genesys Beyond platform. The system uses advanced browser automation and pattern recognition to extract structured data from multiple content types with separate, optimized configurations for each type.

## ✨ New Features (v2.0)

- **🔧 Configuration-Driven**: JSON-based configuration for easy customization
- **📚 Multi-Content Support**: E-learning, webinars, and self-study materials
- **🎯 Type-Specific Outputs**: Separate datasets for each content type
- **🔄 Combined Datasets**: Optional unified dataset across all content types
- **⚙️ Flexible Settings**: Customizable extraction parameters per content type

## 📊 Current Results

### E-Learning Courses (Completed)
- **Total Courses Processed**: 142/142 (100%)
- **Courses with Target Audience**: 122/142 (85.9%)
- **Courses with Descriptions**: 129/142 (90.8%)
- **Courses with Durations**: 129/142 (90.8%)
- **Courses with Outlines**: 126/142 (88.7%)

### Future Content Types
- **Webinars**: Ready for extraction (awaiting content list)
- **Self-Study**: Ready for extraction (awaiting content list)

## 📁 Configuration System

### Main Configuration File: `config.json`

```json
{
  "course_types": {
    "e-learning": {
      "name": "E-Learning Courses",
      "input_file": "elearning_courses_list.txt",
      "url_base": "https://beyond.genesys.com/explore/course/",
      "extraction_settings": {
        "wait_time": 12,
        "extract_target_audience": true,
        "extract_duration": true,
        "extract_course_outline": true
      },
      "output_files": {
        "csv": "genesys_elearning_complete_dataset.csv",
        "json": "genesys_elearning_complete_dataset.json"
      }
    }
  }
}
```

### Content Type Input Files

| Content Type | Input File | Status |
|--------------|------------|--------|
| **E-Learning** | `elearning_courses_list.txt` | ✅ Complete (142 courses) |
| **Webinars** | `webinars_list.txt` | 🔄 Template ready |
| **Self-Study** | `self_study_list.txt` | 🔄 Template ready |

## 🗂️ Universal Data Schema

All content types use a consistent schema with type-specific adaptations:

| Field | Description | E-Learning | Webinars | Self-Study |
|-------|-------------|------------|----------|------------|
| `title` | Content title | ✅ | ✅ | ✅ |
| `url` | Content URL | ✅ | ✅ | ✅ |
| `content_type` | Type identifier | "e-learning" | "webinars" | "self-study" |
| `description` | Content description | ✅ | ✅ | ✅ |
| `learning_type` | Learning format | "E-Learning Courses" | "Webinars" | "Self-Study Materials" |
| `duration` | Content duration | ✅ | ✅ | ⚠️ Optional |
| `course_outline` | Content structure | ✅ | ⚠️ Optional | ✅ |
| `target_audience` | Intended audience | ✅ | ✅ | ✅ |

## 🚀 Getting Started

### 1. Universal Extractor

```bash
# Extract all configured content types
python universal_genesys_extractor.py

# Extract specific content type
python universal_genesys_extractor.py --types e-learning

# Extract multiple types
python universal_genesys_extractor.py --types e-learning,webinars
```

### 2. Add New Content Lists

To add webinars or self-study materials:

1. **Add titles to the appropriate file:**
   ```
   # For webinars
   echo "Your Webinar Title" >> webinars_list.txt

   # For self-study
   echo "Your Self-Study Title" >> self_study_list.txt
   ```

2. **Run extraction:**
   ```bash
   python universal_genesys_extractor.py --types webinars
   ```

### 3. Customize Configuration

Edit `config.json` to modify:
- Extraction wait times
- CSS selectors for different content layouts
- Output file names and locations
- Browser settings

## 📁 Current Output Files

### E-Learning (Completed)
- **`genesys_elearning_complete_dataset.csv`** - E-learning courses in CSV format
- **`genesys_elearning_complete_dataset.json`** - E-learning courses in JSON format

### Future Outputs (When Content Added)
- **`genesys_webinars_complete_dataset.csv`** - Webinars dataset
- **`genesys_webinars_complete_dataset.json`** - Webinars JSON
- **`genesys_self_study_complete_dataset.csv`** - Self-study dataset
- **`genesys_self_study_complete_dataset.json`** - Self-study JSON

### Combined Dataset (Optional)
- **`genesys_all_learning_content_dataset.csv`** - All content types combined
- **`genesys_all_learning_content_dataset.json`** - Unified JSON dataset

## 🎯 Target Audience Distribution

The system identifies 10 distinct target audience types across all content:

| Audience | E-Learning Courses | Future: Webinars | Future: Self-Study |
|----------|-------------------|------------------|-------------------|
| **Administrators** | 59 courses | TBD | TBD |
| **System Administrators** | 44 courses | TBD | TBD |
| **Supervisors** | 33 courses | TBD | TBD |
| **Business Users** | 32 courses | TBD | TBD |
| **Agents** | 31 courses | TBD | TBD |
| **Developers** | 30 courses | TBD | TBD |
| **Managers** | 23 courses | TBD | TBD |
| **Analysts** | 8 courses | TBD | TBD |
| **IT Professionals** | 3 courses | TBD | TBD |
| **Contact Center Managers** | 1 course | TBD | TBD |

## 🔧 Technical Implementation

### Key Features

1. **Configuration-Driven Architecture** - Easy modification without code changes
2. **Content-Type Specific Extraction** - Optimized settings per content type
3. **Advanced Pattern Recognition** - Header-based target audience extraction
4. **Robust Error Handling** - Graceful handling of missing or problematic content
5. **Progress Tracking** - Intermediate saves and detailed logging
6. **Flexible Output** - Both individual and combined datasets

### Architecture

```
Configuration (config.json)
    ↓
Content Type Detection
    ↓
Type-Specific Settings
    ↓
Browser Automation (Selenium Chrome)
    ↓
Content Extraction & Pattern Recognition
    ↓
Type-Specific Output Files
    ↓
Optional Combined Dataset
```

## 📖 Usage Examples

### Load E-Learning Data
```python
import pandas as pd
import json

# Load e-learning dataset
elearning_df = pd.read_csv('genesys_elearning_complete_dataset.csv')
print(f"E-learning courses: {len(elearning_df)}")

# Filter by target audience
dev_courses = elearning_df[elearning_df['target_audience'].str.contains('Developers', na=False)]
print(f"Courses for developers: {len(dev_courses)}")
```

### Load Combined Dataset (Future)
```python
# Load all content types
all_content_df = pd.read_csv('genesys_all_learning_content_dataset.csv')

# Group by content type
by_type = all_content_df.groupby('content_type').size()
print(by_type)
```

## 📂 Project Structure

```
genesys_courses/
├── README.md                                    # This file
├── config.json                                 # Main configuration
├── universal_genesys_extractor.py              # Universal extraction script
│
├── Input Files:
│   ├── elearning_courses_list.txt              # ✅ E-learning titles (142)
│   ├── webinars_list.txt                       # 🔄 Webinars template
│   └── self_study_list.txt                     # 🔄 Self-study template
│
├── E-Learning Outputs (Current):
│   ├── genesys_elearning_complete_dataset.csv  # E-learning CSV
│   ├── genesys_elearning_complete_dataset.json # E-learning JSON
│   ├── all_142_courses.csv                     # E-learning URLs
│   └── complete_genesys_courses_dataset.*      # Legacy files
│
├── Legacy Scripts (v1.0):
│   ├── full_enhanced_extractor.py              # Original e-learning extractor
│   ├── full_target_audience_extractor.py       # Target audience extraction
│   ├── merge_complete_dataset.py               # Dataset merger
│   └── fast_url_generator.py                   # URL generation
│
└── System Files:
    ├── chromedriver.exe                        # Chrome WebDriver
    ├── CLAUDE.md                              # Development notes
    └── requirements.txt                        # Python dependencies
```

## 🎉 Migration from v1.0

### What Changed
- **Single-purpose scripts** → **Universal configurable system**
- **Hardcoded settings** → **JSON configuration**
- **E-learning only** → **Multi-content type support**
- **Single output** → **Type-specific outputs + combined**

### Backward Compatibility
- All original e-learning data preserved
- Legacy scripts maintained for reference
- Same data quality and extraction accuracy

## 🚀 Next Steps

1. **Add Webinars List** - Provide webinar titles in `webinars_list.txt`
2. **Add Self-Study List** - Provide self-study titles in `self_study_list.txt`
3. **Run Extraction** - Execute universal extractor for new content types
4. **Analyze Combined Data** - Use unified dataset for comprehensive analysis

## 🛠️ Requirements

- Python 3.8+
- Chrome Browser
- ChromeDriver (included)
- Dependencies: `selenium`, `beautifulsoup4`, `pandas` (optional)

## 📄 License

This project is for educational and research purposes. Please respect Genesys's terms of service when using their platform.

---

**Project Version**: 2.0.0 - Universal Content Extractor
**Last Updated**: September 2025
**Current Status**: E-learning complete, ready for webinars and self-study expansion