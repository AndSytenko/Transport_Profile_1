#!/bin/bash

# Remove tech and debug info off the SR OS config files

if [[ $# -lt 1 ]]; then
    sed -E '/^#( vim|\{ DEBUG):/d'
#    echo "Usage: $0 <config_file>"
#    exit
else
    sed -i'' -E '/^#( vim|\{ DEBUG):/d' $1
fi
