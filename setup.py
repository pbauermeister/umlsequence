from distutils.core import setup
import os
import sys
import traceback
import platform
import subprocess


################################################################################

# Version. The revision sum is the 3rd number
VERSION = "1.00.00"

def setVersion(v):
    open(os.path.join("uml_sequence", "__version__.py"), "w").write(
        "VERSION = '%s'\n" % v
        )

################################################################################
# FOR LINUX

def make_linux(info):
    info.update({
            'name': "umlsequence",
            'scripts': ['umlsequence'],
            'packages': ['uml_sequence'],
            })
    setup(**info)



################################################################################

# re-generate version string
setVersion(VERSION)

info = {
    'version': VERSION,
    'description': "UML Sequence generator from text input",
    'author': "Pascal Bauermeister",
    'author_email': "pascal.bauermeister@gmail.com",
    'license': 'GPL-2.0',
}

#make_doc()

if platform.system() == "Windows":
    make_windows(info)  # not yet!
else:
    make_linux(info)    # yes Sir!

# done
################################################################################
