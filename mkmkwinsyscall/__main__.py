#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pathlib import Path
import sys
import shutil
import subprocess
import tempfile

import yaml

def main():
    if len(sys.argv) < 2:
        print('usage: mkmkwinsyscall <config file path>')
        return

    with open(sys.argv[1]) as fd:
        data = yaml.safe_load(fd)

    tempd = tempfile.mkdtemp(prefix='.tmp.', dir='.')

    with open(Path(tempd) / 'tmp.go', 'w') as fd:
        fd.write('package __replace_me__pkg__\n')
        fd.write(gen_go_syscall(data))


    cmds = f'''
    go mod init gendllbind
    go get golang.org/x/sys/windows/mkwinsyscall
    go run golang.org/x/sys/windows/mkwinsyscall -output out.go tmp.go
    '''

    for cmd in cmds.split('\n'):
        subprocess.run(cmd, shell=True, cwd=tempd, capture_output=True).check_returncode()

    with open(Path(tempd) / 'out.go') as fd:
        sys.stdout.write(fd.read())

    shutil.rmtree(tempd)


def gen_go_syscall(data):
    buf = []
    for dll, methods in data.items():
        for name, v in methods.items():
            if not v:
                v = []
            while len(v) <= 3:
                v.append('')

            args = v[0]

            rets = ''
            if v[1]:
                rets = f'({v[1]})'

            goname = name
            if v[2]:
                goname = v[2]

            buf = [*buf, f'//sys {goname}({args}){rets} = {dll}.{name}']

    return '\n'.join(buf)

if __name__ == '__main__':
    main()