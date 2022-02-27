from datetime import datetime
import os
import sys
from bs4 import BeautifulSoup

args = sys.argv[1:]

if not args:
    print('usage: kobo_export.py filename')
    sys.exit(1)

filename = args[0]

try:
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")
except FileNotFoundError:
    print("The annotation file was not found")

identifier = soup.find('identifier').get_text()
title = soup.find('title').get_text()
author = soup.find('creator').get_text() 
annotations = soup.find_all('annotation')

# YAML metadata
metadata ="""---
title: {}
author: {} 

---
# 

""".format(title, author)

export = []
export.append(metadata)

for i, annotation in enumerate(annotations):
    progress = float(annotation.target.fragment.get('progress'))
    progresspct = "{:.5%}".format(progress)
    dateiso = annotation.date.get_text()
    datestrp = datetime.strptime(dateiso,"%Y-%m-%dT%H:%M:%S%z")
    date = datetime.date(datestrp)
    citation = annotation.target.find('text').get_text()
    export.append(f'{i}. \"{citation}\" ({date} , {progresspct}) \n\n')
    
    if annotation.content:
        note = annotation.content.find('text')
        if note:
            export.append('> ' + note.get_text() + "\n\n")

with open(filename + ".md", "w", encoding="utf-8") as output:
    output.writelines(export)