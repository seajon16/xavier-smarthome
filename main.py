import json
from core import Body


with open('settings.json') as f:
	settings = json.load(f)

# Use get for these two since they can be undefined
location_coords = settings.get('location_coords')
logfile = settings.get('logfile')
# Use indexing for pin mapping since we need it (may throw a KeyError)
pin_mapping = settings['pin_mapping']
body = Body(pin_mapping, location_coords, logfile)

# Control will be given to the body until it sees an interrupt signal
body.start()
# Delete the body, closing the logger and mixer
del body
