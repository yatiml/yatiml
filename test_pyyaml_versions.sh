#!/bin/bash

# To use this:
# - modify the seq commands in the for loops to select the versions to test
# - run the script from the root directory

# It will test all the selected versions, and print an overview of which worked
# and which didn't.

# Note that it modifies setup.py, so you'll want to restore that afterwards.

# Tip: $(seq 1 0) gives an empty list

# Currently supported:
# 5.1
# 5.1.1
# 5.1.2
# 5.2
# 5.3
# 5.3.1
# 5.4
# 6.0
# 6.0.1

# Broken
# 3.13 and earlier don't work on modern Python
# 5.4.1 fails to install, botched release?

# Issues:

outfile=$(mktemp)

for i in 3.10 3.11 3.12 3.13 5.1 5.1.1 5.1.2 5.2 5.3 5.3.1 5.4 5.4.1 6.0 6.0.1 ; do
    sed -i "s/'PyYAML[^']*'/'PyYAML==$i'/" setup.py
    tox -r
    if (( $? != 0 )); then
        echo "Version $i: broken" >>"${outfile}"
        # break
    else
        echo "Version $i: works" >>"${outfile}"
    fi
done


cat "${outfile}"
rm "${outfile}"

