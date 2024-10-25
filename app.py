import os
import requests
from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)

# Global variables to track scraping status
progress = 0
scraping_thread = None
scraping_active = False

def scrape_nse():
    global progress, scraping_active
    progress = 0
    scraping_active = True

    mongo_uri = os.getenv('MONGODB_URI')
    client = MongoClient(mongo_uri)
    db = client['nse_database']
    collection = db['nse_data']

    url = 'https://www.nseindia.com/market-data/live-equity-market'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example data extraction logic (adjust this to match the actual site structure)
        data = []
        for item in soup.find_all('some_tag'):  # Replace 'some_tag' with actual tag
            entry = {
                'field1': item.find('field1_tag').text,  # Adjust as necessary
                'field2': item.find('field2_tag').text   # Adjust as necessary
            }
            data.append(entry)

        if data:
            collection.insert_many(data)
            print("Data saved to MongoDB!")
        else:
            print("No data found.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraping_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scraping', methods=['POST'])
def start_scraping():
    global scraping_thread
    if not scraping_thread or not scraping_thread.is_alive():
        scraping_thread = threading.Thread(target=scrape_nse)
        scraping_thread.start()
        return jsonify(status="started")
    return jsonify(status="already running")

@app.route('/stop-scraping', methods=['POST'])
def stop_scraping():
    global scraping_active
    scraping_active = False
    return jsonify(status="stopped")

@app.route('/progress')
def get_progress():
    return jsonify(progress=progress)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
