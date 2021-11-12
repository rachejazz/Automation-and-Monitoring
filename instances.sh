#!/bin/bash
echo "|KeyName|LaunchedOn|Tags|" > ec2instances.md
echo "|-|-|-|" >> ec2instances.md

aws ec2 describe-instances | jq  -r '{"Reservations"}|.[]|.[].Instances|.[] | "\(.KeyName)|\(.LaunchTime)|\(.Tags)"' >> ec2instances.md


