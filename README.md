# HKUST Job Board Crawler

A Python script to crawl job listings from the HKUST career website and export them to Excel.

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
   - Replace `<PASTE_THE_ENDPOINT_HERE>` with your desired job search parameters, the best way to do so is go to https://career.hkust.edu.hk/web/job.php manually, setup your desired parameter, like internship, job roles, etc, click search and go to page two. Your url should look something like 'https://career.hkust.edu.hk/web/job.php?page=3&EMT%5B0%5D=4&EMT%5B1%5D=11&JN%5B0%5D=13'. Copy the strings after page=?& and replace it, e.g. 'EMT%5B0%5D=4&EMT%5B1%5D=11&JN%5B0%5D=13' in the above example.
   - Replace `<CHANGE_TO_YOUR_OWN_COOKIES>` with valid session cookies, the best way to do so is go to https://career.hkust.edu.hk/web/job.php manually. Then press F12 -> Application -> Cookie, find the thing start with 'PHPSESSION = xxx' copy the whole thing to replace. example: 'PHPSESSID=712y873717129371289371287389123789123812981'

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
