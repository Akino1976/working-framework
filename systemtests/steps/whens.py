import os
import subprocess
import requests

from pytest_bdd import when, parsers


@when('the app is called from the command line')
def call_app_from_command_line(entrypoint, command, flags, request):

    flags_list = flags.split()
    cmd = [*entrypoint, *command, *flags_list]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stderr_value = str(process.stderr.read(), 'utf-8')
    if stderr_value:
        print('------- Captured stderr from application -----')
        print(stderr_value)

    stdoutdata, stderrdata = process.communicate()
    process.stdoutdata = str(stdoutdata, 'utf-8')
    process.stderrdata = str(stderrdata, 'utf-8')
    request.process = process

    process.kill()
