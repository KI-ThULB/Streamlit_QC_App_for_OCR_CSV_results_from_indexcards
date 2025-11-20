# OCR Quality Control & Correction App (streamlit)

A Streamlit-based web application for reviewing, correcting, and validating metadata extracted from digitized index cards using AI-assisted OCR and Vision Language Models.

## Overview

This application provides an interactive interface for quality assurance of AI-extracted metadata from large-scale digitization projects. It allows teams to review OCR results, correct extraction errors, and monitor data quality across multiple batches of digitized historical materials (index cards, music archives, etc.).

**Key Use Cases:**
- Batch-by-batch review of extracted metadata
- Manual correction of OCR extraction errors
- Real-time quality metrics and statistics
- Search and filter capabilities for targeted quality control
- Export of corrected data and problem reports

## Features

### 📦 Batch View
- Navigate through individual batches of digitized cards
- Review extracted metadata with corresponding image thumbnails
- Edit specific fields directly in the application
- Filter cards by data completeness
- Save corrections back to CSV files
- Navigation between cards with previous/next controls

### 📊 Overview & Statistics
- View aggregate quality metrics across all batches
- Field-level completion rates and percentages
- Data completeness distribution (complete, medium, sparse)
- Batch comparison tables
- Identify problematic cards with insufficient metadata
- Export complete datasets and problem reports

### 🔍 Search
- Full-text search across configurable metadata fields
- Filter results by search terms
- Quick access to specific cards for targeted corrections
- Export search results as CSV

### 💾 Data Management
- Persistent CSV-based storage
- Automatic caching for improved performance
- Download export functionality for processed data
- Support for batch and master metadata files

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quality-control-app
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure paths (IMPORTANT)**
   
   Edit `template_quality_control_app.py` and update the following configuration variables at the top of the file:

   ```python
   # Path Configuration
   CSV_DIR = "/path/to/output_batches/csv"
   JSON_DIR = "/path/to/output_batches/json"
   MASTER_CSV = "/path/to/results/metadata_vlm_complete_UPDATED.csv"
   IMAGE_BASE_DIR = "/path/to/jpeg_output"
   LOGO_PATH = "/path/to/your_logo.png"
   ```

5. **Configure editable fields**
   
   Customize the `EDITABLE_FIELDS` list to match your project's metadata schema:
   ```python
   EDITABLE_FIELDS = [
       "Komponist", "Signatur", "Titel", "Textanfang",
       "Verlag", "Material", "Textdichter", "Bearbeiter", "Bemerkungen"
   ]
   ```

6. **Customize project information**
   
   Update the following placeholders in the sidebar section:
   - Project name (replace "Projektname")
   - Team name and institution
   - Custom footer information

## Usage

### Running the Application

```bash
streamlit run template_quality_control_app.py
```

The application will start on `http://localhost:8501` by default.

### Workflow

#### 1. Batch Review Mode
- Select a batch from the sidebar dropdown
- View statistics for the selected batch (total cards, field completion rates)
- Click on a card to open the detail view
- Edit metadata in the input fields
- Optionally upload a corrected image
- Click "Save Changes" to persist corrections to CSV
- Navigate between cards using Previous/Next buttons

#### 2. Overview & Statistics Mode
- View aggregated metrics across all batches
- Monitor field-level completion percentages
- Identify data quality distribution
- Compare statistics between different batches
- Download complete corrected datasets
- Export identified problematic cards (≤2 fields filled)

#### 3. Search Mode
- Enter search terms to find specific cards by metadata content
- Search across Komponist, Titel, Signatur, and Textanfang fields (configurable)
- View matched results in table format
- Export search results as CSV file

### Data Input Format

The application expects CSV files with the following structure:

**Minimum Required Columns:**
- `Datei` - Filename of the card image
- `Batch` - Batch identifier
- Metadata columns (configurable per project)

**Example CSV Structure:**
```
Datei,Batch,Komponist,Signatur,Titel,Textanfang,Verlag,Material,Textdichter,Bearbeiter,Bemerkungen
card_001.jpg,batch_01,Mozart,MS-001,Requiem,Kyrie,Breitkopf,Paper,Mozart,Müller,Excellent scan
card_002.jpg,batch_01,Bach,,BWV 245,,Henle,Paper,,Weber,Signature needed
```

## Configuration Guide

### File Paths

| Variable | Purpose | Example |
|----------|---------|---------|
| `CSV_DIR` | Directory containing batch CSV files | `/data/output_batches/csv` |
| `JSON_DIR` | Directory containing JSON exports (optional) | `/data/output_batches/json` |
| `MASTER_CSV` | Main consolidated metadata file | `/data/results/metadata_vlm_complete.csv` |
| `IMAGE_BASE_DIR` | Root directory for digitized card images | `/data/jpeg_output` |
| `LOGO_PATH` | Project logo for sidebar | `/images/project_logo.png` |

### Editable Fields

Define which metadata fields should be editable in the application:

```python
EDITABLE_FIELDS = [
    "Komponist",      # Composer
    "Signatur",       # Signature/Call number
    "Titel",          # Title
    "Textanfang",     # Text beginning
    "Verlag",         # Publisher
    "Material",       # Material type
    "Textdichter",    # Lyricist
    "Bearbeiter",     # Editor/Arranger
    "Bemerkungen"     # Notes/Comments
]
```

### Quality Metrics

The application calculates completeness based on field count:
- **Complete:** ≥ 6 fields filled
- **Medium:** 3-5 fields filled
- **Sparse:** ≤ 2 fields filled

These thresholds can be adjusted in the `calculate_statistics()` function.

## Data Export

### Available Exports

