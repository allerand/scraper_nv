import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm
import time
import random
from selenium import webdriver
from utils.file_operations import save_to_csv
import config
import os

def create_webdriver(headless=True):
    """
    Create and configure the webdriver with optimized options
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--lang=en-US")
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=options)

def process_google_ads(df, days=30):
    """
    Process Google Ads for a specific period of days
    """
    df = df.copy()
    
    # Define column names
    column_name = f"Advise_{days}d"
    url_column = f"url_{days}d"
    
    # Initialize columns if they don't exist
    for col in [column_name, url_column, "Advise URLs", "Advertiser URLs"]:
        if col not in df.columns:
            df.loc[:, col] = pd.NA

    # Mark invalid domains as "No"
    df.loc[df['Root Domain'] == "No URL found", column_name] = "No"

    # Filter rows to process
    mask = (
        df[column_name].isna() &
        df['Root Domain'].notna() &
        (df['Root Domain'].str.strip() != '') &
        (df['Root Domain'] != 'No URL found') &
        ~(df['Advise_30d'] == "Yes" if days == 90 else False)
    )
    
    rows_to_process = df[mask]
    total_rows = len(rows_to_process)
    
    if total_rows == 0:
        print(f"[INFO] No rows to process for {days} days")
        return df

    driver = create_webdriver()
    
    step_date_dir = os.path.join(config.STEPS_DIR, config.TODAY_DATE)
    os.makedirs(step_date_dir, exist_ok=True)
    step_filename = os.path.join(step_date_dir, f"STEP_{5 if days == 30 else 6}_google_ads_{days}d.csv")

    with tqdm(total=total_rows, desc=f"Processing ads for {days} days") as pbar:
        for index, row in rows_to_process.iterrows():
            domain = row['Root Domain']
            url = f"https://adstransparency.google.com/?region=GB&domain={domain}&preset-date=Last+{days}+days"
            df.loc[index, url_column] = url

            try:
                driver.get(url)
                # Wait for the page to fully load
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(2)  # Additional wait to ensure dynamic elements load

                # Find advertiser elements using multiple selectors
                advertiser_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/advertiser/']")
                
                if not advertiser_elements:
                    # Try another selector if the first one fails
                    advertiser_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/advertiser/')]")

                if advertiser_elements:
                    df.loc[index, column_name] = "Yes"
                    
                    # Collect advertiser URLs
                    href_values = [el.get_attribute('href') for el in advertiser_elements]
                    df.loc[index, 'Advise URLs'] = ', '.join(href_values)

                    # Collect additional URLs
                    additional_urls = []
                    for el in advertiser_elements:
                        try:
                            parent_element = el.find_element(
                                By.XPATH, 
                                "following-sibling::div[contains(@class, 'thumbnail-container')]"
                            )
                            additional_urls.append(parent_element.get_attribute('href'))
                        except NoSuchElementException:
                            additional_urls.append('')
                            
                    df.loc[index, 'Advertiser URLs'] = ', '.join(filter(None, additional_urls))
                else:
                    df.loc[index, column_name] = "No"

            except (NoSuchElementException, TimeoutException) as e:
                print(f"[ERROR] Timeout/NoElement for {domain}: {str(e)}")
                df.loc[index, column_name] = "No"
            except Exception as e:
                print(f"[ERROR] Error processing {domain}: {str(e)}")
                df.loc[index, column_name] = "Error"

            time.sleep(random.uniform(2, 5))
            pbar.update(1)

            # Save progress every 10 records
            if pbar.n % 10 == 0:
                save_to_csv(df, step_filename)

    driver.quit()
    
    # Update 90-day data if processing 30-day data
    if days == 30:
        mask_30d = df['Advise_30d'] == "Yes"
        df.loc[mask_30d, 'Advise_90d'] = "Yes"
        df.loc[mask_30d, 'url_90d'] = df.loc[mask_30d, 'url_30d']

    return df
