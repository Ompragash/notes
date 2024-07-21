# NSE -Securities in Futures and Options
import requests

# Create a session object
session = requests.Session()

# Define the URL and headers for the initial request to get cookies
initial_url = 'https://www.nseindia.com'
initial_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Perform an initial request to the main page to get the cookies
session.get(initial_url, headers=initial_headers)

# Define the URL and headers for the API request
api_url = 'https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O'
api_headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'referer': 'https://www.nseindia.com/market-data/live-equity-market',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Function to fetch data using the session
def fetch_data():
    response = session.get(api_url, headers=api_headers)
    if response.status_code == 200:
        data = response.json()
        print(data)  # Print the data or process it as needed
    else:
        print(f"Failed to retrieve data: {response.status_code}")

# Fetch data
fetch_data()
