from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import time
import csv
import os  # ⬅️ Added to create a folder

# Create the 'data' folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Timestamped file names
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
txt_filename = f"data/rainfall_3hour_{timestamp}.txt"
csv_filename = f"data/rainfall_3hour_{timestamp}.csv"

# Headless browser options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://meteo.gov.lk/")
    wait = WebDriverWait(driver, 30)

    # Click the "3 Hourly Data" tab
    tab_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '3 Hourly Data')]")))
    tab_button.click()
    time.sleep(5)

    # Retry scraping the rainfall section
    data_loaded = False
    retries = 5
    for _ in range(retries):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        tab_content = soup.find(id="tab-content")
        if tab_content and "Station_ID" in tab_content.text:
            data_loaded = True
            break
        time.sleep(3)

    if not data_loaded:
        print("❌ Rainfall data not found after retrying.")
        data = ""
    else:
        data = tab_content.get_text()

    print("=== Scraped Rainfall Data ===")
    print(data.strip())

    # Save as .txt
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(data)

    # Convert to CSV
    lines = data.splitlines()
    records = []

    for line in lines:
        if line.startswith("Station_ID") or line.strip() == "":
            continue
        parts = line.split()
        if len(parts) >= 7:
            station_id = parts[0]
            station_name = " ".join(parts[1:-5])
            report_time = parts[-5] + " " + parts[-4]
            rainfall = parts[-3]
            temperature = parts[-2]
            rh = parts[-1]
            records.append([station_id, station_name, report_time, rainfall, temperature, rh])

    # Save as .csv
    with open(csv_filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Station_ID", "Station_Name", "Report_Time", "Rainfall (mm)", "Temperature (°C)", "RH (%)"])
        writer.writerows(records)

    print(f"✅ Data saved: {txt_filename} and {csv_filename}")

finally:
    driver.quit()
