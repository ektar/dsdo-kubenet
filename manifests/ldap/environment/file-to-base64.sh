#!/bin/bash

# print a file encode into base64

FILE=$1

FILE_ENCODED=$(cat $FILE | base64)
echo  $FILE_ENCODED
