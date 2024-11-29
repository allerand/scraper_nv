#processors/facebook_ads.py

import requests
import config
import pandas as pd

def check_ads(domain):
    if not domain or domain == "No URL found":
        return "No", "No"

    params = {
        "search_terms": domain,
        "search_type": "KEYWORD_EXACT_PHRASE",
        "ad_delivery_date_min": config.DATE_90_DAYS_AGO,
        "ad_reached_countries": "GB",
        "access_token": config.ACCESS_TOKEN
    }
    response = requests.get("https://graph.facebook.com/v20.0/ads_archive", params=params)
    data = response.json()

    advise_90d, advise_30d = "No", "No"
    if 'data' in data and data['data']:
        advise_90d = "Yes"
        for ad in data['data']:
            if ad['ad_delivery_start_time'] >= config.DATE_30_DAYS_AGO:
                advise_30d = "Yes"
                break

    return advise_90d, advise_30d

def add_facebook_ads_data(df):
    fb_data = df['Root Domain'].apply(check_ads).apply(pd.Series)
    fb_data.columns = ['Advise_90d_Fb', 'Advise_30d_Fb']
    df = pd.concat([df, fb_data], axis=1)
    return df