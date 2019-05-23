#!/bin/bash

cat *.log | grep finished > ./sum.log

awk -f count.awk ./sum.log
