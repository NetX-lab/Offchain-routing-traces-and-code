#!/bin/bash


for line in `cat ./pid`
do
	echo $line
	kill -9 $line
done
