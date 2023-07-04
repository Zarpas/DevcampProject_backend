import requests
import json

class BearerAuth(requests.auth.AuthBase):
	def __init__(self, token):
		self.token = token
	def __call__(self, r):
		r.headers["authorization"] = "Bearer " + self.token

id = "12825"
password = "Spiritus1"

api_url = "http://localhost:5000/api/user/v1.0/login"

payload = {
	"id": id,
	"password": password
}

headers = {"Content-Type": "application/json"}

api_response = requests.post(url=api_url, data=json.dumps(payload), headers=headers)
print(api_response.json())


