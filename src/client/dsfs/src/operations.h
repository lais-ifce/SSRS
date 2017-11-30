#ifndef DSFS_OPERATIONS_H_H
#define DSFS_OPERATIONS_H_H

#include <cstdio>

namespace dsfs
{
    namespace operations
    {
        int write(const char *path, const char *buf, size_t size, off_t offset,
                  struct fuse_file_info *file);
        int read(const char *path, char *buf, size_t size, off_t offset,
                 struct fuse_file_info *file);
        int unlink(const char *path);
        int rmdir(const char *path);
        int rename(const char *from, const char *to);
        int open(const char *path, struct fuse_file_info *file);
        int release(const char *path, struct fuse_file_info *finfo);
        int link(const char *from, const char *to);
        int create(const char *path, mode_t mode, struct fuse_file_info *info);
        int mknod(const char *path, mode_t mode, dev_t rdev);
    };
};

#endif //DSFS_OPERATIONS_H_H
