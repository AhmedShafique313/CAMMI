import requests

linkedin_id = "BiXLFEGlD6"
access_token = "AQU4yKMLg40Q9-skg7Q0HlNhVfEBMqjSpv_nTsVSMpfdvUR6TMdh4UhaUPMq7WGSSaiEcSolJZhB38wc-2cxLs9Y4o8mlYy4KDkhu1fpw0nfBFH3XdjEAD6M6YL_tyj7eW2oKoRvQkcxdlF0DRjh9H7J3cdLsVDZwbWT_9NSQe4NisUGRRCvcwfbDom_JJ9EGH1CGkgat3QGddhpaBzKCDQgneHKl81HjNaHYnwh4UySE2nO7vufYAjVQFFv0cKJACv5hxfqHr8w2u9nXeZ7svB5xM2ktjXe8zoCBg1QzEQnGuHVYSHCoustuwTcSzCMoWgxqkDQYxdWinKm3W7Z0UxVIrffEA"

url = "https://api.linkedin.com/v2/ugcPosts"

payload = {
    "author": f"urn:li:person:{linkedin_id}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "Hello World! Posting directly with my token."},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(response.json())
