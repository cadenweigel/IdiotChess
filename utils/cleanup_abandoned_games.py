import requests

API_URL = "http://127.0.0.1:5000/api/cleanup-abandoned"
TIMEOUT_MINUTES = 60  # Change as needed

def cleanup_abandoned(timeout=TIMEOUT_MINUTES):
    try:
        response = requests.post(API_URL, json={"timeout": timeout})
        response.raise_for_status()
        data = response.json()
        print(f"Deleted {data.get('deleted', 0)} abandoned games (older than {timeout} minutes).")
    except Exception as e:
        print("Error cleaning up abandoned games:", e)

if __name__ == "__main__":
    cleanup_abandoned() 