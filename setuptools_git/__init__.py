"""
A hook into setuptools for Git.
"""
import sys

from subprocess import PIPE

from setuptools_git.utils import check_output
from setuptools_git.utils import b
from setuptools_git.utils import fsdecode
from setuptools_git.utils import CalledProcessError


def ntfsdecode(path):
    # We receive the raw bytes from Git and must decode by hand
    if sys.version_info >= (3,):
        try:
            path = path.decode('utf-8')
        except UnicodeDecodeError:
            path = path.decode(sys.getfilesystemencoding())
    else:
        try:
            path = path.decode('utf-8').encode(sys.getfilesystemencoding())
        except UnicodeError:
            pass  # Already in filesystem encoding (hopefully)
    return path


def listfiles(dirname=''):
    # NB: Passing the '-z' option to 'git ls-files' below returns the
    # output as a blob of null-terminated filenames without canonical-
    # ization or use of double-quoting.
    #
    # So we'll get back e.g.:
    #
    # 'pyramid/tests/fixtures/static/h\xc3\xa9h\xc3\xa9.html'
    #
    # instead of:
    #
    # '"pyramid/tests/fixtures/static/h\\303\\251h\\303\\251.html"'
    #
    # for each file.
    try:
        filenames = check_output(
            ['git', 'ls-files', '-z'], cwd=dirname or None, stderr=PIPE)
    except (CalledProcessError, OSError):
        # Setuptools mandates we fail silently
        return

    for filename in filenames.split(b('\x00')):
        if filename:
            if sys.platform == 'win32':
                yield ntfsdecode(filename)
            else:
                yield fsdecode(filename)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        dirname = sys.argv[1]
    else:
        dirname = ''
    for filename in listfiles(dirname):
        try:
            print(filename)
        except UnicodeEncodeError:
            print(repr(filename)[1:-1])

