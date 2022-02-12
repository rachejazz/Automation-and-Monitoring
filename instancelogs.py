import boto3
import json
import datetime

PREFIX = ""
client_1 = boto3.client('s3')
client_2 = boto3.client('sqs',
    aws_access_key_id='KEY',
    aws_secret_access_key='KEY'
	)
keys = []

def s3get(prefix):
	global client_1, keys
	response = client_1.list_objects_v2(
	    Bucket='s3_bucket_name',
		Prefix=prefix
	)
	try:
		for i in response['Contents']:
			keys.append(i['Key'])
	except:
		pass
	
def sqssend():
	global client_2, keys
# dummy json body for parsing message body
	jsonfile = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': '', 'eventTime': '', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': ''}, 'requestParameters': {'sourceIPAddress': ''}, 'responseElements': {'x-amz-request-id': '', 'x-amz-id-2': ''}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'PHP Prod ELB', 'bucket': {'name': 's3_bucket_name', 'ownerIdentity': {'principalId': ''}, 'arn': 'arn:aws:s3:::s3_bucket_arn'}, 'object': {'key': 'This will be changed each time', 'size': 4795373, 'eTag': '', 'sequencer': ''}}}]}
	for each in keys:
		print(f"sending {each}...")
		jsonfile['Records'][0]['s3']['object']['key'] = each
		response = client_2.send_message(
		QueueUrl='SQS URL',
		MessageBody=json.dumps(jsonfile, default=datetime_handler)
	)


def datesetup(DATE_MIN, DATE_MAX):
	global PREFIX
	range_min = DATE_MIN.split('-')
	range_max = DATE_MAX.split('-')
	
	years = [int(range_min[0]), int(range_max[0])]
	months = [i for i in range(int(range_min[1]),int(range_max[1])+1)]
	
	day_min = int(range_min[2])
	day_max = int(range_max[2])
	if not months[0] == months[-1]:
		for each in months:
			if not each == months[0] and not each == months[-1]:
				for days in range(1,32):
					PREFIX = f"InstanceLogs/NginxLogs/{days:02d}-{each:02d}-{years[0]}"
					s3get(PREFIX)
	
			else:
				if each == months[0]:
					for days in range(day_min, 32):
						PREFIX = f"InstanceLogs/NginxLogs/{days:02d}-{each:02d}-{years[0]}"
						s3get(PREFIX)
	
				if each == months[-1]:
					for days in range(1, day_max+1):
						PREFIX = f"InstanceLogs/NginxLogs/{days:02d}-{each:02d}-{years[0]}"
						s3get(PREFIX)
	else:
		for days in range(day_min, day_max+1):
			PREFIX = f"InstanceLogs/NginxLogs/{days:02d}-{months[0]:02d}-{years[0]}"
			s3get(PREFIX)
	return True

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def lambda_handler(event, context):
	global PREFIX,keys
	datesetup(event, context)
	sqssend()

if __name__ == '__main__':
	try:
		date_min = input("Enter initial date in format YYYY-MM-DD: ")
		date_max = input("Enter last date in format YYYY-MM-DD: ")
		confirm = input(f"Between {date_min} and {date_max}?[y/n]: ")
		for date in [date_min, date_max]:
			check = len(date.split('-')) == 3 and len(date.split('-')[0]) == 4
			if not check:
				raise
		if confirm == 'y':
			lambda_handler(date_min, date_max)
		else:
			exit("Execute:\npython instancelogs.py")
	except:
		print("Recheck input, have you given the right format?")
