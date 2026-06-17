#!/bin/bash

# Ignore STRG-C
trap '' SIGINT

while [ 1 ];do
    echo -n "Please enter your username: "
    read user_name

    if [ ! -d "TAN/$user_name" ]; then
        echo "User does not exist."
        continue
    fi

    if [ ! -s "TAN/$user_name/tans.txt" ]; then
        echo "No more TANs available"
    fi

    echo -n "Please enter your current TAN: "
    read current_tan

    # Validate the entered TAN
    if [ $(echo -n $current_tan | openssl dgst -sha256 | cut -d " " -f2) == $(cat TAN/$user_name/current_tan.txt) ]; then
        # Write next TAN to current_tan
        echo $current_tan > TAN/$user_name/current_tan.txt
        # Remove the used TAN
        sed -i -e "1d" TAN/$user_name/tans.txt
        echo "Correct TAN! Welcome $user_name!"
    else
        echo "Invalid TAN"
    fi
done