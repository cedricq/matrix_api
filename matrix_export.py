#!/usr/bin/python3
import matrix_api as api
import html_export as export

import os
from lxml import etree
import csv
import argparse
import re

green_light = '#ccffcc'
yellow_light = '#FFD966'
red_light = '#ffcccc'
grey_light = '#d3d3d3'
white = '#FFFFFF'

req_id_regexp = r"\s*((?:SDD|SRS)[- _,.]*0*\d{1,6})"


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


def colorize(value):
    if ("5-Catastrophic" in value 
        or "5-Frequent" in value 
        or "Unacceptable(" in value
        or "(FAIL)" in value
        or "Error" == value
        or "Fail" == value
        or '' == value):
        return red_light
    elif ("4-Significant" in value or "3-Moderate" in value 
        or "4-Possible" in value or "3-Unlikely" in value
        or "Review(" in value
        or "Review" == value
        or "(SKIPPED)" in value
        or "Skipped" == value):
        return yellow_light
    elif ("2-Minor" in value or "1-Negligible" in value 
        or "2-Rare" in value or "1-Improbable" in value
        or "Acceptable(" in value
        or "Approved" == value
        or "Published" == value
        or "(PASS)" in value
        or "Pass" == value):
        return green_light
    elif ("New" == value
          or "Reopen" == value
          or "Not in execution" == value
          or "Not Completed" == value):
        return grey_light
    else:
        return white
    

def create_table_around(title):
    output = '<table border=1 width=100%>\n'
    output += '  <tr><td>' + title + '\n' + '</td></tr>'
    output += '</table>\n'
    output += '<br>\n'
    return output


def table_as_html(table_in, table_title):
    root = etree.Element('html')
    table = etree.SubElement(root, 'table')
    table.set('border', "1")
    table.set('cellpadding', "2")
    thead = etree.SubElement(table, 'thead')
    tr = etree.SubElement(thead, 'tr')
    if table_title != "":
        th = etree.SubElement(tr, 'th')
        th.set('colspan', str(len(table_in[0])))
        th.set('bgcolor', grey_light)
        th.text = table_title
    tr1 = etree.SubElement(thead, 'tr')

    for key in table_in[0]:
        etree.SubElement(tr1, 'th').text = key
    for th in tr1:
        th.set("bgcolor", grey_light)
    tbody = etree.SubElement(table, 'tbody')
    
    for line in table_in:
        print(line)
        tr = etree.SubElement(tbody, 'tr')
        for key in line:
            value = clean_from_html(line[key])
            etree.SubElement(tr, 'td').text = value
        for td in tr:
            text = (etree.tostring(td)).decode('utf-8')
            text = clean_from_html(text)
            td.set('bgcolor', colorize(text))
    output = etree.tostring(root).decode("utf-8")

    return output

def export_csv(data, csv_file):
    columns = list(data[0].keys())
    line = ""
    lines = []
    for c in columns:
        line += c + ';'
    lines.append(line + '\n')
    for row in data:
        line = ""
        for c in columns:
            text = row[c].replace('\n', " ")
            line += text + ';'
        lines.append(line + '\n')
            
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        for l in lines:
            f.write(l)


def main():   

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_filename", required=False, type=str, default="output.html", help="HTML format, default is \'output.html\'")
    parser.add_argument("-f", "--folder_id", required=True, type=str, default='F-PREQ-16', help="Folder ID from which items will be exported")
    args = parser.parse_args()
    
    folder_name = api.getFolderName(args.folder_id)
    print("\n### Exporting from folder: " + args.folder_id + " " + folder_name + " ....\n")
    rows_srs = api.getWorkItemsFromFolder(args.folder_id)
    export.generate_interactive_html_table(rows_srs, out_path=args.output_filename, title="Interactive Table")
    filename = args.output_filename + ".csv"
    export_csv(rows_srs, filename)


if __name__ == '__main__':
    main()