1. **Batch CSV** - Corrected metadata for a single batch
2. **Complete Dataset** - Full corrected metadata across all batches (Overview mode)
3. **Problematic Cards** - Cards with sparse data (≤2 fields) identified for review (Overview mode)
4. **Search Results** - Results from searches, exported as CSV (Search mode)

### Export Locations

Downloads are stored in your browser's default download folder. Ensure proper file naming conventions for archival purposes.

## Image Handling

The application supports flexible image path resolution:

```
Attempts to find images in the following order:
1. {IMAGE_BASE_DIR}/{batch}/{filename}
2. {IMAGE_BASE_DIR}/{filename}
3. {IMAGE_BASE_DIR}/../{batch}/{filename}
```

**Supported Formats:** JPEG, PNG, TIFF, and other PIL-compatible image formats

## Performance Considerations

### Caching
- CSV files are cached using Streamlit's `@st.cache_data` decorator
- Cache is automatically cleared when data is saved
- For large datasets (>50,000 cards), initial load may take several seconds

### Optimization Tips
- Store images in compressed JPEG format for faster loading
- Consider splitting very large master CSV files into smaller batches
- Run the application on a machine with sufficient RAM for large datasets
- Use SSD storage for faster file I/O

## Customization

### Project-Specific Adjustments

Before deploying, customize the following sections:

1. **Sidebar Information** (lines 155-195)
   ```python
   st.title("Your Project Name")
   st.markdown("### Your Subtitle")
   st.markdown("**YOUR TEAM NAME**")
   st.markdown("YOUR INSTITUTION")
   ```

2. **Page Configuration** (lines 29-34)
   ```python
   st.set_page_config(
       page_title="Your Title",
       page_icon="🎵",  # Change emoji as needed
       layout="wide"
   )
   ```

3. **Footer** (lines 614-616)
   ```python
   <p><strong>Your Project Name</strong></p>
   <p>Your Museum/Institution | Your Team</p>
   ```

4. **Search Fields** (lines 575-579)
   Adjust which columns are searchable based on your metadata schema

5. **Batch Comparison Metrics** (lines 498-507)
   Modify which fields are compared in the Overview mode

## Troubleshooting

### Common Issues

**Problem: "No batches found!"**
- Verify `CSV_DIR` path is correct and contains `.csv` files
- Check file permissions (app needs read access)

**Problem: Images not displaying**
- Verify `IMAGE_BASE_DIR` path is correct
- Confirm image filenames match the `Datei` column in CSV
- Check that image format is supported (JPEG, PNG, TIFF)

**Problem: "Master-CSV not found"**
- Verify `MASTER_CSV` path is correct
- Ensure file has `.csv` extension
- Check file exists and is readable

**Problem: Slow performance with large datasets**
- Clear cache: Restart the Streamlit application
- Reduce number of rows in master CSV
- Consider splitting into smaller batch files
- Check available system RAM

**Problem: CSV encoding errors**
- Ensure CSV files are UTF-8 encoded with BOM
- Files should use "utf-8-sig" encoding (standard for Excel CSVs)

## Requirements

See `requirements.txt` for complete dependency list:

```
streamlit>=1.28.0
pandas>=2.0.0
Pillow>=10.0.0
```

## Technical Details

### Architecture

The application uses a three-mode interface pattern:

```
┌─────────────────────────────┐
│    Sidebar Navigation       │
│  [Mode Selection + Config]  │
└─────────────────────────────┘
          │
    ┌─────┴─────┬─────────────┬──────────┐
    ▼           ▼             ▼          ▼
[Batch Mode] [Overview] [Search] [Detail View]
```

### Data Flow

```
CSV Files → Load/Cache → Display → Edit → Save → CSV
   ↓                                        ↓
[Master CSV]                          [Updated CSV]
   ↓
[Statistics Calculation]
   ↓
[Visualization & Export]
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `load_csv_data()` | Loads and caches CSV files |
| `load_image()` | Resolves and loads card images |
| `save_corrections()` | Persists edited metadata to CSV |
| `calculate_statistics()` | Computes quality metrics |
| `get_batch_list()` | Retrieves available batches |

## Project Structure

```
project-root/
├── template_quality_control_app.py  # Main application
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── data/                            # (Not included, configure paths)
    ├── output_batches/csv/          # Batch CSV files
    ├── results/                     # Master CSV location
    └── jpeg_output/                 # Digitized card images
```

## Best Practices

### Data Management
- Always maintain backup copies of original CSV files
- Use version control for tracking metadata corrections
- Document any systematic corrections or bulk changes
- Periodically export corrected data for archival

### Quality Control Workflow
1. Review batches in order (Batch View)
2. Identify problematic cards (Overview mode)
3. Use Search mode for targeted corrections
4. Export corrected datasets regularly
5. Maintain correction logs for audit trails

### Team Collaboration
- Establish naming conventions for batch identifiers
- Define clear field completion standards
- Document project-specific customizations
- Assign batch reviews to team members
- Track correction progress in Overview mode

## Contributors

ThULB KI-Team, Thuringian University and State Library (ThULB), Jena, Germany

## Support & Documentation

For issues, questions, or contributions, please refer to the project's issue tracker or contact the development team.

### AI Code Audits & Updates

Given the AI-generated nature of this code, we recommend:

Regular code audits and security reviews
Testing after any dependencies are updated
Documenting any modifications made to the original code
Keeping detailed logs of reported issues and fixes
Periodic review of best practices for AI-assisted code quality
Consideration of having external security professionals review critical components

If you identify issues, vulnerabilities, or improvements related to AI-generated code quality, please report them to the development team with detailed information about:

The specific code section and line numbers
Steps to reproduce any issues
Expected vs. actual behavior
Environment details (Python version, OS, etc.)

### Contact
Mail: ki_thulb[at]uni-jena.de

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Status:** Production-Ready (beta)
