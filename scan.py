import requests
import os
import json
from datetime import datetime

TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_ACTOR")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SPAM_PATTERNS = [
    "give me stars",
    "star back",
    "follow for follow",
    "stars to my repositories",
    "i will star your repo",
    "GIVE ME STARS TO MY REPOSITORIES AND BACK TO YOUR REPOSITORIES"
]

def is_spam(bio):
    if not bio:
        return False

    bio = bio.lower()

    keywords = ["star", "repo", "follow", "back"]

    score = sum(1 for k in keywords if k in bio)

    return score >= 2


def get_followers():
    followers = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data:
            break

        followers.extend(data)
        page += 1

    return followers

def get_user(login):
    url = f"https://api.github.com/users/{login}"
    return requests.get(url, headers=headers).json()


def block_user(login):
    url = f"https://api.github.com/user/blocks/{login}"
    r = requests.put(url, headers=headers)
    print("Block status:", login, r.status_code, r.text)


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

    for follower in followers:
        login = follower["login"]
        user = get_user(login)

        if is_spam(user.get("bio")):
            if login not in blocked:
                print("Blocking:", login)
                block_user(login)
                blocked.append({
                    "login": login,
                    "blocked_at": datetime.utcnow().isoformat()
                })

    save_blocked(blocked)


if __name__ == "__main__":
    main()
