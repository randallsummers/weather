# forecast.py

To setup forecast.py, you simply need to create a file named
'config.py' with the following contents:

~~~~
uagent = 'Some user agent string'
lat = 'Your latitutde as a string'
lon = 'Your longitude as a string'
obsstation = 'Your nearest NWS observation station'
radarstation = 'Your nearest NWS radar station'
~~~~

You can then import forecast.py as a module and call the functions,
i.e.

~~~~
from weather import forecast
print(forecast.daily())
~~~~

Or you can use forecast.py as a command line script, i.e.

~~~~
forecast.py daily
~~~~

forecast.py supports several command line arguments, which are
described by calling

~~~~
forecast.py -h
~~~~

## Dependencies

Make sure your python environment can import all modules listed at the
top of forecast.py