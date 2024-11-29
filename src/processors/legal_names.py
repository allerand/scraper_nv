# processors/legal_names.py
import time
import pandas as pd
import re
from tqdm import tqdm
from collections import Counter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

def create_webdriver():
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-agent={ua.random}')
    return webdriver.Chrome(options=options)

def process_legal_names(df):
    print("\n[INFO] Starting legal names extraction process...")
    
    if 'Legal Name' not in df.columns:
        df['Legal Name'] = pd.NA
    if 'Legal Name Most Freq' not in df.columns:
        df['Legal Name Most Freq'] = pd.NA

    visited_advertisers = {}
    rows_to_process = df[df['Advertiser URLs'].notna() & df['Legal Name'].isna()]
    print(f"[INFO] Found {len(rows_to_process)} rows with advertiser URLs to process")
    
    driver = create_webdriver()

    try:
        for index, row in tqdm(rows_to_process.iterrows(), total=len(rows_to_process), desc="Processing advertiser URLs"):
            urls = row['Advertiser URLs'].split(', ')
            print(f"\n[DEBUG] Processing URLs for index {index}: {urls}")
            legal_names = []

            for url in urls:
                if url.startswith('/'):
                    url = f"https://adstransparency.google.com{url}"
                
                print(f"[DEBUG] Processing URL: {url}")

                match = re.search(r'advertiser/([^?]*)', url)
                if match:
                    advertiser_code = match.group(1)
                else:
                    print(f"[WARNING] No advertiser code found in URL: {url}")
                    continue

                if advertiser_code in visited_advertisers:
                    if visited_advertisers[advertiser_code]:
                        legal_names.append(visited_advertisers[advertiser_code])
                        print(f"[DEBUG] Using cached legal name for {advertiser_code}: {visited_advertisers[advertiser_code]}")
                    continue

                if url.startswith("http"):
                    driver.get(url)
                    time.sleep(3)
                    WebDriverWait(driver, 20).until(
                        lambda driver: driver.execute_script('return document.readyState') == 'complete'
                    )
                else:
                    print(f"[WARNING] Invalid URL skipped: {url}")
                    continue

                try:
                    selectors = [
                        "div.metadata",
                        "div[class*='metadata']",
                        "div.advertiser-info",
                        "//div[contains(text(), 'Legal name')]/..",
                        "//div[contains(text(), 'Based in')]/.."
                    ]
                    
                    metadata_element = None
                    for selector in selectors:
                        try:
                            if selector.startswith("//"):
                                metadata_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                            else:
                                metadata_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                            if metadata_element:
                                break
                        except:
                            continue

                    if not metadata_element:
                        raise NoSuchElementException("No se pudo encontrar la información del anunciante")

                    raw_text = metadata_element.text.strip()
                    print(f"[DEBUG] Raw metadata text: {raw_text}")

                    lines = raw_text.split('\n')
                    legal_name = None
                    location = None

                    for line in lines:
                        if any(text in line.lower() for text in ["legal name", "nombre legal"]):
                            legal_name = line.split(":")[-1].strip()
                        elif any(text in line.lower() for text in ["based in", "se encuentra en"]):
                            location = line.split(":")[-1].strip()

                    legal_name = legal_name if legal_name else "N/A"
                    location = location if location else "N/A"
                    print(f"[DEBUG] Found legal name: {legal_name}, location: {location}")

                    if any(loc in location.lower() for loc in ["united kingdom", "reino unido"]) and legal_name != "N/A":
                        legal_names.append(legal_name)
                        print(f"[DEBUG] Added legal name: {legal_name}")

                    visited_advertisers[advertiser_code] = legal_name

                except Exception as e:
                    print(f"[ERROR] Error loading data from {url}: {str(e)}")
                    visited_advertisers[advertiser_code] = None

            if legal_names:
                df.at[index, 'Legal Name'] = ', '.join(legal_names)
                most_common_name = Counter(legal_names).most_common(1)[0][0]
                df.at[index, 'Legal Name Most Freq'] = most_common_name
                print(f"[INFO] Updated row {index} with legal names: {legal_names}")

    except KeyboardInterrupt:
        print("\n[WARNING] Process interrupted by user.")
    finally:
        driver.quit()

    print("\n[INFO] Legal names extraction completed")
    print("\nFinal verification of the DataFrame:")
    print(df[['Advertiser URLs', 'Legal Name', 'Legal Name Most Freq']].dropna().head())
    
    return df