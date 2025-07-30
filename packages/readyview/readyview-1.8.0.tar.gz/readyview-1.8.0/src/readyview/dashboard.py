from . import rest_session
from .switch import Switch
from .network import Network
import os

class Dashboard:
	def __init__(self, organization_id=None, api_key=None):
		self.organization_id = organization_id or os.environ.get("READYVIEW_DASHBOARD_ORG_ID")
		self.api_key = api_key or os.environ.get("READYVIEW_DASHBOARD_API_KEY")
		self._rest = rest_session.RestSession(self.organization_id, self.api_key)
		self.switch = Switch(self._rest)		
		self.network = Network(self._rest)		

	def display_info(self):
		return (
			f"Org ID: {self.organization_id}\n"
			f"API Key: {self.api_key}\n"
		)
		
