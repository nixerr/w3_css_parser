#!/usr/bin/python
# coding: utf8

__author__ = 'slashd'

import sys
import json
import requests
from bs4 import BeautifulSoup

CSS_URL = 'https://www.w3.org/Style/CSS/all-properties.en.json'
CSS_JSON = {}
URL_TAGS = {}
CSS_SCHEME = {}
CSS_NAMES = []

fwd = open('result.txt', 'w')

def get_json():
    global CSS_JSON
    CSS_JSON = json.loads(requests.get(CSS_URL).text)


def parse_url_by_tag(statuses):
    global URL_TAGS
    for css in CSS_JSON:
        url = css['url'].split('#')[0]
        if url not in URL_TAGS.keys():
            tags = []
            for css2 in CSS_JSON:
                if url in css2['url'] and css2['status'] in statuses:
                    tags.append(css2['property'])

            URL_TAGS[url] = {}
            URL_TAGS[url]['tags'] = tags
            URL_TAGS[url]['status'] = css['status']


def extract_scheme_from_tables(url, page):
    global CSS_NAMES

    print("TABLE")
    tables = page.find_all('table', {'class': 'propdef'})
    for table in tables:

        tds = table.find_all('td')
        ths = table.find_all('th')
        trs = table.find_all('tr')


        isTr = False
        if len(ths) != 0 and len(trs) != 0:
            isTr = True
            

        names = table.find_all('dfn')
        new_names = []
        if len(names) == 0:
            names = table.find_all('a', {'class': 'propdef'})

        for name in names:
            n = u"".join(name.strings).replace("'",'')
            n = n.split('#')[0]
            new_names.append(n)

        find_value = False
        value = u''
        if isTr == False:
            for td in tds:
                if find_value == True:
                    value = u"".join(td.strings)
                    value = value.replace('\n', '').replace('‘', '').replace('’','').replace("'", '')
                    break
                if 'Value' in u"".join(td.strings):
                    find_value = True
        else:
            for tr in trs:
                try:
                    th = u''.join(tr.find('th').strings)
                    if 'Value' in th:
                        value = u''.join(tr.find('td').strings)
                        value = value.replace('\n', '').replace('‘', '').replace('’','').replace("'",'')
                        break
                except:
                    print(tr)


        for name in new_names:
            # fwd.write(name.encode('utf8') + '\t' + value.encode('utf8') + '\n')
            if name in URL_TAGS[url]['tags']:

                print("  NAME   => " + name)
                print("  VALUE  => " + value)
                print("  STATUS => " + URL_TAGS[url]['status'])
                print("")
                CSS_NAMES.append(name)

                fwd.write(URL_TAGS[url]['status'] + '\t' + name + '\t' + value + '\n')


def extract_scheme_from_divs(url, page):
    global CSS_NAMES

    divs = page.find_all('div', {'class': 'propdef'})
    print("DIV:")

    for div in divs:
        new_names = []
        names = div.find_all('a', {'class': 'propdef-title'})
        # name = u"".join(name.strings).replace("'", "")
        for name in names:
            new_names.append(u''.join(name.strings).replace("'", ''))

        trs = div.find_all('tr')
        value = u''
        for tr in trs:

            find_value = False
            tds = tr.find_all('td')
            
            for td in tds:
                if find_value == True:
                    value = u''.join(td.strings)
                    value = value.replace('\n', '').replace('‘', '').replace('’','').replace("'", '')

                if 'Value' not in u''.join(td.strings):
                    continue
                else:
                    find_value = True

        # fwd.write(name.encode('utf8') + '\t' + value.encode('utf8') + '\n')
        
        for name in new_names:
            if name in URL_TAGS[url]['tags']:
                print("")
                print("  NAME   => " + name)
                print("  VALUE  => " + value)
                print("  STATUS => " + URL_TAGS[url]['status'])

                fwd.write(URL_TAGS[url]['status'] + '\t' + name + '\t' + value + '\n')

                CSS_NAMES.append(name)




def get_descrition_from_url():
    global CSS_SCHEME

    for url in URL_TAGS.keys():

        page = BeautifulSoup(requests.get(url).text.encode('utf8'), 'lxml')

        isTables = page.find('table', {'class': 'propdef'})
        isDivs = page.find('div', {'class': 'propdef'})

        if isTables != None:
            print("URL => " + url)
            extract_scheme_from_tables(url, page)

        elif isDivs != None:
            print("URL => " + url)
            extract_scheme_from_divs(url, page)

        else:
            print(url)
            print(URL_TAGS[url]['tags'])
            sys.exit(0)


        print("+++++++++++++++++++++++++++++")
            

def main(statuses):
    get_json()
    parse_url_by_tag(statuses)
    get_descrition_from_url()
    for css in CSS_JSON:
        if css['status'] in statuses and css['property'] not in CSS_NAMES:
            print(css['property'] + " not in names. URL => " + css['url'])

    for name in CSS_NAMES:
        print(name)

    print(len(CSS_NAMES))
    print(len(CSS_JSON))


if __name__ == '__main__':
    st = ['REC','NOTE','PR']
    main(st)
