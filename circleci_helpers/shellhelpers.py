# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import select
import io
import re

from collections import namedtuple

# Regex matches assignments: FOO=foo foo BAR="bar = bar" COO=coo = coo
ENV_ASSIGNMENT = re.compile(r'(\w+)=((.|\s)*?)((?=\w+=)|$)')


def _shell_out_kwargs(args, env=None, shell='/bin/bash'):
    env_copy = os.environ.copy()
    env_copy.update(env or {})
    kwargs = {
        'env': env_copy, 'args': args,
        'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE,
        'stdin': subprocess.PIPE
    }
    if isinstance(args, str):
        kwargs.update({'executable': shell, 'shell': True})

    return kwargs


def shell_out(command, env=None, shell='/bin/bash', stdin=None):
    '''Process command (in a shell or not), process the output
       continuously as it appears.

    Returns:
        namedtuple: struct with fields: command, returncode, pid, success and failed
    '''
    klass_struct = namedtuple('ostruct', 'command returncode pid success failed')

    # Start subprocess
    kwargs = _shell_out_kwargs(command, env=env, shell=shell)
    proc = subprocess.Popen(**kwargs)
    fdlist = [proc.stdout, proc.stderr]

    # Check if stdin provided as string or a file.
    if stdin and isinstance(stdin, str):
        proc.stdin.write(stdin)
        proc.stdin.close()
    elif stdin and (hasattr(stdin, 'fileno') and hasattr(stdin, 'read')):
        fdlist.append(stdin)
    elif stdin:
        raise TypeError('stdin must be type of str or file-like object')

    # Process streams in non-blocking way by reading chunks and
    # blocking until the data appears.
    while True:
        ios = select.select(fdlist, [], [])
        for fd in ios[0]:
            if fd == stdin:
                data = stdin.read(io.DEFAULT_BUFFER_SIZE)
                proc.stdin.write(data)
                # Finish proc stdin processing since source eof is reached.
                if not data:
                    fdlist.remove(stdin)
                    proc.stdin.close()
            elif fd == proc.stdout:
                sys.stdout.write(proc.stdout.read(io.DEFAULT_BUFFER_SIZE))
            else:
                sys.stderr.write(proc.stderr.read(io.DEFAULT_BUFFER_SIZE))

        if proc.poll() is not None:
            break

    return klass_struct(command, proc.returncode, proc.pid,
                        proc.returncode == 0, proc.returncode != 0)


def readenv(source):
    '''Reads environment variable assignments from env file or string'''
    if not (isinstance(source, str) or hasattr(source, 'readlines')):
        raise TypeError('source must type of str or file-like object')

    env = {}
    data = [source]
    if hasattr(source, 'readlines'):
        data = source.readlines()

    for line in data:
        # skip commented lines from others extract assignments
        if re.match(r'\s#', line):
            continue
        for match in re.finditer(ENV_ASSIGNMENT, line):
            name, value = match.groups()[0:2]
            env[name] = value.rstrip()

    return env
