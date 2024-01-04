#if defined(__GNUC__)
#include <errno.h>
#include <sys/stat.h>

#define WEAK __attribute__((weak))
#define STUB(name, ...)                                                        \
  WEAK int name(__VA_ARGS__) {                                                 \
    errno = ENOSYS;                                                            \
    return -1;                                                                 \
  }

STUB(_close, int f)
STUB(_lseek, int f, int ptr, int dir)
STUB(_fstat, int fs, struct stat *st)
STUB(_getpid, void)
STUB(_isatty, int f)
STUB(_kill, int pid, int sig)
STUB(_link, const char *path1, const char *path2)
STUB(_unlink, const char *path)
STUB(_open, const char *filename, int oflag)
STUB(_stat, const char *f, struct stat *st)

STUB(_write, int handle, char *buffer, int size)
STUB(_read, int handle, char *buffer, int size)

#endif