from distutils.core import setup
import os
import sys
import traceback
import platform
import subprocess


################################################################################

# Version. The revision sum is the 3rd number
VERSION = "1.00.%s"

def _get_scm_rev():
    """For build time: compute revision from SCM info"""
    p = subprocess.Popen(["svnversion", "-c"], stdout=subprocess.PIPE)
    output = p.communicate()[0].strip()
    output = output.split(":")[-1] # take rev of last modified file
    if ("%s " % output)[0].isdigit():
        return output
    return None

def getVersionFromScm():
    """For build time: build version str"""
    rev_number = _get_scm_rev()
    if rev_number is None:
        rev_number = "unknown-revision"
        valid = False
    else:
        rev_number = rev_number
        valid = True

    version_str = VERSION % rev_number
    return version_str, valid

def setVersion(s):
    open(os.path.join("uml_sequence", "__version__.py"), "w").write(
        "VERSION = '%s'\n" % s
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
version_str, valid = getVersionFromScm()
if valid:
    setVersion(version_str)
print version_str

info = {
    'version': version_str,
    'description': "JewelPUMP Logs Tool",
    'author': "Pascal Bauermeister - Debiotech S.A.",
    'author_email': "p.bauermeister@debiotech.com",
    'url': 'http://www.debiotech.com/',
    'license': 'proprietary',
}

#make_doc()

if platform.system() == "Windows":
    make_windows(info)  # not yet!
else:
    make_linux(info)    # yes Sir!

# done
################################################################################
