#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
test_examples.py - Unit tests for Python-LLFUSE.

Copyright © 2015 Nikolaus Rath <Nikolaus.org>

This file is part of Python-LLFUSE. This work may be distributed under
the terms of the GNU LGPL.
'''

if __name__ == '__main__':
    import pytest
    import sys
    sys.exit(pytest.main([__file__] + sys.argv[1:]))

import subprocess
import os
import sys
import time
import pytest
import stat
import shutil
import platform
import errno
from pytest import raises as assert_raises

basename = os.path.join(os.path.dirname(__file__), '..')

# For Python 2 + 3 compatibility
if sys.version_info[0] == 2:
    subprocess.DEVNULL = open('/dev/null', 'w')

def skip_if_no_fuse():
    '''Skip test if system/user/environment does not support FUSE'''

    if platform.system() == 'Darwin':
        # No working autodetection, just assume it will work.
        return

    # Python 2.x: Popen is not a context manager...
    which = subprocess.Popen(['which', 'fusermount'], stdout=subprocess.PIPE,
                             universal_newlines=True)
    try:
        fusermount_path = which.communicate()[0].strip()
    finally:
        which.wait()

    if not fusermount_path or which.returncode != 0:
        pytest.skip("Can't find fusermount executable")

    if not os.path.exists('/dev/fuse'):
        pytest.skip("FUSE kernel module does not seem to be loaded")

    if os.getuid() == 0:
        return

    mode = os.stat(fusermount_path).st_mode
    if mode & stat.S_ISUID == 0:
        pytest.skip('fusermount executable not setuid, and we are not root.')

    try:
        fd = os.open('/dev/fuse', os.O_RDWR)
    except OSError as exc:
        pytest.skip('Unable to open /dev/fuse: %s' % exc.strerror)
    else:
        os.close(fd)
skip_if_no_fuse()


def wait_for_mount(mount_process, mnt_dir):
    elapsed = 0
    while elapsed < 30:
        if os.path.ismount(mnt_dir):
            return True
        if mount_process.poll() is not None:
            pytest.fail('file system process terminated prematurely')
        time.sleep(0.1)
        elapsed += 0.1
    pytest.fail("mountpoint failed to come up")

def cleanup(mnt_dir):
    if platform.system() == 'Darwin':
        subprocess.call(['umount', '-l', mnt_dir], stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    else:
        subprocess.call(['fusermount', '-z', '-u', mnt_dir], stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

def umount(mount_process, mnt_dir):
    if platform.system() == 'Darwin':
        subprocess.check_call(['umount', '-l', mnt_dir])
    else:
        subprocess.check_call(['fusermount', '-z', '-u', mnt_dir])
    assert not os.path.ismount(mnt_dir)

    # Give mount process a little while to terminate. Popen.wait(timeout)
    # was only added in 3.3...
    elapsed = 0
    while elapsed < 30:
        if mount_process.poll() is not None:
            if mount_process.returncode == 0:
                return
            pytest.fail('file system process terminated with code %d' %
                        mount_process.exitcode)
        time.sleep(0.1)
        elapsed += 0.1
    pytest.fail('mount process did not terminate')

def name_generator(__ctr=[0]):
    __ctr[0] += 1
    return 'testfile_%d' % __ctr[0]

def test_lltest(tmpdir):
    mnt_dir = str(tmpdir)
    cmdline = [sys.executable,
               os.path.join(basename, 'examples', 'lltest.py'),
               mnt_dir ]
    mount_process = subprocess.Popen(cmdline, stdin=subprocess.DEVNULL,
                                     universal_newlines=True)
    try:
        wait_for_mount(mount_process, mnt_dir)
        assert os.listdir(mnt_dir) == [ 'message' ]
        filename = os.path.join(mnt_dir, 'message')
        with open(filename, 'r') as fh:
            assert fh.read() == 'hello world\n'
        with pytest.raises(IOError) as exc_info:
            open(filename, 'r+')
        assert exc_info.value.errno == errno.EPERM
        with pytest.raises(IOError) as exc_info:
            open(filename + 'does-not-exist', 'r+')
        assert exc_info.value.errno == errno.ENOENT
    except:
        cleanup(mnt_dir)
        raise
    else:
        umount(mount_process, mnt_dir)
