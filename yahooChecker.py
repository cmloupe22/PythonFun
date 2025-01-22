import yfinance as yf

def determine_status(value, green_range, yellow_range):
    if green_range[0] <= value <= green_range[1]:
        return "GREEN"
    elif yellow_range[0] <= value <= yellow_range[1]:
        return "YELLOW"
    else:
        return "RED"

# Function to analyze a stock and display key metrics with status
def analyze_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Fetch sector and industry
        industry = info.get("industry", "").lower()
        sector = info.get("sector", "").lower()

        # Check for pharmaceutical or biotech keywords
        pharma_keywords = ["pharma", "biotech", "healthcare", "therapeutics"]
        is_pharma = any(keyword in industry for keyword in pharma_keywords) or any(keyword in sector for keyword in pharma_keywords)

        # Display if the stock is in the pharmaceutical or biotech sector
        if is_pharma:
            print(f"{symbol} is a pharmaceutical or biotech stock.")
        else:
            print(f"{symbol} is NOT a pharmaceutical or biotech stock.")

        # Retrieve Market Cap
        market_cap = info.get("marketCap", None)
        if market_cap is not None:
            market_cap_status = determine_status(
                market_cap,
                green_range=(50_000_000, 500_000_000),
                yellow_range=(10_000_000, 50_000_000)
            )
            print(f"Market Cap for {symbol}: ${market_cap:,.2f} (Status: {market_cap_status})")
        else:
            print(f"Market Cap data not available for {symbol}.")

        # Retrieve short interest data
        shares_short = info.get("sharesShort", None)
        float_shares = info.get("floatShares", None)
        short_percentage = info.get("sharesPercentSharesOut", None)
        average_volume = info.get("averageVolume", None)

        # Calculate short percentage of the float
        if shares_short is not None and float_shares:
            short_percentage_float = (shares_short / float_shares) * 100
            float_status = determine_status(
                short_percentage_float,
                green_range=(10, 30),
                yellow_range=(30, 50)
            )
            print(f"Short Percentage (Float) for {symbol}: {short_percentage_float:.2f}% (Status: {float_status})")
        else:
            print(f"Short percentage (float) data not available for {symbol}.")

        # Display short percentage of outstanding shares
        if short_percentage is not None:
            short_out_status = determine_status(
                short_percentage * 100,
                green_range=(5, 20),
                yellow_range=(20, 30)
            )
            print(f"Short Percentage (Outstanding Shares) for {symbol}: {short_percentage * 100:.2f}% (Status: {short_out_status})")
        else:
            print(f"Short percentage (outstanding shares) data not available for {symbol}.")

        # Calculate and display days to cover
        if shares_short is not None and average_volume:
            days_to_cover = shares_short / average_volume
            days_status = determine_status(
                days_to_cover,
                green_range=(2, 5),
                yellow_range=(5, 10)
            )
            print(f"Days to Cover for {symbol}: {days_to_cover:.2f} (Status: {days_status})")
        else:
            print(f"Days to cover data not available for {symbol}.")

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

if __name__ == "__main__":
    for test_symbol in [ "AQST"]:
        print(f"Analyzing {test_symbol}...")
        analyze_stock(test_symbol)
        print("\n" + "-" * 50 + "\n")
