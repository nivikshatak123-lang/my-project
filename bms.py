import time
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- PART 1: EXTRACTION LOGIC ---
def scrape_bookmyshow(city):
    print(f"Starting extraction for {city}...")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.add_argument('--headless') 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Requirement: Allows selecting a city 
    url = f"https://in.bookmyshow.com/explore/events-{city.lower()}"
    driver.get(url)

    events_data = []
    try:
        # Wait up to 10 seconds for the event cards to appear [cite: 36]
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/events/')]"))
        )
        
        cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/events/')]")

        for card in cards:
            try:
                # Extracting fields: name, url [cite: 25]
                name = card.text.split('\n')[0] 
                link = card.get_attribute('href')
                
                if name and link:
                    events_data.append({
                        "event_name": name,
                        "city": city.capitalize(),
                        "url": link,
                        "status": "Active",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    })
            except:
                continue
    finally:
        driver.quit()

    return pd.DataFrame(events_data)

# --- PART 2: STORAGE & DEDUPLICATION LOGIC ---
def update_event_sheet(new_df, filename="event_tracker.xlsx"):
    # Requirement: Deduplication & Storage [cite: 27, 29]
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        
        # Mark old events as 'Expired' if they aren't in the new scrape [cite: 20, 30, 33]
        existing_df.loc[~existing_df['url'].isin(new_df['url']), 'status'] = 'Expired'
        
        # Only pull in truly new events [cite: 18, 29]
        new_only = new_df[~new_df['url'].isin(existing_df['url'])]
        final_df = pd.concat([existing_df, new_only], ignore_index=True)
    else:
        final_df = new_df

    # Stores data in Excel [cite: 15]
    final_df.to_excel(filename, index=False)
    print(f"✅ Success! {filename} updated.")

# --- EXECUTION ---
if __name__ == "__main__":
    target_city = "jaipur" 
    scraped_data = scrape_bookmyshow(target_city)
    
    if not scraped_data.empty:
        update_event_sheet(scraped_data)
    else:
        print("No data found to update.")
