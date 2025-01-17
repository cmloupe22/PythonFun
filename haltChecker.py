import requests
from bs4 import BeautifulSoup
import yfinance as yf 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, time as dt_time
import pytz
import time
import csv

# Gmail credentials
gmail_user = ''
gmail_password = ''

# Recipients
email_addresses = ['']

# URL of the Nasdaq halted stocks page
url = "https://www.nasdaqtrader.com/trader.aspx?id=tradehalts"

# Tracking processed halts to avoid dups
processed_halts = set()

# Store checked tickers to avoid rework
checked_symbols = set()

# Store unresolved halts
unresolved_halts = {}

# CSV file for historical purposes
email_log_file = "email_log.csv"

#Write to historical csv file
with open(email_log_file, "a", newline="") as file:
    writer = csv.writer(file)
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Stock Ticker", "Market Cap", "Short Percentage (Float)", 
                         "Market Cap Status", "Short Float Status", "Days to Cover", "Days Status", 
                         "Confidence Rating (%)"])

start_time = dt_time(5, 55)  # 5:55 AM
end_time = dt_time(19, 0)    # 7:00 PM
central_tz = pytz.timezone('US/Central')

blacklisted_companies = [
    'pfizer', 'johnson & johnson', 'novartis', 'merck', 'gsk',
    'sanofi', 'astrazeneca', 'roche', 'abbvie', 'bayer', 'amgen'
]

# Function to assign investment status
def determine_status(value, green_range, yellow_range):
    if green_range[0] <= value <= green_range[1]:
        return "GREEN"
    elif yellow_range[0] <= value <= yellow_range[1]:
        return "YELLOW"
    else:
        return "RED"

def fetch_halted_stocks():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="divTradeHaltResults"]/div/table'))
    )

    page_source = driver.page_source
    driver.quit()

    # Use BeautifulSoup to scrape page
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('div', {'id': 'divTradeHaltResults'}).find('table')
    rows = table.find_all('tr')[1:]  # Header --> first row

    halted_stocks = []
    for row in rows:
        cols = row.find_all('td')
        halted_stocks.append({
            "Halt Date": cols[0].text.strip(),
            "Halt Time": cols[1].text.strip(),
            "Issue Symbol": cols[2].text.strip(),
            "Issue Name": cols[3].text.strip(),
            "Market": cols[4].text.strip(),
            "Reason Codes": cols[5].text.strip(),
            "Pause Threshold Price": cols[6].text.strip() if len(cols) > 6 else None,
            "Resumption Date": cols[7].text.strip(),
            "Resumption Quote Time": cols[8].text.strip(),
            "Resumption Trade Time": cols[9].text.strip(),
        })
    return halted_stocks

def is_pharma_stock_with_metrics(symbol):
    try:
        if symbol in checked_symbols:
            return False, None, None, None, None, None, None

        stock = yf.Ticker(symbol)
        info = stock.info
        industry = info.get("industry", "").lower()
        sector = info.get("sector", "").lower()
        company_name = info.get("longName", "").lower()

        checked_symbols.add(symbol)

        if any(blacklisted in company_name for blacklisted in blacklisted_companies):
            print(f"{company_name} is blacklisted.")
            return False, None, None, None, None, None, None

        pharma_keywords = ["pharma", "biotech", "healthcare", "therapeutics"]
        is_pharma = any(keyword in industry for keyword in pharma_keywords) or any(keyword in sector for keyword in pharma_keywords)

        # Fetch metrics
        market_cap = info.get("marketCap", None)
        shares_short = info.get("sharesShort", 0)
        float_shares = info.get("floatShares", None)
        short_percentage_float = (shares_short / float_shares) * 100 if float_shares else None
        average_volume = info.get("averageVolume", 1)  # Avoid division by zero
        days_to_cover = shares_short / average_volume if average_volume > 0 else None

        # Assign investment status
        market_cap_status = determine_status(market_cap, (50_000_000, 500_000_000), (10_000_000, 50_000_000)) if market_cap else "Not Available"
        float_status = determine_status(short_percentage_float, (10, 30), (30, 50)) if short_percentage_float else "Not Available"
        days_status = determine_status(days_to_cover, (2, 5), (5, 10)) if days_to_cover else "Not Available"

        if is_pharma:
            print(f"{symbol} ({company_name}) is a pharmaceutical or biotech stock.")
            return True, market_cap, short_percentage_float, market_cap_status, float_status, days_to_cover, days_status
        else:
            print(f"{symbol} ({company_name}) is NOT a pharmaceutical or biotech stock.")
            return False, None, None, None, None, None, None
    except Exception as e:
        print(f"Error determining metrics for {symbol}: {e}")
        checked_symbols.add(symbol)
        return False, None, None, None, None, None, None

