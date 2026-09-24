import requests
resp = requests.get("http://127.0.0.1:8081/mcp", headers={"Authorization": "Bearer no-oauth-required"})
print(resp.status_code, resp.text)
