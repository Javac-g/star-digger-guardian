import requests
import os
import json
import sys
from datetime import datetime

TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_ACTOR")

if not TOKEN:
    print("ERROR: GITHUB_TOKEN is missing")
    sys.exit(1)

if not USERNAME:
    print("ERROR: GITHUB_ACTOR is missing")
    sys.exit(1)

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Broad keyword detection (robust)
KEYWORDS = ["star","stars", "repo", "follow", "back"]


def is_spam(bio):
    if not bio:
        return False

    bio = bio.lower()
    score = sum(1 for k in KEYWORDS if k in bio)

    return score >= 2


def get_followers():
    followers = []
    page = 1

    print("Fetching followers...")

    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page=100&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Failed to fetch followers:", response.status_code, response.text)
            break

        data = response.json()

        if not data:
            break

        followers.extend(data)
        page += 1

    print(f"Total followers fetched: {len(followers)}")
    return followers


def get_user(login):
    url = f"https://api.github.com/users/{login}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch user {login}:",
              response.status_code, response.text)
        return {}

    return response.json()


def block_user(login):
    url = f"https://api.github.com/user/blocks/{login}"
    response = requests.put(url, headers=headers)

    print("Block status:", login, response.status_code)

    if response.status_code == 204:
        print("Successfully blocked:", login)
        return True
    else:
        print("Failed to block:", login, response.text)
        return False


def load_blocked():
    try:
        with open("blocked-users.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_blocked(data):
    with open("blocked-users.json", "w") as f:
        json.dump(data, f, indent=2)


def main():
    followers = get_followers()
    blocked = load_blocked()

    already_blocked_logins = [u["login"] for u in blocked]

    print("Starting scan...")

    for follower in followers:
        login = follower["login"]

        user = get_user(login)
        bio = user.get("bio")

        print("Checking:", login, "| Bio:", bio)

        if is_spam(bio):
            print("Spam detected:", login)

            if login not in already_blocked_logins:
                success = block_user(login)

                if success:
                    blocked.append({
                        "login": login,
                        "blocked_at": datetime.utcnow().isoformat()
                    })
                    already_blocked_logins.append(login)
            else:
                print("Already in blocked list:", login)

    save_blocked(blocked)

    print("Scan completed.")


if __name__ == "__main__":
    main()
