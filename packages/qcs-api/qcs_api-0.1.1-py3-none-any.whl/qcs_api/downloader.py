import requests
import os 

FILENAME = "hbn_defects_structure.db"
DATA_PATH = os.path.join(os.path.dirname(__file__), FILENAME)

def get_all_data():
    url = "https://quick3.de/hbN.info/database/hbn_defects_structure.db"  # Your Strato download link
    response = requests.get(url)
    with open(DATA_PATH, "wb") as f:
        f.write(response.content)
    print(f"Database downloaded as {FILENAME}")
