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
      -mesh              Create an alembic cache including all meshes attached to your -p particles

Maya nBackgrounder Utils
--------------

Refresh your scenes cacheFile nodes using refresh_cache, allowing you to see more recently cached frames. This is a hack where we just toggle multiThread in the cacheFile node on and then off. For some reason this refreshes the cacheFile node.::

    import nbackgrounder.utils as nbutils
    nbutils.refresh_ncache()

Launch nBackgrounder shell scripts directly from maya using the convenient ShellScript context.

    with nbutils.ShellScript() as shscript:
        nbutils.execute(shscript)

ShellScript acceps the following parameters:
    mesh_only: Generate an alembic cache from all meshes attached to selected particles. (default: False)
    post_mesh: Generate an nParticle cache, then afterwards generate an alembic cache. (default: False)
    timeout: Time to leave shell window open after nBackgrounder is finished. (default: 10)
