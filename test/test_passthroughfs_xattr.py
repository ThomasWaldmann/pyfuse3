#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
test_passthrough_xattr.py - Unit tests for passthroughfs xattr support.

Copyright © 2015 Nikolaus Rath <Nikolaus.org>

This file is part of pyfuse3. This work may be distributed under
the terms of the GNU LGPL.
'''

if __name__ == '__main__':
    import pytest
    import sys
    sys.exit(pytest.main([__file__] + sys.argv[1:]))

import subprocess
import os
import sys
import pytest
import errno

import pyfuse3

from util import fuse_test_marker, wait_for_mount, umount, cleanup

basename = os.path.join(os.path.dirname(__file__), '..')
TEST_FILE = __file__

pytestmark = fuse_test_marker()

# Only run if underlying filesystem supports xattrs
try:
    with open('/tmp/pyfuse3-xattr-test', 'w') as fh:
        pass
    os.setxattr('/tmp/pyfuse3-xattr-test', 'user.test', b'val')
    os.remove('/tmp/pyfuse3-xattr-test')
except OSError:
    pytestmark = pytest.mark.skip(reason="Underlying filesystem does not support xattrs")
except AttributeError:
    pytestmark = pytest.mark.skip(reason="os module does not support xattrs")


def test_passthrough_xattr(tmpdir):
    mnt_dir = str(tmpdir.mkdir('mnt'))
    src_dir = str(tmpdir.mkdir('src'))
    cmdline = [sys.executable,
               os.path.join(basename, 'examples', 'passthroughfs.py'),
               src_dir, mnt_dir ]
    mount_process = subprocess.Popen(cmdline, stdin=subprocess.DEVNULL,
                                     universal_newlines=True)
    try:
        wait_for_mount(mount_process, mnt_dir)
        tst_xattrs(mnt_dir)
    except:
        cleanup(mount_process, mnt_dir)
        raise
    else:
        umount(mount_process, mnt_dir)

def tst_xattrs(mnt_dir):
    filename = os.path.join(mnt_dir, 'testfile')
    with open(filename, 'w') as fh:
        fh.write('test')
    
    # Test setxattr
    key = 'user.pyfuse3_test'
    value = b'test_value'
    os.setxattr(filename, key, value)

    # Test getxattr
    assert os.getxattr(filename, key) == value

    # Test listxattr
    keys = os.listxattr(filename)
    assert key in keys

    # Test removexattr
    os.removexattr(filename, key)
    
    with pytest.raises(OSError) as exc_info:
        os.getxattr(filename, key)
    assert exc_info.value.errno == pyfuse3.ENOATTR
    
    assert key not in os.listxattr(filename)

    os.unlink(filename)
