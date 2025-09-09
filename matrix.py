import requests
from requests.structures import CaseInsensitiveDict
import json
import re

# Configuration - create config.json (see readme)
BASE_URL = ""
API_TOKEN = ""
PROJECT = ""   

def clean_from_html(input):
    if input is None:
        return ""
    p = re.compile(r'<.*?>')
    output = p.sub('', input)
    output = output.replace('&nbsp;', '')
    output = output.replace('&deg;', '°')
    output = output.replace('&lt;', '<')
    output = output.replace('&gt;', '>')
    output = output.replace('&ldquo;', '\"')
    output = output.replace('&rdquo;', '\"')
    output = output.replace('&#39;', '\'')
    output = output.replace('&quot;', '\'')
    output = output.replace('&micro;', 'u')
    return output

def exportItemFromJson(base_url, headers, project, json_in):
    export = []
    
    for line in json_in:
        if line['isFolder'] == 1:
            export += exportItemFromJson(base_url, headers, project, line['itemList'])
        else:
            item = {}
            item['ID'] = line['itemRef']
            item['Title'] = line['title']
            item['Description'] = getMatrixItemDesc(base_url, headers, project, item['ID'])
            export.append(item)
    return export

def printRaw(raw, fields):
    for line in raw:
        out = ""
        for f in fields:
            out += line[f] + ' \t'
        print(out)


def getMatrixItems(base_url, headers, project, item_type):

    url = f"{base_url}/{project}/cat/{item_type}"
    response = requests.get(url, headers=headers)
    
    # Handle response
    if response.status_code == 200:
        try:
            data_json = json.loads(response.text)
            raw = exportItemFromJson(base_url, headers, project, data_json['folder']['itemList'])
        except ValueError:
            print("Expected JSON but got:", response.text[:500])  # print the first 500 chars
    else:
        print(f"Error {response.status_code}: {response.text}")
    return raw

def getMatrixItemDesc(base_url, headers, project, item):

    url = f"{base_url}/{project}/item/{item}"
    response = requests.get(url, headers=headers)
    
    # Handle response
    if response.status_code == 200:
        try:
            data_json = json.loads(response.text)
            for i in data_json['fieldValList']['fieldVal']:
                if i['id'] == 21734:  #SRS Description field
                    return clean_from_html(i['value'])
        except ValueError:
            print("Expected JSON but got:", response.text[:500])  # print the first 500 chars
    else:
        print(f"Error {response.status_code}: {response.text}")
    return "No description found"

def main():

    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    BASE_URL = data.get("url")
    API_TOKEN = data.get("token")
    PROJECT = data.get("project")

    headers = {"Authorization": "Token " + API_TOKEN}
    raw = getMatrixItems(BASE_URL, headers, PROJECT, 'SRS')
    printRaw(raw, ['ID', 'Title', 'Description'])

if __name__ == '__main__':
    main()