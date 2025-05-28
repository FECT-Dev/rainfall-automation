from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import csv

# Create a timestamp for the file name
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")

txt_filename = f"rainfall_3hour_{timestamp}.txt"
csv_filename = f"rainfall_3hour_{timestamp}.csv"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://meteo.gov.lk/")
    wait = WebDriverWait(driver, 25)

    # Step 1: Click the "3 Hourly Data" tab
    tab_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '3 Hourly Data')]")))
    tab_button.click()
    time.sleep(5)

    # Step 2: Try to click "Load Data" button (more flexible XPath)
    try:
        load_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@id='tab-content']//button[contains(text(), 'Load Data')]")
        ))
        load_button.click()
        print("✅ Clicked 'Load Data' button.")
    except Exception as e:
        print(f"⚠️ 'Load Data' button not found or not clickable: {e}")

    # Step 3: Wait for actual data to load
    wait.until(EC.presence_of_element_located((By.ID, "tab-content")))
    time.sleep(10)

    # Step 4: Extract data
    rainfall_section = driver.find_element(By.ID, "tab-content")
    data = rainfall_section.text

    # Debug print
    print("=== Scraped Rainfall Data ===")
    print(data)

    # Save as .txt
    with open(txt_filename, "w", encoding="utf-8") as file:
        file.write(data)

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
    with open(csv_filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Station_ID", "Station_Name", "Report_Time", "Rainfall (mm)", "Temperature (°C)", "RH (%)"])
        writer.writerows(records)

    print(f"✅ Data saved: {txt_filename} and {csv_filename}")

finally:
    driver.quit()
