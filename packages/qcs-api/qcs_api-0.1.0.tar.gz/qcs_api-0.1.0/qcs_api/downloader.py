import requests

def get_all_data():
    url = "https://quick3.de/hbN.info/database/hbn_defects_structure.db"  # Your Strato download link
    response = requests.get(url)
    with open("downloaded_file.zip", "wb") as f:
        f.write(response.content)
    print("File downloaded successfully!")
