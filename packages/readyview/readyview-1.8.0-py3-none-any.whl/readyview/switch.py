class Switch(object): 
	def __init__(self, rest):
		super(Switch, self).__init__()
		self._rest = rest
		
	def get_ports(self, mac_address: str):
		url = f"v1/devices/{mac_address}/switch/ports/cache"
		return self._rest.get(url)

	def get_switch(self, mac_address: str):
		url = f"v1/devices/{mac_address}/switch/cache"
		return self._rest.get(url)

	def get_switches(self):
		url = "v2/devices?device_type=Switch"
		return self._rest.get(url)

	def get_device(self, id: str):
		url = f'v2/devices/{id}'
		return self._rest.get(url)

	def display_info(self):
		return (
			f"MAC Address: {self.mac_address}\n"
		)
