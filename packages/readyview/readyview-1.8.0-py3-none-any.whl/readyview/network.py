class Network(object): 
	def __init__(self, rest):
		super(Network, self).__init__()
		self._rest = rest
		
	def get_networks(self):
		url = f"v2/networks"
		return self._rest.get(url)
		
	def get_network(self, id: str):
		url = f"v2/networks/{id}"
		return self._rest.get(url)

	def get_devices(self, id: str):
		url = f"v2/devices?network[0]={id}"
		return self._rest.get(url)
