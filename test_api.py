import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    'http://localhost:5000/api/chat/FT-8527',
    data=json.dumps({"sender": "user", "message": "hello"}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(e)
