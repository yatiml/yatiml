#!/bin/bash

# To use this:
# - modify the seq commands in the for loops to select the versions to test
# - create and activate a venv
# - run the script from the root directory

# It will test all the selected versions, and print an overview of which worked
# and which didn't.

# Note that it modifies setup.py, so you'll want to restore that afterwards.

# Tip: $(seq 1 0) gives an empty list

# Currently supported:
# 0.15.71 -> 0.15.100
# 0.16.0 -> 0.16.13
# 0.17.0 -> 0.17.28

# Broken
# 0.17.28 -> 0.17.40
# 0.18.0 -> 0.18.5

# Issues:
# 0.16.6 has a broken type definition
# 0.16.8 does not exist
# 0.17.5 had an incompatible change that got reverted again

outfile=$(mktemp)

for i in $(seq 100 1 100) ; do
    sed -i "s/'ruamel.yaml[^']*'/'ruamel.yaml==0.15.$i'/" setup.py
    tox -r
    if (( $? != 0 )); then
        echo "Version 0.15.$i: broken" >>"${outfile}"
        # break
    else
        echo "Version 0.15.$i: works" >>"${outfile}"
    fi
done

for i in $(seq 0 1 13) ; do
    sed -i "s/'ruamel.yaml[^']*'/'ruamel.yaml==0.16.$i'/" setup.py
    tox -r
    if (( $? != 0 )); then
        echo "Version 0.16.$i: broken" >>"${outfile}"
        # break
    else
        echo "Version 0.16.$i: works" >>"${outfile}"
    fi
done

for i in $(seq 0 1 21) ; do
    sed -i "s/'ruamel.yaml[^']*'/'ruamel.yaml==0.17.$i'/" setup.py
    tox -r
    if (( $? != 0 )); then
        echo "Version 0.17.$i: broken" >>"${outfile}"
        # break
    else
        echo "Version 0.17.$i: works" >>"${outfile}"
    fi
done


cat "${outfile}"
rm "${outfile}"

