#!/bin/bash

if [ $# -ne 2 ];then
    echo "Please use this tool like: ./generate_tan.sh <username> <n>, where n is the number of tans";
    exit 1;
fi
USER_NAME=$1
n=$2

if [ -d "TAN/$USER_NAME" ]; then
    echo "User already exists."
    exit 1
fi

USER_PATH="TAN/$USER_NAME"
mkdir $USER_PATH

if [ $? -ne 0 ];then
    echo "Error during subdir generation"
    exit 1
fi

echo -n "Please enter your password: "
read PASSWORD

touch TAN/$USER_NAME/tans.txt
if [ $? -ne 0 ];then
    echo "Error during TAN-file generation"
    rm -rf $USER_PATH
    exit 1
fi
COUNTER=0
PREV_HASH=$PASSWORD
while [ $COUNTER -lt $n ]; do
    CURRENT_HASH=$(echo -n $PREV_HASH | openssl dgst -sha256 | cut -d " " -f2)
    echo $current_hash >> $USER_PATH/tans.txt
    PREV_HASH=$CURRENT_HASH
    COUNTER=$((COUNTER+1))
done

# Reverse tan order n -> n-1 -> ... -> 0
tail -r TAN/$user_name/tans.txt > TAN/$user_name/tans_tmp.txt
mv TAN/$user_name/tans_tmp.txt TAN/$user_name/tans.txt

# Save tan n+1 in current_tan for server to validate
touch TAN/$user_name/current_tan.txt
if [ $? -ne 0 ];then
    echo "Error during current TAN-file generation"
    rm -rf TAN/$user_name
    exit 1;
fi
final=$(echo -n "$current_hash" | openssl dgst -sha256 | cut -d " " -f2)
echo $final > TAN/$user_name/current_tan.txt
