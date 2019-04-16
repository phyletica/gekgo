#!/bin/bash

this_dir="`dirname $0`"

if [ "$this_dir" = '.' ]
then
    base_dir="`pwd`"
else
    cd "$this_dir"
    base_dir="`pwd`"
fi

curl -o darwin-tol-copyright-boris-kulikov-2007.jpg http://www.boriskulikov.com/images/DarwinTreeOfLife-%20L.jpg
