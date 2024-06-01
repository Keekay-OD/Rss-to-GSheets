import os
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from feedgen.feed import FeedGenerator

# Load credentials and create a service client
creds = None
with open('tradingbot-425112-f2e36bc0983a.json') as source:
    creds = service_account.Credentials.from_service_account_info(json.load(source))

service = build('sheets', 'v4', credentials=creds)

# The ID of your Google Spreadsheet
SPREADSHEET_ID = '10vWdfv-zBWVHsseiNrCDW32s7Vu2KdEo1DcqOLtH978'
RANGE_NAME = 'Sheet1!A1:C100'  # Adjust the range as needed

# Fetch Tech News Data
def fetch_tech_news():
    api_key = '7c5b24c135f04806b7f42a1a11d36833'
    keywords = 'bitcoin'
    url = f'https://newsapi.org/v2/everything?q={keywords}&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    articles = news_data.get('articles', [])
    
    # Debugging: Print fetched articles
    print(f"Fetched {len(articles)} articles")
    for article in articles:
        print(article)
        
    return [(article['source']['name'], article['title'], article['description']) for article in articles]

# Write Data to Google Sheets
# Write Data to Google Sheets
def write_to_google_sheets(data):
    # Calculate the range based on the size of the data
    num_rows = len(data)
    num_cols = len(data[0]) if data else 0
    end_column = chr(ord('A') + num_cols - 1) if num_cols > 0 else 'A'
    end_row = num_rows if num_rows > 0 else 1
    range_name = f'Sheet1!A1:{end_column}{end_row}'

    body = {
        'values': data
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption='RAW', body=body).execute()

    # Debugging: Print the result of the update operation
    print('Google Sheets update result:', result)

# Generate RSS Feed from Google Sheets Data
def generate_rss_feed():
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Debugging: Print the result to see the raw API response
    print('API Response:', result)
    print('Values:', values)

    # Generate RSS feed
    fg = FeedGenerator()
    fg.id('http://example.com/rss')
    fg.title('Tech News RSS Feed')
    fg.description('Latest updates on technology, gaming, and PC parts')
    fg.author({'name': 'Keekay', 'email': 'Keekay@pm.me'})
    fg.link(href='http://example.com', rel='alternate')
    fg.language('en')

    if values:
        headers = values[0]
        for row in values[1:]:
            entry = fg.add_entry()
            entry.id(row[0] if len(row) > 0 else 'No ID')
            entry.title(row[1] if len(row) > 1 else 'No Title')
            entry.description(row[2] if len(row) > 2 else 'No Description')

        rss_feed = fg.rss_str(pretty=True)

        # Save the RSS feed to a file
        with open('rss_feed.xml', 'wb') as f:
            f.write(rss_feed)

        print('RSS feed generated and saved as rss_feed.xml')
    else:
        print('No data found in the specified range.')

# Main Execution
if __name__ == '__main__':
    # Fetch tech news data
    news_data = fetch_tech_news()

    # Prepare data for Google Sheets (including headers)
    sheet_data = [['Source', 'Title', 'Description']] + news_data

    # Debugging: Print the data being written to Google Sheets
    print('Data to be written to Google Sheets:', sheet_data)

    # Write data to Google Sheets
    write_to_google_sheets(sheet_data)

    # Generate RSS feed from Google Sheets data
    generate_rss_feed()
