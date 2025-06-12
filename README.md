# HKUST Job Board Scraper

A Python script to scrape job listings from the HKUST career website and export them to Excel.

## Features

- Scrapes all job pages automatically
- Extracts specific job details including:
  - Company name and job title
  - Application deadline
  - Job description
  - Other requirements
  - Level of qualification
  - Year of study
  - Application email
  - Application website
  - Salary information
- Exports data to Excel with timestamp

## Setup

1. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Update the configuration in `fetch.py`:
   - Replace `<PASTE_THE_ENDPOINT_HERE>` with your desired job search parameters
   - Replace `<CHANGE_TO_YOUR_OWN_COOKIES>` with valid session cookies

## Usage

Run the script:

```bash
python fetch.py
```

The script will:

1. Process all job pages automatically
2. Extract job details for non-expired positions
3. Save results to an Excel file named `hkust_jobs_YYYYMMDD_HHMMSS.xlsx`

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- pandas
- openpyxl

## Notes

- Make sure to update cookies periodically as they expire
- The script respects application deadlines and only processes current jobs
- Generated Excel files are automatically excluded from git (see .gitignore)
