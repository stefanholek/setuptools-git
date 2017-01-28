# -*- coding: utf-8 -*-
import sys
import os
import tempfile
import unittest

from os.path import realpath, join
from setuptools_git.utils import rmtree
from setuptools_git.utils import posix
from setuptools_git.utils import fsdecode
from setuptools_git.utils import hfs_quote
from setuptools_git.utils import compose
from setuptools_git.utils import decompose


class GitTestCase(unittest.TestCase):

    def setUp(self):
        self.old_cwd = os.getcwd()
        self.directory = self.new_repo()

    def tearDown(self):
        os.chdir(self.old_cwd)
        rmtree(self.directory)

    def new_repo(self):
        from setuptools_git.utils import check_call
        directory = realpath(tempfile.mkdtemp())
        os.chdir(directory)
        check_call(['git', 'init', '--quiet', os.curdir])
        return directory

    def create_file(self, *path):
        fd = open(join(*path), 'wt')
        fd.write('dummy\n')
        fd.close()

    def create_dir(self, *path):
        os.makedirs(join(*path))

    def create_git_file(self, *path):
        from setuptools_git.utils import check_call
        filename = join(*path)
        fd = open(filename, 'wt')
        fd.write('dummy\n')
        fd.close()
        if sys.platform == 'darwin':
            try:
                filename = hfs_quote(filename)
            except TypeError:
                pass
        check_call(['git', 'add', filename])
        check_call(['git', 'commit', '--quiet', '-m', 'add new file'])


class listfiles_tests(GitTestCase):

    def listfiles(self, *a, **kw):
        from setuptools_git import listfiles
        return listfiles(*a, **kw)

    def test_at_repo_root(self):
        self.create_git_file('root.txt')
        self.assertEqual(
                set(self.listfiles(self.directory)),
                set(['root.txt']))

    def test_at_repo_root_with_subdir(self):
        self.create_git_file('root.txt')
        self.create_dir('subdir')
        self.create_git_file('subdir/entry.txt')
        self.assertEqual(
                set(self.listfiles(self.directory)),
                set(['root.txt', 'subdir/entry.txt']))

    def test_at_repo_subdir(self):
        self.create_git_file('root.txt')
        self.create_dir('subdir')
        self.create_git_file('subdir/entry.txt')
        self.assertEqual(
                set(self.listfiles('subdir')),
                set(['entry.txt']))

    def test_empty_dirname(self):
        self.create_git_file('root.txt')
        self.assertEqual(
                set(self.listfiles()),
                set(['root.txt']))

    def test_empty_dirname_in_subdir(self):
        self.create_git_file('root.txt')
        self.create_dir('subdir')
        self.create_git_file('subdir/entry.txt')
        os.chdir('subdir')
        self.assertEqual(
                set(self.listfiles()),
                set(['entry.txt']))

    def test_directory_only_contains_another_directory(self):
        self.create_dir('foo/bar')
        self.create_git_file('foo/bar/entry.txt')
        self.assertEqual(
            set(self.listfiles()),
            set(['foo/bar/entry.txt'])
            )
        self.assertEqual(
            set(self.listfiles('foo')),
            set(['bar/entry.txt'])
            )

    def test_nonascii_filename(self):
        filename = 'héhé.html'

        self.create_git_file(filename)

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [filename])

        # git ls-files returns composed UTF-8
        if sys.platform == 'darwin':
            filename = compose(filename)

        self.assertEqual(
                set(self.listfiles(self.directory)),
                set([filename]))

    def test_utf8_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('utf-8')
        else:
            filename = 'héhé.html'

        # Windows does not like byte filenames under Python 3
        if sys.platform == 'win32' and sys.version_info >= (3,):
            filename = filename.decode('utf-8')

        self.create_git_file(filename)

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [fsdecode(filename)])

        # git ls-files returns composed UTF-8
        if sys.platform == 'darwin':
            filename = compose(filename)

        self.assertEqual(
                set(self.listfiles(self.directory)),
                set([fsdecode(filename)]))

    def test_latin1_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('latin-1')
        else:
            filename = 'h\xe9h\xe9.html'

        # Windows does not like byte filenames under Python 3
        if sys.platform == 'win32' and sys.version_info >= (3,):
            filename = filename.decode('latin-1')

        self.create_git_file(filename)

        # HFS Plus quotes unknown bytes
        if sys.platform == 'darwin':
            filename = hfs_quote(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [fsdecode(filename)])

        self.assertEqual(
                set(self.listfiles(self.directory)),
                set([fsdecode(filename)]))

    def test_empty_repo(self):
        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [])

        self.assertEqual(
                set(self.listfiles(self.directory)),
                set([]))

    def test_git_error(self):
        import setuptools_git
        from setuptools_git.utils import CalledProcessError

        def do_raise(*args, **kw):
            raise CalledProcessError(1, 'git')

        self.create_git_file('root.txt')
        saved = setuptools_git.check_output
        setuptools_git.check_output = do_raise
        try:
            self.assertEqual(set(self.listfiles()), set())
        finally:
            setuptools_git.check_output = saved

