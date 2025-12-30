'''
macros.pxd

Cython definitions for macros.c

Copyright © 2018 Nikolaus Rath <Nikolaus.org>

This file is part of pyfuse3. This work may be distributed under
the terms of the GNU LGPL.
'''

from fuse_lowlevel cimport fuse_stat_t

cdef extern from "macros.c" nogil:
    long GET_BIRTHTIME(fuse_stat_t* buf)
    long GET_ATIME_NS(fuse_stat_t* buf)
    long GET_CTIME_NS(fuse_stat_t* buf)
    long GET_MTIME_NS(fuse_stat_t* buf)
    long GET_BIRTHTIME_NS(fuse_stat_t* buf)

    void SET_BIRTHTIME(fuse_stat_t* buf, long val)
    void SET_ATIME_NS(fuse_stat_t* buf, long val)
    void SET_CTIME_NS(fuse_stat_t* buf, long val)
    void SET_MTIME_NS(fuse_stat_t* buf, long val)
    void SET_BIRTHTIME_NS(fuse_stat_t* buf, long val)

    void ASSIGN_DARWIN(void*, void*)
    void ASSIGN_NOT_DARWIN(void*, void*)
