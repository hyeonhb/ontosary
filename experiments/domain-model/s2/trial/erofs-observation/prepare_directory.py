"""Guest administrator's only conditional filesystem change."""
import json
import os
import stat


def prepare(parent="/tmp"):
    if os.path.realpath(parent) != parent:
        raise ValueError("unexpected temp directory alias")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_fd = os.open(parent, flags)
    name = "codex-daemon-22002"
    try:
        # mkdir rejects *any* existing entry before chown is possible.
        os.mkdir(name, 0o700, dir_fd=parent_fd)
        fd = os.open(name, flags, dir_fd=parent_fd)
        try:
            os.fchown(fd, 22002, 22002)
            info = os.fstat(fd)
            if (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (22002, 22002, 0o700):
                raise RuntimeError("directory identity mismatch")
            return dict(path=parent + "/" + name, uid=info.st_uid, gid=info.st_gid,
                        mode=oct(stat.S_IMODE(info.st_mode)), inode=info.st_ino)
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


if __name__ == "__main__":
    print(json.dumps(prepare()))
