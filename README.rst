nbackgrounder
-------------
Cache nParticles and nCloth in a background process, freeing you up to continue using Maya while caching.


Command Line
------------
mayapy nbackgrounder.py -f "path\to\maya\file.mb" -d "path\to\cache\dir" -p "particle1" -p "particle2" -fr 100 200

::

    usage: nbackgrounder.py [-h] -f FILEPATH -d CACHEDIR -p PARTICLES [-fr FRANGE FRANGE]

    Cache nParticle systems from your command line, freeing you up to continue
    working inside maya.

    optional arguments:
      -h, --help         show this help message and exit
      -f FILEPATH        Maya filename
      -d CACHEDIR        Cache Directory
      -p PARTICLES       Particles to cache, use more than one -p flag in order to
                         cache more than one particleShape
      -fr FRANGE FRANGE  Frame Range to cache

