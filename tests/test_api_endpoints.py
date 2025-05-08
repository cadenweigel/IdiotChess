import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_start_game():
    print("\n🟢 Starting new game...")
    r = requests.post(f"{BASE_URL}/start", json={"mode": "human_vs_bot"})
    print(r.json())

def test_make_move():
    print("\n⚪ Human plays e2 to e4...")
    r = requests.post(f"{BASE_URL}/move", json={"from": [6, 4], "to": [4, 4]})
    print(r.json())

def test_bot_move():
    print("\n⚫ Bot makes a move...")
    r = requests.post(f"{BASE_URL}/bot-move")
    try:
        print(r.json())
    except Exception:
        print("Non-JSON response:", r.text)

def test_get_state():
    print("\n📋 Getting game state...")
    r = requests.get(f"{BASE_URL}/state")
    state = r.json()
    print("Current turn:", state["turn"])
    print("Status:", state["status"])

def test_illegal_move():
    print("\n⛔ Attempting illegal move: e4 to e5 (not our turn or invalid)...")
    r = requests.post(f"{BASE_URL}/move", json={"from": [4, 4], "to": [3, 4]})
    print(r.json())

def test_promotion():
    print("\n👑 Simulating pawn promotion...")
    # This assumes you've moved a white pawn to promotion rank manually for testing
    # You may adapt these positions based on board state
    r = requests.post(f"{BASE_URL}/move", json={"from": [1, 0], "to": [0, 0], "promotion": "Queen"})
    print(r.json())

def run_all_tests():
    test_start_game()
    time.sleep(0.5)
    test_make_move()
    time.sleep(0.5)
    test_bot_move()
    time.sleep(0.5)
    test_get_state()
    time.sleep(0.5)
    test_illegal_move()
    time.sleep(0.5)
    test_promotion()

if __name__ == "__main__":
    run_all_tests()