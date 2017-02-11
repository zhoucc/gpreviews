#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import bs4
from bs4 import BeautifulSoup
import csv
import urllib
import urllib2
import json
import time


def getContentFromWeb(page, pkg, lang):
    url = 'https://play.google.com/store/getreviews?hl='+lang

    data = {
            'reviewType':0,
            'pageNum':page,
            'id':pkg,
            'reviewSortOrder':0,
            'xhr':1,
            }

    postdata = urllib.urlencode(data)

    request = urllib2.Request(url, postdata)

    response  = urllib2.urlopen(request)

    content = response.read()

    endIndex = -7
    if page > 9:
        endIndex = -8
    if page > 99:
        endIndex = -9

    realContent = content[18:endIndex]
    realContent = realContent.replace('\u003c', '<')
    realContent = realContent.replace('\u003d', '=')
    realContent = realContent.replace('\u003e', '>')
    realContent = realContent.replace('\u0026', '&')
    realContent = realContent.replace('\\"', '"')
    return realContent

def parseReviews(realContent):
    soup = BeautifulSoup(realContent, "html.parser")
    for child in soup.find_all(class_='single-review'):
        yield child

def parseSingleReview(review):
    try:
        author = review.find_all(class_='author-name')[0].string
        date = review.find_all(class_='review-date')[0].string
        rating = review.find_all(class_='tiny-star star-rating-non-editable-container')[0].get("aria-label").split()[1]
        body = review.find_all(class_='review-body with-review-wrapper')[0]
        title = body.find_all(class_='review-title')[0].string
        body = body.contents[2].strip()
    except:
        print review.prettify()
        sys.exit(-1)
    if author == None:
        author = ''
    if date == None:
        date = ''
    if rating == None:
        rating = ''
    if title == None:
        title = ''
    if body == None:
        body = ''
    return author, date, rating, title, body

pkgList = [
        'com.psafe.msuite',
        'com.qihoo.security',
        'com.lionmobi.powerclean',
        'com.dianxinos.optimizer.duplay',
        'com.turboc.cleaner',
        'com.powerd.cleaner',
        'com.lm.powersecurity',
        ]
lang = 'en'
for pkg in pkgList:
    for page in range(120):
        csvfile = file(pkg+'_'+lang+'_'+str(page)+'.csv', 'wb')
        csvwriter = csv.writer(csvfile)
        try:
            realContent = getContentFromWeb(page, pkg, lang)
        except:
            csvfile.close()
            break

        for review in parseReviews(realContent):
            if type(review) == bs4.element.NavigableString:
                continue
            author, date, rating , title, body = parseSingleReview(review)
            csvwriter.writerow([author.encode('utf-8'), date.encode('utf-8'), rating.encode('utf-8'), title.encode('utf-8'), body.encode('utf-8')])

        csvfile.close()
        time.sleep(10)
