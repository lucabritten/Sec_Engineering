#!/bin/bash

[ ! -f words.txt ] && wget https://www-crypto.htwsaar.de/weber/download/words-f87a5a595d.txt -O words.txt

while read line; do
    user_name=$(echo $line | cut -d " " -f1)
    hash_entry=$(echo $line | cut -d " " -f2)

    salt=$(echo $hash_entry | cut -d "$" -f3)
    echo $user_name
    echo $salt
    echo $hash_entry
    while read word; do
        calculated_hash=$(openssl passwd -1 -salt $salt $word)
        if [ "$hash_entry" = "$calculated_hash" ]; then
            echo "Password for $user_name is $word"
            break
        fi
    done < words.txt
done < users.txt
# !/bin/bash

# [ ! -f words.txt ] && \
# wget https://www-crypto.htwsaar.de/weber/download/words-f87a5a595d.txt -O words.txt

# while IFS= read -r line; do
#     user_name=$(awk '{print $1}' <<< "$line")
#     hash_entry=$(awk '{print $2}' <<< "$line")
#     salt=$(cut -d '$' -f3 <<< "$hash_entry")

#     while IFS= read -r word; do
#         if [ "$hash_entry" = "$(openssl passwd -1 -salt "$salt" "$word")" ]; then
#             echo "Password for $user_name is $word"
#             break
#         fi
#     done < words.txt
# done < users.txt