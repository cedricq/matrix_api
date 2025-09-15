import requests
from requests.structures import CaseInsensitiveDict
import json
import re
import argparse

# Configuration - create config.json (see readme)
with open("config.json", "r", encoding="utf-8") as f:
    data = json.load(f)
BASE_URL = data.get("url")
API_TOKEN = data.get("token")
PROJECT = data.get("project")

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


def getFieldIdJson(data_json, field):
    for elt in data_json["fieldList"]:
        if elt["label"] == field:
            return elt["id"]
    return None


def exportItemFromJson(json_in, full=True):
    export = []
    
    for line in json_in:
        if line['isFolder'] == 1:
            if "obsolete" not in line['title']:
                export += exportItemFromJson(line['itemList'], full)
        else:
            item = {}
            item['ID'] = line['itemRef']
            item['Title'] = line['title']
            print(item['ID'] + "  \t" + item['Title'])
            if full:
                item['Description'] = getItemField(item['ID'], "Description")
                item['Labels'] = getItemField(item['ID'], "Labels")
            export.append(item)
    return export


def printRaw(raw):
    for line in raw:
        out = ""
        for k in line:
            if "\n" in line[k]:
                line[k] = line[k].replace('\n', ';')
            out += line[k] + ' \t'
            
        print(out)


def getItemField(item, field):

    headers = {"Authorization": "Token " + API_TOKEN}
    param = param = {'field':field}
    url = f"{BASE_URL}/{PROJECT}/field/{item}"
    response = requests.get(url, headers=headers, params=param)
    return clean_from_html(response.text)


def getFolderName(item):

    headers = {"Authorization": "Token " + API_TOKEN}
    url = f"{BASE_URL}/{PROJECT}/item/{item}"
    response = requests.get(url, headers=headers, params={})
    data_json = json.loads(response.text)
    return data_json['title']


def getMatrixItems(item_type, full=True):

    url = f"{BASE_URL}/{PROJECT}/cat/{item_type}"
    print(url)
    headers = {"Authorization": "Token " + API_TOKEN}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data_json = json.loads(response.text)
            raw = exportItemFromJson(data_json['folder']['itemList'], full)
        except ValueError: 
            print("Expected JSON but got:", response.text[:500])  # print the first 500 chars
    else:
        print(f"Error {response.status_code}: {response.text}")
    return raw

def getMatrixItemsFromFolder(folder_id):

    url = f"{BASE_URL}/{PROJECT}/item/{folder_id}"
    print(url)
    headers = {"Authorization": "Token " + API_TOKEN}
    param = {'children':'yes', 'fields':1}
    response = requests.get(url, headers=headers, params=param)
    
    if response.status_code == 200:
        try:
            data_json = json.loads(response.text)
            raw = exportItemFromJson(data_json['itemList'], True)
        except ValueError: 
            print("Expected JSON but got:", response.text[:500])  # print the first 500 chars
    else:
        print(f"Error {response.status_code}: {response.text}")
    return raw

def getWorkItems(item_type):
    raw = getMatrixItems(item_type, True)
    return raw

def getWorkItemsFromFolder(folder_id):
    raw = getMatrixItemsFromFolder(folder_id)
    return raw

def getTest(scheme, param):

    url = f"{BASE_URL}/{PROJECT}{scheme}"
    print(url)
    headers = {"Authorization": "Token " + API_TOKEN}
    response = requests.get(url, headers=headers, params=param)
    
    if response.status_code == 200:
        try:
            data_json = json.loads(response.text)
            return data_json
        except ValueError:
            print("Expected JSON but got:", response.text[:500])  # print the first 500 chars
    else:
        print(f"Error {response.status_code}: {response.text}")
    return "No description found - " + str(response.status_code)



def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder_id", required=True, type=str, default='F-SRS-2', help="Folder ID from which items will be exported")
    parser.add_argument("-i", "--item_id", required=True, type=str, default='SRS-1', help="Folder ID from which items will be exported")
    args = parser.parse_args()

    folder_name = getFolderName(args.folder_id)
    
    print("\n### Get Work Item from folder : " + args.folder_id + " " + folder_name + " ....\n")
    raw = getWorkItemsFromFolder(args.folder_id)
    printRaw(raw)

    print("\n### Get raw JSON data from : " + args.folder_id + " ....\n")
    param = {'children':'yes', 'fields':1}
    data_json = getTest('/item/' + args.folder_id, param)
    print(json.dumps(data_json, indent=4))
    
    print("\n### Get raw JSON data from : " + args.item_id + " ....\n")
    param = {'fields':1}
    data_json = getTest('/item/' + args.item_id, param)
    print(json.dumps(data_json, indent=4))
   
    print("\n### Get Item field Description from : " + args.item_id + " ....\n")
    desc = getItemField(args.item_id, "Description")
    print("Description field = " + desc)


if __name__ == '__main__':
    main()