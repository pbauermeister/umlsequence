#!/bin/bash

# cleanup
rm -rf deb_dist/

# run setup
python setup.py --command-packages=stdeb.command bdist_deb
