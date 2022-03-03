#!/usr/bin/python

from datetime import datetime
from fileinput import filename
import os
import sys
from bs4 import BeautifulSoup

files2convert = []

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

    # write .annot.md file if .md file exists ask for confirmation
    filepathmd = f'{file}.md'
    if os.path.exists(filepathmd) is True:
        print(f'file : {file}.md exists')
        overwrite = input("do you want to overwrite the existing file (y/n): ")

        if overwrite == "y":
            with open(annotfile + ".md", "w", encoding="utf-8") as output:
                output.writelines(export)
                print(f'SUCCESFULLY converted : {annotfile}')

        elif overwrite == "n":
            print(f'NOT overwritten: {file}')

        else: 
            print("wrong input, not overwriting, going to next file")  

    else:
        with open(annotfile + ".md", "w", encoding="utf-8") as output:
            output.writelines(export)
        print(f'SUCCESFULLY converted : {annotfile}')


## when file is generated check if filename ends with .md
if "\n" in filename_raw:
    files2convert = filename_raw.split('\n')
else:
    files2convert.append(filename_raw)
for file in files2convert:
    ext = file[-6:] 
    # print(f'filename = {filename_raw}')

    try:
        if not ext == ".annot":
            raise ValueError('NOT converted, no valid .ANNOT file :'+ file) 
        else:
            convertannot(file)
    except ValueError as error:
        print(error)

print("all files have been processed")