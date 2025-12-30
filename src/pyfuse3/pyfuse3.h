/*
pyfuse3.h

Copyright © 2013 Nikolaus Rath <Nikolaus.org>

This file is part of pyfuse3. This work may be distributed under
the terms of the GNU LGPL.
*/

#define PLATFORM_LINUX 1
#define PLATFORM_BSD 2
#define PLATFORM_DARWIN 3

#ifdef __linux__
#define PLATFORM PLATFORM_LINUX
#elif __FreeBSD_kernel__ && __GLIBC__
#define PLATFORM PLATFORM_LINUX
#elif __FreeBSD__
#define PLATFORM PLATFORM_BSD
#elif __NetBSD__
#define PLATFORM PLATFORM_BSD
#elif __APPLE__ && __MACH__
#define PLATFORM PLATFORM_DARWIN
#else
#error "Unable to determine system (Linux/FreeBSD/NetBSD/Darwin)"
#endif

#if PLATFORM == PLATFORM_DARWIN
#include "darwin_compat.h"
#include <fuse.h>
#include <unistd.h>

typedef struct fuse_darwin_attr pyfuse3_stat_t;
typedef struct fuse_darwin_entry_param pyfuse3_entry_param_t;

/* Shim for missing syncfs on macOS */
static inline int syncfs(int fd) {
  (void)fd;
  sync();
  return 0;
}

/* Macros to map standard stat members to fuse_darwin_attr members */
#define st_ino ino
#define st_mode mode
#define st_nlink nlink
#define st_uid uid
#define st_gid gid
#define st_rdev rdev
#define st_size size
#define st_blocks blocks
#define st_blksize blksize
#define st_flags flags
#define st_atimespec atimespec
#define st_mtimespec mtimespec
#define st_ctimespec ctimespec
#define st_birthtimespec btimespec

#else
/* Linux / generic definitions */
#include <unistd.h> /* for syncfs usually */
/* See also: Include/pthreads.pxd */
#include <semaphore.h>

/* Use standard stat struct */
#include <sys/stat.h>
typedef struct stat pyfuse3_stat_t;
typedef struct fuse_entry_param pyfuse3_entry_param_t;
#endif

#include <fuse.h>
#include <fuse_lowlevel.h>

#if PLATFORM == PLATFORM_LINUX
#include <linux/fs.h>
#endif

#if FUSE_VERSION < 32
#error FUSE version too old, 3.2.0 or newer required
#endif

#ifndef RENAME_EXCHANGE
#define RENAME_EXCHANGE 0
#endif

#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE 0
#endif
