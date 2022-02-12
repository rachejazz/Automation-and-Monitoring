#this script transfers log files from s3 bucket to desired remote server
DIR = '~/var/logs'
COPIED_TO = ''
ssh remote_user@<IP> find $DIR -maxdepth <max depth here> -mtime -$1 -mtime +$2 -type f > loglist.txt
while read -r line
do
	rsync -chavzP --stats user@remote.host:$line $COPIED_TO
done < loglist.txt

aws s3 cp $COPIED_TO s3://bucket/ --recursive \
    --exclude "*" --include "*.txt"

rm loglist.txt
