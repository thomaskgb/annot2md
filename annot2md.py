#!/usr/bin/python

from datetime import datetime
import os
from sqlite3 import DataError
import sys
from bs4 import BeautifulSoup

args = sys.argv[1:]

if not args:
    print('usage: annot2md.py filename or file list')
    sys.exit(1)
filename_raw = args[0]


def convertannot(annotfile):
    try:
        with open(annotfile, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml-xml")        
        # check if annotations are empty
        try:
            annotations = soup.find_all('annotation')
            if not annotations:
                raise ValueError(annotfile + ' NOT CONVERTED -> has empty annotations')

        except ValueError as error:
            print(error)
            return

    except FileNotFoundError:
        print("The annotation file was not found")

    identifier = soup.find('identifier').get_text()
    title = soup.find('title').get_text()
    author = soup.find('creator').get_text() 


    # YAML metadata
    metadata = (f'---\n' +
    f'tags: [auto]\n' +
    f'type: book_annotation\n' +
    f"title: '{title}'\n" +
    f'author: {author}\n' +
    f'ISBN: {identifier}\n' +
    f'---\n')
    
    title_block = (f'# {title} - {author}\n\n' +
    f'## Annotations\n\n')

    export = []
    export.append(metadata)
    export.append(title_block)

    for i, annotation in enumerate(annotations):
        progress = float(annotation.target.fragment.get('progress'))
        # convert float progress to % symbol with 5 trailing digits
        progresspct = "{:.5%}".format(progress)
        dateiso = annotation.date.get_text()

        # convert date to human readable
        datestrp = datetime.strptime(dateiso,"%Y-%m-%dT%H:%M:%S%z")
        date = datetime.date(datestrp)
        citation_raw = annotation.target.find('text').get_text()
        
        # remove whitespace and enters
        citation = " ".join(citation_raw.split()) 
        export.append(f'{i}. \"{citation}\" \n({date} , {progresspct}) \n\n')
        
        # read content and append note as comment
        if annotation.content:
            note = annotation.content.find('text')
            if note:
                export.append('> ' + note.get_text() + "\n\n")

    with open(annotfile + ".md", "w", encoding="utf-8") as output:
        output.writelines(export)

# check if its an fzf list
if "\n" in filename_raw:
    filename = filename_raw.split('\n')
    # print(f'filename = {filename}')
    for file in filename:
        convertannot(file)

# file ="Sönke Ahrensx - How to Take Smart Notes_ One Simple Technique to Boost Writing, Learning and Thinking – for Students, Academics and Nonfiction Book Writers-CreateSpace Independent Publishing Platform (.epub.annot"
# convertannot(file)