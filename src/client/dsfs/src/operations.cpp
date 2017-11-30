#include "encfs.h"
#include "operations.h"

#include "event.h"
#include "context.h"

namespace dsfs::operations {

int open(const char *path, struct fuse_file_info *file)
{
    int ret = encfs::encfs_open(path, file);
    if(ret >= 0)
        dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_OPEN, path);
    return ret;
}

int write(const char *path, const char *buf, size_t size, off_t offset,
          struct fuse_file_info *file)
{
    dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_WRITE, path);
    return encfs::encfs_write(path, buf, size, offset, file);
}

int read(const char *path, char *buf, size_t size, off_t offset,
         struct fuse_file_info *file)
{
    dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_READ, path);
    return encfs::encfs_read(path, buf, size, offset, file);
}

int release(const char *path, struct fuse_file_info *finfo) {
    int ret = encfs::encfs_release(path, finfo);
    if(ret == 0)
        dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_RELEASE, path);
    return ret;
}

int unlink(const char *path)
{
    int ret = encfs::encfs_unlink(path);
    if(ret == 0)
        dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_UNLINK, path);
    return ret;
}

int rmdir(const char *path)
{
    int ret = encfs::encfs_rmdir(path);
    if(ret == 0)
        dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_RMDIR, path);
    return ret;
}

int rename(const char *from, const char *to)
{
    int ret = encfs::encfs_rename(from, to);
    if(ret == 0)
        dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_RENAME, from);
    return ret;
}

    int link(const char *from, const char *to)
    {
        int ret = encfs::encfs_link(from, to);
        if(ret == 0)
            dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_OPEN, to);
        return ret;
    }

    int create(const char *path, mode_t mode, struct fuse_file_info *info)
    {
        int ret = encfs::encfs_create(path, mode, info);
        if(ret >= 0)
            dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_OPEN, path);
        return ret;
    }

    int mknod(const char *path, mode_t mode, dev_t rdev)
    {
        int ret = encfs::encfs_mknod(path, mode, rdev);
        if(ret == 0)
            dsfs::get_context()->event()->notify(dsfs::EventInterface::EVENT_OPEN, path);
        return ret;
    }

}; // namespace dsfs::operations