def calculate_confidence(market_cap_status, float_status, days_status):
    score = 0

    if market_cap_status == "GREEN":
        score += 30
    elif market_cap_status == "YELLOW":
        score += 15

    if float_status == "GREEN":
        score += 30
    elif float_status == "YELLOW":
        score += 15

    if days_status == "GREEN":
        score += 20
    elif days_status == "YELLOW":
        score += 10

    return score

def send_email_and_log(subject, body, ticker, market_cap, short_percentage_float, market_cap_status, float_status, days_to_cover, days_status, confidence):
    try:
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)

        for email in email_addresses:
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            server.sendmail(gmail_user, email, text)

        server.quit()
        print(f"Email sent successfully to {email_addresses}")

        # Log the email data to the CSV file
        with open(email_log_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now(central_tz).strftime("%Y-%m-%d %H:%M:%S"),
                ticker,
                f"${market_cap:,.2f}" if market_cap is not None else "Not Available",
                f"{short_percentage_float:.2f}%" if short_percentage_float is not None else "Not Available",
                market_cap_status,
                float_status,
                f"{days_to_cover:.2f}" if days_to_cover is not None else "Not Available",
                days_status,
                f"{confidence}%"
            ])

    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def monitor_halted_stocks(check_interval=300):
    global processed_halts, unresolved_halts

    while True:
        now = datetime.now(central_tz)
        current_time = now.time()

        if current_time < start_time or current_time > end_time:
            print("Outside of trading hours. Waiting until the next check...")
            time.sleep(check_interval)
            continue

        halted_stocks = fetch_halted_stocks()
        for stock in halted_stocks:
            symbol = stock['Issue Symbol']
            unique_id = f"{symbol}-{stock['Halt Date']}-{stock['Halt Time']}"
            reason_code = stock['Reason Codes']

            # Skip already processed halts
            if unique_id in processed_halts:
                continue

            # Only process halts with Reason Codes T1, T2, or T3
            if reason_code not in ["T1", "T2", "T3"]:
                print(f"Skipping {symbol} due to irrelevant reason code: {reason_code}")
                continue

            try:
                # Get stock metrics
                is_pharma, market_cap, short_percentage_float, market_cap_status, float_status, days_to_cover, days_status = is_pharma_stock_with_metrics(symbol)
                if not is_pharma:
                    continue

                # Calculate confidence
                confidence = calculate_confidence(market_cap_status, float_status, days_status)

                # Fallback for missing data
                market_cap_str = f"${market_cap:,.2f}" if market_cap else "Not Available"
                short_percentage_str = f"{short_percentage_float:.2f}%" if short_percentage_float else "Not Available"
                days_to_cover_str = f"{days_to_cover:.2f}" if days_to_cover else "Not Available"

                # Create the email body
                subject = f"Pharma Stock Halted: {symbol}"
                body = (
                    f"The pharmaceutical stock {symbol} ({stock['Issue Name']}) is currently halted.\n\n"
                    f"Details:\n"
                    f"Halt Date: {stock['Halt Date']}\n"
                    f"Halt Time: {stock['Halt Time']}\n"
                    f"Market: {stock['Market']}\n"
                    f"Reason Codes: {reason_code}\n"
                    f"Resumption Date: {stock['Resumption Date']}\n"
                    f"Resumption Trade Time: {stock['Resumption Trade Time']}\n\n"
                    f"Metrics:\n"
                    f"Market Cap: {market_cap_str} (Status: {market_cap_status})\n"
                    f"Short Percentage (Float): {short_percentage_str} (Status: {float_status})\n"
                    f"Days to Cover: {days_to_cover_str} (Status: {days_status})\n\n"
                    f"**Confidence Score**: {confidence}/80\n"

                )

                # Send email and log
                send_email_and_log(subject, body, symbol, market_cap, short_percentage_float, market_cap_status, float_status, days_to_cover, days_status, confidence)

                processed_halts.add(unique_id)

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                # If data is missing --> log an empty row
                with open(email_log_file, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        datetime.now(central_tz).strftime("%Y-%m-%d %H:%M:%S"),
                        symbol,
                        "Error",
                        "Error",
                        "Error",
                        "Error",
                        "Error",
                        "Error",
                        "Error"
                    ])

        print(f"Waiting {check_interval} seconds before the next check...")
        time.sleep(check_interval)



if __name__ == "__main__":
    monitor_halted_stocks(check_interval=120)
