from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def select_chevrolet_tahoe_with_price_and_zip():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("https://www.cars.com/shopping/")

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "makes[]")))
        driver.find_element(By.NAME, "makes[]").send_keys("Chevrolet")
        print("✅ Chevrolet selected")

        driver.find_element(By.NAME, "models[]").send_keys("Tahoe")
        print("✅ Tahoe selected")

        driver.find_element(By.XPATH, "//option[contains(text(), '$45,000')]").click()
        print("✅ 45k Selected")

        #time.sleep(5)

        zip_input = driver.find_element(By.NAME, "zip")
        zip_input.clear()
        zip_input.send_keys("73301")
        #time.sleep(5)
        print("✅ 73301 entered")

        shadow_host = driver.find_element(By.XPATH, "//spark-button[@type='submit']")
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        search_button = shadow_root.find_element(By.CSS_SELECTOR, "button")

        #search button
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        driver.execute_script("arguments[0].click();", search_button)
        print("🔍 Search button clicked successfully!")

        time.sleep(10)

        #gather the top 10, leather seats, 25,000 miles
        #send myself an email

    except Exception as e:
        print(f"❌ Error during selection: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    select_chevrolet_tahoe_with_price_and_zip()
