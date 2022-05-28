import requests


def get_token(client_id: int, client_secret: str) -> str:
    url = "https://osu.ppy.sh/oauth/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public"
    }

    resp = requests.post(url, data=params).json()

    with open("token.txt", "w") as f:
        f.write(resp["access_token"])
    return resp["access_token"]


if __name__ == "__main__":
    token = get_token(6322, "G5Dpfd1hAgAt8zkt0aFklV8bteaZITv1vC2bxcfO")
    print(token)
