To use forecast.py, you need to use python's shelve module to
create a config file with the default location information the
script should use when retreiving forecast information. That is,
run the following in a python shell in the directory the module
will live in:

~~~~
import shelve
shelf = shelve.open('config')
shelf['lat'] = <your latitude>
shelf['lon'] = <your longitude>
shelf['obsstation'] = <your nearest NWS observation station>
shelf['radarstation'] = <your nearest NWS radar station>
shelf.close()
~~~~
