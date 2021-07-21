#!/bin/bash

# To use this:
# - remove the version constraint on ruamel.yaml in setup.py
# - modify the seq commands in the for loops to select the versions to test
# - create and activate a venv
# - run the script from the root directory

# It will test all the selected versions, and print an overview of which worked
# and which didn't.

# Tip: $(seq 1 0) gives an empty list

# Currently supported:
# 0.15.71 -> 0.15.100
# 0.16.0 -> 0.16.10

# Issues:
# 0.16.6 has a broken type definition
# 0.16.8 does not exist

outfile=$(mktemp)

for i in $(seq 71 1 100) ; do
    pip install --upgrade "ruamel.yaml==0.15.$i"
    python setup.py test
    if (( $? != 0 )); then
        echo "Version 0.15.$i: broken" >>"${outfile}"
        break
    else
        echo "Version 0.15.$i: works" >>"${outfile}"
    fi
done

for i in $(seq 10 1 13) ; do
    pip install --upgrade "ruamel.yaml==0.16.$i"
    python setup.py test
    if (( $? != 0 )); then
        echo "Version 0.16.$i: broken" >>"${outfile}"
        # break
    else
        echo "Version 0.16.$i: works" >>"${outfile}"
    fi
done

for i in $(seq 0 1 10) ; do
    pip install --upgrade "ruamel.yaml==0.17.$i"
    python setup.py test
    if (( $? != 0 )); then
        echo "Version 0.17.$i: broken" >>"${outfile}"
        # break
    else
        echo "Version 0.17.$i: works" >>"${outfile}"
    fi
done


cat "${outfile}"
rm "${outfile}"

