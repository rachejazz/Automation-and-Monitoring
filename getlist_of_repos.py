#!/bin/python
import requests
import sys
import json

def getlist(token, page_no = 10):
	group_id = ""
	data = ""
	data_json = []
	data_list = []
	for page in range(page_no):
		url = f"https://gitlab.com/api/v4/groups/{group_id}/projects?simple=true&order_by=last_activity_at&pagination=keyset&per_page=100&page={page}"
		req = requests.get(
				url = url,
				headers = {"PRIVATE-TOKEN": token}
				)
		data += req.text+'%%%%'
		data_list = data.split('%%%%')
	for each in range(len(data_list)):
		if not data_list[each] == '':
			per_data = json.loads(data_list[each])
			data_json.extend(per_data)
	with open("README.md", 'w') as PR:
		PR.write("|Name|Created At|Last Activity At|Web Url|\n")
		PR.write("|----|----------|-------------|-------|\n")
		for each in data_json:
			PR.write(f"{each['name']}|{each['created_at']}|{each['last_activity_at']}|{each['web_url']}\n")

if __name__ == "__main__":
	try:
		token = sys.argv[1]
		page_no = int(sys.argv[2])
		getlist(token, page_no)
	except:
		print("Usage\n\t./getlist_of_repos.py <Access Token> <Max Page Limit>\n")

