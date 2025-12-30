'''
libc_extra.pxd

This file contains Cython definitions libc functions that are not included in
the pxd files shipped with Cython.

Copyright © 2010 Nikolaus Rath <Nikolaus.org>

This file is part of pyfuse3. This work may be distributed under
the terms of the GNU LGPL.
'''

from posix.time cimport timespec

cdef extern from "<dirent.h>" nogil:
    ctypedef struct DIR:
        pass
    cdef struct dirent:
        char* d_name

    dirent* readdir(DIR* dirp)
    int readdir_r(DIR *dirp, dirent *entry, dirent **result)

cdef extern from "<sys/types.h>" nogil:
    DIR *opendir(char *name)
    int closedir(DIR* dirp)

cdef extern from "<string.h>" nogil:
    void *memset(void *b, int c, size_t len)

cdef extern from "<sys/statvfs.h>" nogil:
    ctypedef int fsblkcnt_t
    ctypedef int fsfilcnt_t

    struct statvfs:
        unsigned long f_bsize
        unsigned long f_frsize
        fsblkcnt_t     f_blocks
        fsblkcnt_t     f_bfree
        fsblkcnt_t     f_bavail
        fsfilcnt_t     f_files
        fsfilcnt_t     f_ffree
        fsfilcnt_t     f_favail
        unsigned long  f_fsid
        unsigned long  f_flag
        unsigned long  f_namemax

IF UNAME_SYSNAME == "Darwin":
    cdef extern from "<sys/mount.h>" nogil:
        struct statfs:
            unsigned int   f_bsize
            int            f_iosize
            unsigned long long f_blocks
            unsigned long long f_bfree
            unsigned long long f_bavail
            unsigned long long f_files
            unsigned long long f_ffree
            # f_fsid is complex (val[2])
            # f_owner
            unsigned int   f_type
            unsigned int   f_flags
            unsigned int   f_fssubtype
            # f_fstypename
            # f_mntonname
            # f_mntfromname
            # f_reserved

cdef extern from "<fuse_lowlevel.h>" nogil:
    struct fuse_req:
        pass
    ctypedef fuse_req* fuse_req_t

cdef extern from "pyfuse3.h" nogil:
    int syncfs(int fd)

cdef extern from "xattr.h" nogil:
    int setxattr_p (char *path, char *name,
                    void *value, int size, int namespace)

    ssize_t getxattr_p (char *path, char *name,
                        void *value, int size, int namespace)

    enum:
        EXTATTR_NAMESPACE_SYSTEM
        EXTATTR_NAMESPACE_USER
        XATTR_CREATE
        XATTR_REPLACE
        XATTR_NOFOLLOW
        XATTR_NODEFAULT
        XATTR_NOSECURITY


cdef extern from "gettime.h" nogil:
    int gettime_realtime(timespec *tp)
