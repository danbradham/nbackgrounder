import maya.cmds as cmds
import platform
import os
import subprocess
import contextlib

NBACKGROUNDER_PY = os.path.join(os.path.dirname(__file__), "nbackgrounder.py")

BAT = '''
mayapy "{nback}" -f "{filename}" -d "{cachedir}" {particles} -fr {start} {stop} {mesh}
timeout {timeout}
'''

SH = '''
mayapy "{nback}" -f "{filename}" -d "{cachedir}" {particles} -fr {start} {stop} {mesh}
sleep {timeout}
'''

TEMPLATES = {
    "Windows": BAT,
    "Linux": SH,
    "Darwin": SH
    }


def refresh_ncache():
    for ncache in cmds.ls(type="cacheFile"):
        cmds.setAttr(ncache + ".multiThread", 1)
        cmds.setAttr(ncache + ".multiThread", 0)


def execute(script):
    plat = platform.system()
    if plat == "Windows":
        os.startfile(os.path.abspath(script))
    else:
        starter = {
            "Linux": "xdg-open",
            "Darwin": "open"
        }[plat]
        subprocess.call([starter, script])


@contextlib.contextmanager
def ShellScript(mesh_only=False, post_mesh=False, timeout=10):
    shell_script = generate_shell_script(mesh_only, post_mesh, timeout)
    try:
        yield shell_script
    except Exception, err:
        raise Exception(err)
    finally:
        # try:
        #     os.remove(shell_script)
        # except OSError:
        #     print "Could not remove {0}".format(shell_script)
        pass


def generate_shell_script(mesh_only=False, post_mesh=False, timeout=10):
    '''Generates an OS specific shell script.'''
    template = TEMPLATES.get(platform.system(), None)
    if not TEMPLATES:
        raise OSError("Can not find a shell script template for your OS.")

    particles = " ".join(['-p {0}'.format(n) for n in cmds.ls(sl=True)
                          if cmds.listRelatives(n, type="nParticle")])
    if not particles:
        cmds.headsUpMessage("Select the particle nodes you'd like to cache.")
        raise Exception("Select the particle nodes you'd like to cache.")

    #Get the appropriate data from current Maya session
    filename = cmds.file(query=True, sceneName=True)
    file_prefix = os.path.splitext(os.path.basename(filename))[0]
    mesh_cachedir = os.path.join(
        cmds.workspace(q=True, rd=True),
        cmds.workspace("Alembic", q=True, fre=True),
        file_prefix.split(".")[0])
    cachedir = os.path.join(
        cmds.workspace(q=True, rd=True),
        cmds.workspace("fileCache", q=True, fre=True),
        file_prefix.replace(".", "_"))
    start_time, stop_time = (
        int(cmds.playbackOptions(query=True, min=True)),
        int(cmds.playbackOptions(query=True, max=True)))

    fname, fext = os.path.splitext(filename)
    script_file = fname + ".bat"
    cached_file = fname + "_cached" + fext
    if post_mesh:
        script = template.format(
            nback=NBACKGROUNDER_PY,
            filename=filename,
            cachedir=cachedir,
            particles=particles,
            start=start_time,
            stop=stop_time,
            mesh="",
            timeout=timeout)
        script.replace("sleep {0}".format(timeout), "sleep 10")
        script.replace("timeout {0}".format(timeout), "timeout 10")
        script += template.format(
            nback=NBACKGROUNDER_PY,
            filename=cached_file,
            cachedir=mesh_cachedir,
            particles=particles,
            start=start_time,
            stop=stop_time,
            mesh="-mesh",
            timeout=timeout)
    else:
        script = template.format(
            nback=NBACKGROUNDER_PY,
            filename=filename if not mesh_only else cached_file,
            cachedir=cachedir if not mesh_only else mesh_cachedir,
            particles=particles,
            start=start_time,
            stop=stop_time,
            mesh="-mesh" if mesh_only else "",
            timeout=timeout)

    with open(script_file, 'w') as f:
        f.write(script)

    cmds.headsUpMessage("Shell script generated: " + script_file)
    print "Shell script generated: ", script_file
    return script_file

