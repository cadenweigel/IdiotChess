import requests

API_URL = "http://127.0.0.1:5000/api/cleanup-abandoned"
TIMEOUT_MINUTES = 60  # Change as needed

def cleanup_abandoned(timeout=TIMEOUT_MINUTES):
    try:
        print(f"Cleaning up games abandoned for more than {timeout} minutes...")
        response = requests.post(API_URL, json={"timeout": timeout})
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            print(f"Error from server: {data['error']}")
        else:
            print(f"Successfully deleted {data.get('deleted', 0)} abandoned games.")
    except requests.exceptions.RequestException as e:
        print(f"Error cleaning up abandoned games: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    cleanup_abandoned() 