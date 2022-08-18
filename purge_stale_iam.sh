#!/usr/bin/env bash
set -e

cleanup() {
	rm -f "$iam_output_file" "$jq_output_file"
}

trap 'cleanup' 0 1 2 15					# cleanup tmp files in case script ends upbruptly.

usage() {								# Function: Print a help message
  echo "Usage: $0 \\
	  [ -n Y|yes (dry run or execute) ] \\
		[ -p project_id ]" 1>&2
}

dry_check() {	
	if [ "$dry_run" = 'true'  ];then
		echo "$@"
	else
		"$@"
	fi
}

project_id="project-id-here"			# Default value
dry_run='false'
while getopts ":n:p:" options
do
case $options in
n)
	dry_run='true'
;;
p)
	project_id=${OPTARG}
;;
*)
	usage
	exit 1
esac
done

if [ $# -eq 0 ];
then
	usage
    exit 1
fi

if [ -f "$jq_output_file"  ]; then rm "$jq_output_file"; fi
date_last_year="$(date -v-1y +"%Y")"							# From last year if ANY
date_last_month="$(date +"%Y")-0[1-$(date -v-1m +"%-m")]"		# Till last month if ANY

iam_output_file=$(mktemp)
jq_output_file=$(mktemp)

gcloud projects get-iam-policy "$project_id" --format=json > "$iam_output_file"

# Below payload parses the json output of gcloud and checks for the expiry date in the "condition" key. 
# If the date is of one month before or of previous year, it matches the rule and prints it.
# The last piping denotes the format of the output of jq i.e. `member_name%condition_keys%role_name`
# Space is not used as a delimiter here because it will cause parsing issues since condition keys already contains spaces that needs to be included.

jq --raw-output --arg date "$date_last_year" '.[]|.[]|select(.condition.expression) | if (.condition.expression | test($date)) then "\(.members|.[])%expression=\(.condition.expression),title=\(.condition.title)%\(.role)" else empty end' >> "$jq_output_file" < "$iam_output_file" 2>/dev/null
jq --raw-output --arg date "$date_last_month" '.[]|.[]|select(.condition.expression) | if (.condition.expression | test($date)) then "\(.members|.[])%expression=\(.condition.expression),title=\(.condition.title)%\(.role)" else empty end' >> "$jq_output_file" < "$iam_output_file" 2>/dev/null

while IFS='%' read -ra line
do
	dry_check gcloud projects remove-iam-policy-binding "$project_id" --member=\'"${line[0]}"\' --role=\'"${line[2]}"\' --condition=\'"${line[1]}"\'
done < "$jq_output_file"

