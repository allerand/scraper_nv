# processors/email_extraction.py

import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import pandas as pd
from datetime import datetime

ua = UserAgent()

def extract_emails_from_url(url):
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Regex for valid emails, avoiding image extensions
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b', str(soup))
        
        # Filter out any email that ends in image file extensions or other exclusions
        valid_emails = [
            email for email in emails
            if not any(email.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'])
        ]
        return valid_emails

    except requests.exceptions.RequestException as e:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] ERROR: Unable to access {url}. Details: {str(e)}")
        return []

def add_email_data(df):
    print("\n[INFO] Starting email extraction process...")
    total_rows = len(df)
    processed = 0
    emails_found = 0
    
    df.loc[:, 'Email'] = 'N/A'
    df.loc[:, 'Most Common Email'] = 'N/A'
    emails_by_domain = {}

    for index, row in df.iterrows():
        processed += 1
        if processed % 10 == 0:  # Progress update every 10 records
            print(f"[INFO] Processing progress: {processed}/{total_rows} records ({(processed/total_rows*100):.1f}%)")
        
        url = row['URL']
        root_domain = row['Root Domain']
        
        if pd.isna(url) or url in ['No URL found', 'N/A']:
            df.at[index, 'Emails'] = 'No URL found'
            df.at[index, 'Most Common Email'] = 'No URL found'
            emails_by_domain[root_domain] = {'Emails': 'No URL found', 'Most Common Email': 'No URL found'}
            continue

        # Check cache to avoid re-processing the same domain
        if root_domain in emails_by_domain:
            df.at[index, 'Emails'] = emails_by_domain[root_domain]['Emails']
            df.at[index, 'Most Common Email'] = emails_by_domain[root_domain]['Most Common Email']
            continue

        # Extract emails from URL
        unique_emails = extract_emails_from_url(url)
        if unique_emails:
            emails_found += 1
            most_common_email = max(set(unique_emails), key=unique_emails.count)
            df.at[index, 'Emails'] = ', '.join(unique_emails)
            df.at[index, 'Most Common Email'] = most_common_email
            emails_by_domain[root_domain] = {'Emails': ', '.join(unique_emails), 'Most Common Email': most_common_email}
        else:
            df.at[index, 'Emails'] = 'No emails found'
            df.at[index, 'Most Common Email'] = 'No emails found'
            emails_by_domain[root_domain] = {'Emails': 'No emails found', 'Most Common Email': 'No emails found'}

    success_rate = (emails_found / total_rows) * 100 if total_rows > 0 else 0
    print(f"\n[SUMMARY] Email extraction completed:")
    print(f"• Total records processed: {total_rows}")
    print(f"• Successful email extractions: {emails_found}")
    print(f"• Success rate: {success_rate:.1f}%")
    print(f"• Unique domains processed: {len(emails_by_domain)}\n")

    return df