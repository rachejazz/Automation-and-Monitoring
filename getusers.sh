#!/bin/bash
#Usage:
#./getusers.sh <TOKEN> <GROUP ID>
#
i=1
rm users ids final
while [[ $i -ne 10 ]]
do
	curl -s --header "PRIVATE-TOKEN: $1" "https://gitlab.com/api/v4/groups/$2/projects?simple=true&order_by=last_activity_at&pagination=keyset&per_page=100&page=$i" | jq -r '.[]|.id' > ids
	while read -r line
	do
		echo "for project $line"
		curl -s --header "PRIVATE-TOKEN: $1" "https://gitlab.com/api/v4/projects/$line/members/all?per_page=100&page=1" | jq -r '.[]|.username' >> users
	done < ids
	let "i++"
done
cat users | sort | uniq > final
rm users ids
