#****************************************************************************
#* setup.py for svdep
#****************************************************************************
import os
import sys
import platform
from setuptools import Extension, find_namespace_packages


proj_dir = os.path.dirname(os.path.abspath(__file__))

try:
    import sys
    sys.path.insert(0, os.path.join(proj_dir, "src/svdep"))
    from __version__ import VERSION, BASE
    base = BASE
    version = VERSION
except ImportError as e:
    base="0.0.5"
    version=base
    print("Import error: %s" % str(e))
    pass

isSrcBuild = False

try:
    from ivpm.setup import setup
    isSrcBuild = os.path.isdir(os.path.join(proj_dir, "src"))
    print("zuspec-arl-dm: running IVPM SrcBuild")
except ImportError as e:
    from setuptools import setup
    print("zuspec-arl-dm: running non-src build")

svdep_dir = proj_dir

ext = Extension("zsp_arl_dm.core",
            sources=[
#                os.path.join(svdep_dir, 'src', "core.pyx"),
                os.path.join('src', "core.pyx"),
            ],
            language="c++",
            include_dirs=[]
        )
ext.cython_directives={'language_level' : '3'}

setup_args = dict(
  name = "svdep",
  version=version,
  packages=['svdep'],
  package_dir = {'' : 'src'},
#  package_data={ 'zsp_arl_dm': [
#      "core.pxd",
#      "decl.pxd" ]},
  author = "Matthew Ballance",
  author_email = "matt.ballance@gmail.com",
  description = ("SystemVerilog source dependency checker"),
  long_description = """
  Provides a SystemVerilog pre-processor that checks whether a collection of source is up-to-date
  """,
  license = "Apache 2.0",
  keywords = ["SystemVerilog", "Verilog", "RTL", "Python"],
  url = "https://github.com/fvutils/svdep",
#  install_requires=[
#    'vsc-dm',
#    'debug-mgr'
#  ],
#  entry_points={
#    'ivpm.pkginfo': [
#        'zuspec-arl-dm = zsp_arl_dm.pkginfo:PkgInfo'
#    ]
#  },
  setup_requires=[
    'cython',
    'ivpm',
    'setuptools_scm',
  ],
  ext_modules=[ext]
)

if isSrcBuild:
#    setup_args["ivpm_extdep_pkgs"] = ["vsc-dm", "debug-mgr"]
    setup_args["ivpm_extra_data"] = {
        "svdep": [
            ("build/cpp/{libpref}svdep{dllext}", ""),
        ]
    }

setup(**setup_args)
