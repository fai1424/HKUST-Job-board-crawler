import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

url = "https://career.hkust.edu.hk/web"
base_endpoint = "/job.php?page={}&<PASTE_THE_ENDPOINT_HERE>"
cookies = "<CHANGE_TO_YOUR_OWN_COOKIES>"




def extract_job_details(soup):
    """Extract specific job details from the job detail page"""
    details = {}

    # Find all tables with job information
    tables = soup.find_all("table", class_="second-detail")
    tables_2 = soup.find_all("table", class_="second-detail2")
    tables_4 = soup.find_all("table", class_="second-detail4")

    all_tables = tables + tables_2 + tables_4

    for table in all_tables:
        rows = table.find_all("tr")
        for row in rows:
            header = row.find("td", class_="detail-header")
            text = row.find("td", class_="detail-text")

            if header and text:
                header_text = header.get_text(strip=True)

                # Extract Job Description
                if "Job Description" in header_text:
                    # Get all list items if present, otherwise get text
                    ul = text.find("ul")
                    if ul:
                        items = [li.get_text(strip=True)
                                 for li in ul.find_all("li")]
                        details["job_description"] = "; ".join(items)
                    else:
                        details["job_description"] = text.get_text(strip=True)

                # Extract Other Requirement
                elif "Other Requirement" in header_text:
                    ul = text.find("ul")
                    if ul:
                        items = [li.get_text(strip=True)
                                 for li in ul.find_all("li")]
                        details["other_requirement"] = "; ".join(items)
                    else:
                        details["other_requirement"] = text.get_text(
                            strip=True)

                # Extract Level of Qualification
                elif "Level of Qualification" in header_text:
                    details["level_of_qualification"] = text.get_text(
                        strip=True)

                # Extract Year of Study
                elif "Year of Study" in header_text:
                    details["year_of_study"] = text.get_text(strip=True)

                # Extract Salary
                elif "Salary" in header_text:
                    details["salary"] = text.get_text(strip=True)

                # Extract Application Method (Email and Website separately)
                elif "Application Method" in header_text:
                    # Look for email in the same row or next rows
                    email_link = row.find(
                        "a", href=lambda x: x and x.startswith("mailto:"))
                    if email_link:
                        details["application_email"] = email_link.get_text(
                            strip=True)

                    # Look for website links (non-mailto links, excluding generic career pages)
                    # Only capture if it's clearly an external application website
                    website_links = row.find_all(
                        "a", href=lambda x: x and not x.startswith("mailto:") and x.startswith("http") and "careers/main.html" not in x and "hkust.edu.hk" not in x)
                    for link in website_links:
                        href = link.get('href', '')
                        # Only capture if it's clearly not a generic page
                        if href and not any(generic in href.lower() for generic in ["welcome", "main.html", "index", "home"]):
                            details["application_website"] = href
                            break

                    # If no links found in current row, check subsequent rows
                    if "application_email" not in details or "application_website" not in details:
                        next_row = row.find_next_sibling("tr")
                        if next_row:
                            # Check for email in next row
                            if "application_email" not in details:
                                email_link = next_row.find(
                                    "a", href=lambda x: x and x.startswith("mailto:"))
                                if email_link:
                                    details["application_email"] = email_link.get_text(
                                        strip=True)

                            # Check for website links in next row
                            if "application_website" not in details:
                                website_links = next_row.find_all(
                                    "a", href=lambda x: x and not x.startswith("mailto:") and x.startswith("http") and "careers/main.html" not in x and "hkust.edu.hk" not in x)
                                for link in website_links:
                                    href = link.get('href', '')
                                    # Only capture if it's clearly not a generic page
                                    if href and not any(generic in href.lower() for generic in ["welcome", "main.html", "index", "home"]):
                                        details["application_website"] = href
                                        break

    # If application methods weren't found in the table structure, search more broadly
    if "application_email" not in details:
        # Search for email links
        email_links = soup.find_all(
            "a", href=lambda x: x and x.startswith("mailto:"))
        if email_links:
            details["application_email"] = email_links[0].get_text(strip=True)

    if "application_website" not in details:
        # Search for application-related website links (look for common application keywords)
        # Exclude generic HKUST career pages
        application_keywords = ["apply", "application", "job", "recruitment"]
        website_links = soup.find_all(
            "a", href=lambda x: x and x.startswith("http") and "careers/main.html" not in x and "hkust.edu.hk" not in x)
        for link in website_links:
            link_text = link.get_text(strip=True).lower()
            link_href = link.get('href', '').lower()
            # Only match if the keyword is in the URL or link text, and it's not a generic page
            if any(keyword in link_text or keyword in link_href for keyword in application_keywords):
                details["application_website"] = link.get('href', '')
                break  # Take the first matching website

    return details


