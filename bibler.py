#!/usr/bin/python3
#
# A very simlpe command line tool to parse bibtex files and launch
# link items in a PDF viewer or web browser.
# 

import bibtexparser
import argparse
import subprocess
import os.path
import re
import requests
import sys 


PDF_VIEWER = "evince"
WEB_VIEWER = "google-chrome"
DEFAULT_BIBTEX_FILE = "/home/ms/git/work_latex/library.bib"


def parse_bibtex(bibfile):
    with open(bibfile, 'r') as bibtex_file:
        db = bibtexparser.load(bibtex_file)
        return db.entries_dict


def launch_viewer(fname):

    if os.path.isfile(fname) == 1:
        cmd_str = PDF_VIEWER + " " + fname
    else:
        request = requests.get(fname)
        if request.status_code == 200:
            print('Opening url: ', fname)
            cmd_str = WEB_VIEWER + " " + fname
        else:
            print("'%s' is not a valid url or local file" % fname) 


    proc = subprocess.Popen([cmd_str], shell=True,
         stdin=None, stdout=None, stderr=None, close_fds=True)

    return True

def evaluate_search(ret):
    if len(ret) > 0:
        for idx, val in enumerate(ret):
            found_key = val[0]
            found_bib = val[1]
            print("(%d) {%s}:" % (idx, found_key))
            print("\t%s, [%s]" % (found_bib['title'], found_bib['author']))
            if 'link' in found_bib:
                print("\tlink: ",  found_bib['link'])

        n = int(input('\nChoose item: '))
        selected = ret[n]
        if 'link' in selected[1]:
            launch_viewer(selected[1]['link'])
        else:
            print("No link in the selected bibtex item")
    else:
        print("No match ...")


def search_key(dictionary, substr):
    result = []
    for key in dictionary:
        str_match = '.*' + substr + '.*'
        m = re.match(str_match, key, re.IGNORECASE)
        if m:
            result.append((key, dictionary[key]))   
    return result


def search_generic(dictionary, bib_item, substr):
    result = []
    for key in dictionary:
        value = dictionary[key]
        str_match = '.*' + substr + '.*'
        m = re.match(str_match, value[bib_item], re.IGNORECASE)
        if m:
            result.append((key, dictionary[key]))   
    return result


parser = argparse.ArgumentParser()
parser.add_argument('-f', '-file', nargs=1, help="input bibtex file")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-k', '-key', nargs=1, help="search for bibtex key")
group.add_argument('-a', '-author', nargs=1, help="search for author")
group.add_argument('-t', '-title', nargs=1, help="search for title")
args = parser.parse_args()

if args.f == None:
    bibfile = DEFAULT_BIBTEX_FILE
else:
    bibfile = args.f
    bibfile = args.f[0]

if os.path.isfile(bibfile) == 0:
    print("Bibtex file not found '%s'" % bibfile)
    sys.exit(0)
else:
    b = parse_bibtex(bibfile)


if args.k:
    key = args.k[0]
    print("\nSearching for bibtex key '%s'\n" % args.k[0])
    if key in b:
        item = b[key]
        link = item["link"]
        print("Found exact match for '%s', showing pdf: '%s'" % (key, item["link"]))
        launch_viewer(link)
    else:
        ret = search_key(b, key)
        evaluate_search(ret)

elif args.a:
    print("\nSearching for author '%s'\n" % args.a[0])
    key = args.a[0]
    ret = search_generic(b, 'author', key)
    evaluate_search(ret)
elif args.t:
    print("\nSearching for title '%s'\n" % args.t[0])
    key = args.t[0]
    ret = search_generic(b, 'title', key)
    evaluate_search(ret)

