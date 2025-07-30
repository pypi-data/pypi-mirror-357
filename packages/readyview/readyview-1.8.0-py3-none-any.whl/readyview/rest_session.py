import requests
from requests.auth import HTTPBasicAuth

# Base URL preceding all endpoint resources
DEFAULT_BASE_URL = "https://api.readylinks.io/"

class RestSession:
	def __init__(self, organization_id: str, api_key: str, base_url=DEFAULT_BASE_URL):
		self.base_url = base_url
		self.organization_id = organization_id
		self.api_key = api_key
		
	def request(self, method, url):
		reponse = None
		try:
			response = requests.get(self.base_url + url, auth=HTTPBasicAuth(self.organization_id, self.api_key), timeout=100)
		except Exception as e:
			print(str(e))
		return response
			
		
	def get(self, url, params=None):
		response = self.request("GET", url)
		if response:
			if response.status_code != 200:
				return {"error": f'failed with code {response.status_code} {response.text}'}
			return response.json()
		return None
