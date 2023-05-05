import sys

from subprocess import Popen

def run_procpip(args, kwargs):
    sys.stdout.flush()

    proc = Popen(args, shell=True,cwd= kwargs)

    stdout, stderr  = proc.communicate()

    if proc.returncode != 0:
        print(stdout, '\n', stderr)
        sys.stdout.flush()
        # raise Exception('Command "%s" failed: %d' % (' '.join(args[0]),proc.returncode))

#Call method: run_procpip(command,workDir)
#command : The command to be executed can be a string.