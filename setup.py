from setuptools import setup, find_packages

version = '2.0'

setup(
    name="setuptools-git",
    version=version,
    maintainer='Stefan H. Holek',
    maintainer_email='stefan@epy.co.at',
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="https://github.com/stefanholek/setuptools-git",
    keywords='distutils setuptools git',
    description="Setuptools revision control system plugin for Git",
    long_description=open('README.rst').read(),
    license='BSD-3-Clause',
    packages=find_packages(),
    test_suite='setuptools_git',
    zip_safe=True,
    classifiers=[
        "Topic :: Software Development :: Version Control",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        ],
    entry_points="""
        [setuptools.file_finders]
        git=setuptools_git:listfiles
        """
)
