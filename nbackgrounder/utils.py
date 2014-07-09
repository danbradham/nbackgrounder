import maya.cmds as cmds
import platform
import os
import subprocess

NBACKGROUNDER_PY = os.path.join(os.path.dirname(__file__), "nbackgrounder.py")

BAT = '''
mayapy "{nback}" -f "{filename}" -d "{cachedir}" {particles} -fr {start} {stop} {mesh}
timeout 60
'''

SH = '''
mayapy "{nback}" -f "{filename}" -d "{cachedir}" {particles} -fr {start} {stop} {mesh}
'''


def refresh_ncache():
    for ncache in cmds.ls(type="cacheFile"):
        cmds.setAttr(ncache + ".multiThread", 1)
        cmds.setAttr(ncache + ".multiThread", 0)


def start(script):
    plat = platform.system()
    if plat == "Windows":
        os.startfile(os.path.abspath(script))
    else:
        starter = {
            "Linux": "xdg-open",
            "Darwin": "open"
        }[plat]
        subprocess.call([starter, script])


def generate(mesh=False):
    '''Generates an OS specific shell script.'''
    gen_fn = GENERATORS.get(platform.system(), None)
    if not gen_fn:
        raise OSError("Can not find a generator for your OS.")

    #Get the appropriate data from current Maya session
    filename = cmds.file(query=True, sceneName=True)
    file_prefix = os.path.splitext(os.path.basename(filename))[0]
    if mesh:
        cachedir = os.path.join(
            cmds.workspace(q=True, rd=True),
            cmds.workspace("Alembic", q=True, fre=True),
            file_prefix.split(".")[0])
    else:
        cachedir = os.path.join(
            cmds.workspace(q=True, rd=True),
            cmds.workspace("fileCache", q=True, fre=True),
            file_prefix.replace(".", "_"))
    particles = " ".join(['-p {0}'.format(n) for n in cmds.ls(sl=True)
                          if cmds.listRelatives(n, type="nParticle")])
    if not particles:
        cmds.headsUpMessage("Select the particle nodes you'd like to cache.")
        raise Exception("Select the particle nodes you'd like to cache.")
    start_time, stop_time = (
        int(cmds.playbackOptions(query=True, min=True)),
        int(cmds.playbackOptions(query=True, max=True)))

    script = gen_fn(filename, cachedir, particles, start_time, stop_time, mesh)
    print "Shell script generated: ", script
    return script


def generate_bat(filename, cachedir, particles, start_time, stop_time, mesh=False):
    '''Windows Shell Script'''
    bat_file = os.path.splitext(filename)[0] + ".bat"
    bat_txt = BAT.format(
            nback=NBACKGROUNDER_PY,
            filename=filename,
            cachedir=cachedir,
            particles=particles,
            start=start_time,
            stop=stop_time,
            mesh="-mesh" if mesh else "")

    with open(bat_file, "w") as f:
        f.write(bat_txt)

    return bat_file


def generate_sh(filename, cachedir, particles, start_time, stop_time, mesh=False):
    '''Linux Shell Script'''
    sh_file = os.path.splitext(filename)[0] + ".sh"
    sh_txt = SH.format(
            nback=NBACKGROUNDER_PY,
            filename=filename,
            cachedir=cachedir,
            particles=particles,
            start=start_time,
            stop=stop_time)

    with open(sh_file, "w") as f:
        f.write(sh_txt)

    return sh_file


GENERATORS = {
    "Windows": generate_bat,
    "Linux": generate_sh
    }

