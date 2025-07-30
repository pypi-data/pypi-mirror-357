"""
setup.py - Luke Bouma (luke@astro.princeton.edu) - Jul 2020

Pillaged from https://github.com/garrettj403/SciencePlots
"""

import sys
from setuptools import setup
from setuptools.command.install import install

import atexit, glob, os, shutil
import matplotlib

# Get description from README
root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

def install_styles():

    # Find all style files
    stylefiles = glob.glob('data/*.mplstyle', recursive=True)

    # Find stylelib directory (where the *.mplstyle files go)
    mpl_stylelib_dir = os.path.join(matplotlib.get_configdir() ,"stylelib")
    if not os.path.exists(mpl_stylelib_dir):
        os.makedirs(mpl_stylelib_dir)

    # Copy files over
    print("Installing styles into", mpl_stylelib_dir)
    for stylefile in stylefiles:
        print(os.path.basename(stylefile))
        shutil.copy(
            stylefile,
            os.path.join(mpl_stylelib_dir, os.path.basename(stylefile))
        )

class PostInstallMoveFile(install):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        atexit.register(install_styles)


def readme():
    with open('README.md') as f:
        return f.read()


INSTALL_REQUIRES = [
    'numpy',
    'scipy',
    'matplotlib',
]

###############
## RUN SETUP ##
###############

# run setup.
version = 0.7
setup(
    name='aesthetic',
    version=version,
    description=('a e s t h e t i c'),
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    keywords=[
        'astronomy',
        'matplotlib-style-sheets'
    ],
    url='https://github.com/lgbouma/aesthetic',
    download_url = f'https://github.com/lgbouma/aesthetic/archive/refs/tags/v{str(version).replace(".","")}.tar.gz',
    author='Luke Bouma',
    author_email='bouma.luke@gmail.com',
    license='MIT',
    packages=[
        'aesthetic',
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=['pytest==3.8.2',],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': PostInstallMoveFile,},
)
