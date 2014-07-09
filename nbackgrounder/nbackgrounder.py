from multiprocessing import Pool
from functools import partial
from glob import glob
import maya.standalone
import maya.mel as mel
import maya.cmds as cmds
import argparse
import time
import os


time_msgs = {
    "hours": "{0:.1f}%  ({1} of {2}) {3:.0f}h {4:.0f}m remaining",
    "minutes": "{0:.1f}%  ({1} of {2}) {3:.0f}m {4:.0f}s remaining",
    "seconds": "{0:.1f}%  ({1} of {2}) {3:.0f}s remaining",
    "notime": "{0:.1f}%  ({1} of {2}) 0s remaining"
}


def format_progress(frame, start_time, frange):
    '''Formats a report message for console.'''
    try:
        num_frames = frange[1] - frange[0]
        frames_processed = frame - frange[0]
        elapsed_ms = time.clock() - start_time
        frame = int(cmds.getAttr("time1.outTime"))
        per = (frame - frange[0]) / float(num_frames)
        tl = (elapsed_ms / frames_processed) * (num_frames - frames_processed)
    except ZeroDivisionError:
        return ""
    minutes, seconds = divmod(tl, 60.0)
    hours, minutes = divmod(minutes, 60.0)

    if hours > 0:
        return time_msgs["hours"].format(
            per * 100, frame, frange[1], hours, minutes)
    if minutes > 0:
        return time_msgs["minutes"].format(
            per * 100, frame, frange[1], minutes, seconds)
    if seconds > 0:
        return time_msgs["seconds"].format(
            per * 100, frame, frange[1], seconds)
    return time_msgs["notime"].format(per * 100, frame, frange[1])

ABC_CALLBACK = "print(format_progress(#FRAME#, {0}, ({1}, {2})))"


def kwargs_to_jargs(**kwargs):
    '''Convenience method for generating jobArgs for alembic import and
    export.'''
    kwargs.setdefault('step', 1.0)
    kwargs.setdefault('attr', 'alembicID')
    paramsOrder = ['root',
                   'frameRange',
                   'step',
                   'uvWrite',
                   'writeVisibility',
                   'worldSpace',
                   'attr',
                   'file']

    params = []
    for param in paramsOrder:
        kwargs.setdefault(param, None)
        if param == "root":
            roots = kwargs[param].split()
            for root in roots:
                params.append('-{0} {1}'.format(param, root))
        elif kwargs[param] is None:
            params.append('-{0}'.format(param))
        else:
            params.append('-{0} {1}'.format(param, kwargs[param]))

    return ' '.join(params)


def background_abc(filepath, cachedir, particles, frange=None):
    '''Background abc Cache

    :param filepath: path to maya file
    :param cachedir: dir to cache
    :param nodes: geo to cache
    '''

    cmds.loadPlugin("AbcExport")

    cmds.file(filepath, open=True, force=True)

    if not frange:
        frange = (
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True))

    particle_nodes = []
    for p in particles:
        if not cmds.objExists(p):
            raise NameError(p + " does not exist in specified scene.")
        particle_nodes.append(cmds.listRelatives(p, type="nParticle")[0])

    meshes = [cmds.listConnections(p + ".outMesh")[0]
              for p in particle_nodes]

    abc_id = os.path.basename(cachedir)
    try:
        os.makedirs(cachedir)
    except OSError:
        pass
    versions = glob(os.path.join(cachedir, '*.abc'))
    fpth = os.path.join(
        cachedir, '{0}.{1:0>3d}.abc'.format(abc_id, len(versions) + 1))
    start_time = time.clock()
    jargs = kwargs_to_jargs(
        root=" ".join(meshes),
        frameRange='{0} {1}'.format(*frange),
        file=fpth)

    cmds.AbcExport(jobArg=jargs + ' -pfc "{0}"'.format(ABC_CALLBACK.format(start_time, *frange)))

    elapsed = time.clock() - start_time
    minutes, seconds = divmod(elapsed, 60.0)
    hours, minutes = divmod(minutes, 60.0)

    print "Cache completed in {0:.0f}h {1:.0f}m {2:.0f}s!".format(
        hours, minutes, seconds)


def background_cache(filepath, cachedir, particles, frange=None):
    '''Background Cache

    :param filepath: path to maya file
    :param cachename: dir to cache
    :param particles: list of particles to cache'''

    cmds.file(filepath, open=True, force=True)

    if not frange:
        frange = (
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True))

    particle_nodes = []
    for p in particles:
        if not cmds.objExists(p):
            raise NameError(p + " does not exist in specified scene.")
        particle_nodes.append(cmds.listRelatives(p, type="nParticle")[0])

    start_time = time.clock()
    num_frames = frange[1] - frange[0]
    cmds.setAttr("time1.outTime", frange[0])

    cache_files = cmds.cacheFile(
        directory=cachedir,
        startTime=frange[0],
        endTime=frange[0],
        cacheableNode=particle_nodes,
        cacheFormat="mcx",
        format="OneFilePerFrame",
        noBackup=True)

    cache_connections = [
        ("{0}.inRange", "{0}.playFromCache"),
        ("{0}.outCacheArrayData", "{0}.cacheArrayData"),
        ("{0}.outCacheData[0]", "{0}.positions"),]

    for p, cache_file in zip(particle_nodes, cache_files):
        cache_node = cmds.cacheFile(
            f=os.path.abspath(os.path.join(cachedir, cache_file + ".xml")),
            createCacheNode=True)
        for src, dest in cache_connections:
            cmds.connectAttr(src.format(cache_node), dest.format(p))

    cmds.file(rename=os.path.splitext(filepath)[0] + "_cached.mb")
    cmds.file(save=True, force=True)

    for i, frame in enumerate(range(frange[0], frange[1] + 1)):
        cmds.setAttr("time1.outTime", frame)
        cmds.cacheFile(
            directory=cachedir,
            startTime=frame,
            endTime=frame,
            appendFrame=True,
            cacheableNode=particle_nodes,
            cacheFormat="mcx",
            format="OneFilePerFrame",
            noBackup=True)
        print(format_progress(frame, start_time, frange))

    cmds.file(save=True, force=True)

    elapsed = time.clock() - start_time
    minutes, seconds = divmod(elapsed, 60.0)
    hours, minutes = divmod(minutes, 60.0)

    print "Cache completed in {0:.0f}h {1:.0f}m {2:.0f}s!".format(
        hours, minutes, seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            'Cache nParticle systems from your command line, freeing you up to'
            ' continue working inside maya.'),
        add_help=True)

    parser.add_argument(
        '-f',
        dest="filepath",
        help="Maya filename",
        required=True)
    parser.add_argument(
        '-d',
        dest="cachedir",
        help="Cache Directory",
        required=True)
    parser.add_argument(
        '-p',
        dest="particles",
        help=(
            "Particles to cache, use more than one -p flag in order to cache"
            " more than one particleShape"),
        action="append",
        required=True)
    parser.add_argument(
        "-fr",
        dest="frange",
        help="Frame Range to cache",
        type=int,
        nargs=2)

    parser.add_argument(
        "-mesh",
        dest="mesh",
        help="Alembic Cache Particles",
        action="store_true",
        default=False)

    kwargs = vars(parser.parse_args())
    mayapystandalone = partial(maya.standalone.initialize, name='python')

    p = Pool(processes=1, initializer=mayapystandalone)
    if kwargs.pop("mesh"):
        p.apply(background_abc, kwds=kwargs)
    else:
        p.apply(background_cache, kwds=kwargs)