# List to store all job data
all_jobs_data = []
total_jobs_processed = 0

print("Starting to fetch jobs from all pages...")

# Loop through pages
page = 1
while True:
    print(f"\n📄 Processing page {page}...")

    # Construct endpoint for current page
    endpoint = base_endpoint.format(page)

    try:
        response = requests.get(url + endpoint, headers={"Cookie": cookies})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        job_tables = soup.find("table", class_="job-list")
        if not job_tables:
            print(f"❌ No job table found on page {page}. Ending pagination.")
            break

        joblists = job_tables.find_all("tr", class_="job-item")

        if not joblists:
            print(f"❌ No jobs found on page {page}. Ending pagination.")
            break

        print(f"📋 Found {len(joblists)} jobs on page {page}")

        page_jobs_processed = 0

        for i, job in enumerate(joblists):
            try:
                company_url = job.find("a")["href"][1:]
                columns = job.find_all("td", class_="detail-text")
                company_name = columns[0].find(
                    "font", class_="font2").text.strip()
                job_title = columns[1].find(
                    "font", class_="font2").text.strip()
                application_deadline = datetime.strptime(
                    columns[3].text.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")

                if application_deadline >= datetime.today().strftime("%Y-%m-%d"):
                    print(
                        f"🔄 Processing job {i+1} on page {page}: {company_name} - {job_title}")

                    # Create basic job data dictionary
                    job_data = {
                        "company_name": company_name,
                        "job_title": job_title,
                        "application_deadline": application_deadline,
                        "job_description": "",
                        "other_requirement": "",
                        "level_of_qualification": "",
                        "year_of_study": "",
                        "application_email": "",
                        "application_website": "",
                        "salary": ""
                    }

                    # Fetch and parse job details
                    second_response = requests.get(
                        url+company_url, headers={"Cookie": cookies})
                    second_soup = BeautifulSoup(
                        second_response.text, "html.parser")

                    # Extract specific job details
                    job_details = extract_job_details(second_soup)

                    # Update job_data with extracted details
                    job_data.update(job_details)

                    # Add to the list
                    all_jobs_data.append(job_data)
                    page_jobs_processed += 1
                    total_jobs_processed += 1

                    print(f"✓ Processed: {company_name} - {job_title}")
                else:
                    print(
                        f"⏭️  Skipping expired job: {company_name} - {job_title} (deadline: {application_deadline})")

            except Exception as e:
                print(f"❌ Error processing job {i+1} on page {page}: {str(e)}")
                continue

        print(
            f"✅ Page {page} completed. Processed {page_jobs_processed} valid jobs.")

        # Move to next page
        page += 1

    except requests.RequestException as e:
        print(f"❌ Error fetching page {page}: {str(e)}")
        break
    except Exception as e:
        print(f"❌ Unexpected error on page {page}: {str(e)}")
        break

print(f"\n🎯 Pagination completed. Total pages processed: {page - 1}")

# Create DataFrame and save to Excel
if all_jobs_data:
    df = pd.DataFrame(all_jobs_data)

    # Reorder columns for better readability
    column_order = [
        "company_name",
        "job_title",
        "application_deadline",
        "job_description",
        "other_requirement",
        "level_of_qualification",
        "year_of_study",
        "application_email",
        "application_website",
        "salary"
    ]

    df = df[column_order]

    # Generate filename with current date
    filename = f"hkust_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # Save to Excel
    df.to_excel(filename, index=False, engine='openpyxl')

    print(f"\n✅ Successfully saved {len(all_jobs_data)} jobs to {filename}")
    print(f"📊 Total jobs processed: {total_jobs_processed}")
    print(f"📋 Valid jobs exported: {len(all_jobs_data)}")
else:
    print("❌ No valid jobs found to export")


# print(joblists[0].find("a")["href"])
# for job in joblists:
#     columns = job.find_all("td")
#     company_name = columns[0].text.strip()
#     job_title = columns[1].text.strip()
#     application_deadline = columns[3].text.strip()
#     print(company_name, job_title, application_deadline)
