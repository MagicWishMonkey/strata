#!/bin/bash


python setup.py install --record files.txt && cat files.txt | xargs rm -rf && rm -rf files.txt

# uninstall
# python setup.py develop && rm -rf dist && rm -rf build && rm -rf strata.egg-info