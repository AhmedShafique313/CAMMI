import requests

linkedin_id = "BiXLFEGlD6"
access_token = "AQWWG8K9blcJibIl9-0t8bo_a_Th9KgqmMsComo6a0iEFJ2zAKtuOAsb_Ot7bjuk3OURUgGR8a-Xn4IiAwG459f8fzUCqkab2NN_QnZ4QnWVwoMCoCWvzgV7oOySmECNVlRHKojAe0vMPEcgnUSyGpOwJAquN4FqdDA1bM-PXKsgtwolbk7QvK3vUfCoqVPfPj4XqNHygxe48BYCOfPS42jJ15QdbbLNLGIu_ykMHDcucm0VffOK102TPlDJMzvbu-1ijBN2anI2iN7qW8xwQQbABlXZJgmfk5A67zINoPILIlzlbHg-G2rf7EJe7q6PBIZJ4D1w62Rvsa_jAHsVyUuFpanzHw"

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
