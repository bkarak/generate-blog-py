#!/usr/bin/env python
# encoding: utf-8
"""
blog.py - easy static blogging with python

Created by Vassilios Karakoidas on 2008-04-01.
"""

# import statements
from xml.dom import minidom
from cStringIO import StringIO
import re
import sys
import shutil

##### class definitions & functions

class RssItem:	
	def __init__(self):
		self.category = ''
		self.title = ''
		self.url = ''
		self.description = ''
		self.date = ''
		self.xml = ''
	
	def add_title(self, text):
		pat = re.compile("([^(]*)\((.*)\)")
		mo = pat.search(text)
		self.title = mo.group(1).strip()
		self.category = mo.group(2).strip()

def replace_tags(tfile, tags):
	result_html = StringIO()
	tagged_file = open(tfile, "r")
	
	for lines in tagged_file:
		try:
			l = tags[lines.strip()]
			result_html.write(l)
		except KeyError:
			result_html.write(lines)
	tagged_file.close()
	
	return result_html.getvalue()

##
# main program
##

rssItems = []
categories = []
rssFile = sys.argv[1]

# do the parsing
rssdoc = minidom.parse(rssFile)
elements = rssdoc.getElementsByTagName('item')

for node in elements:
	item = RssItem()
	for child in node.childNodes:
		if child.nodeName == 'title':
			item.add_title(child.firstChild.nodeValue)
		elif child.nodeName == 'link':
			item.url = child.firstChild.nodeValue
		elif child.nodeName == 'description':
			item.description = child.firstChild.nodeValue
		elif child.nodeName == 'pubDate':
			item.date = child.firstChild.nodeValue
	item.xml = node.toxml()
	rssItems.append(item)

# find the distincts categories
for rssItem in rssItems:
	try:
		categories.index(rssItem.category)
	except ValueError:
		categories.append(rssItem.category)

# create rss categories and write rss files
for categ in categories:
	rss_file = open("public_html/" + categ.lower() + "-rss.xml","w")
	rss_tags = {}
	rss_data = StringIO()
	for rssItem in rssItems:
		if rssItem.category == categ:
			rss_data.write(rssItem.xml)
	
	rss_tags['[[blog]]'] = rss_data.getvalue()
	rss_file.writelines(replace_tags("templates/template.rss", rss_tags))
	rss_file.close()

# copy the full rss file to public_html
shutil.copy(rssFile, "public_html/blog-rss.xml")

# open the output file
output_file = open("public_html/index.html","w")

# create the tags dictionary the categ text and the blog text
categ_text = StringIO()
blog_text = StringIO()

# fill the categ_text
categ_text.write('<ul>\n')
categ_text.write('<li><a href="public_html/blog-rss.xml">All</a></li>\n')

for categ in categories:
	categ_text.write('<li><a href="public_html/' + categ.lower() + '-rss.xml">' + categ + '</a></li>\n')

categ_text.write('</ul>\n')

# fill the blog text
for categ in categories:
	blog_text.write('<h2>' + categ + '</h2>')
	blog_text.write('<ul>')
	for rssItem in rssItems:
		if rssItem.category == categ:
			blog_text.write('<li><a href="'+ rssItem.url + '">' + rssItem.date + ' - ' + rssItem.title + '</a></li>')
	blog_text.write('</ul>')

# assign the tags
tags = {}
tags['[[rss]]'] = categ_text.getvalue()
tags['[[index]]'] = blog_text.getvalue()

output_file.writelines(replace_tags("templates/template.html", tags))

output_file.close()