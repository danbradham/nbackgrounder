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

Maya nBackgrounder Utils
--------------

Refresh your scenes cacheFile nodes using refresh_cache, allowing you to see more recently cached frames. This is a hack where we just toggle multiThread in the cacheFile node on and then off. For some reason this refreshes the node.::

    import nbackgrounder.utils as nbutils
    nbutils.refresh_ncache()

Generate a bat or sh script using generate. Creates a shell script for your current os from your currently select particle nodes. The script will be generated inside the same folder as the current maya scene. All you need to do is run the script and you'll start caching in a separate process.::

    shell_script_path = nbutils.generate()

You can also start the generated nBackgrounder shell script directly from maya.

    nbutils.start(shell_script_path)
