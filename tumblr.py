# -*- coding: utf-8 -*-


#import some dope
import sys
import os
import math
import json
import sqlite3
import datetime
import re


#Define some shit
apiKey = "xxxxxxxxx" 


def getBlog():
	cmd = "curl -s -L 'http://api.tumblr.com/v2/blog/%s.tumblr.com/info?api_key=%s'" % (blogName,apiKey)
	jsonCode = os.popen(cmd).read()
	jsonObject = json.loads(jsonCode)
	blog = jsonObject['response']['blog']
	return blog
	
	

def getPosts(offSet):
	cmd = "curl -s -L 'http://api.tumblr.com/v2/blog/%s.tumblr.com/posts?offset=%d&api_key=%s'" % (blogName,offSet,apiKey)
	jsonCode = os.popen(cmd).read()
	jsonObject = json.loads(jsonCode)
	posts = jsonObject['response']['posts']
	return posts

def validateKey(p,k,d):
     return p.get(k, d)


def saveVideoPost(p):
	
	id = validateKey(p,'id',None)
	blog = blogName
	type = 'video'
	timestamp = validateKey(p,'timestamp',0)
	tags = validateKey(p,'tags','')
	directurl = validateKey(p,'video_url',None)
	thumbnailurl = validateKey(p,'thumbnail_url','')
	sourceurl = validateKey(p,'source_url','')
	duration = validateKey(p,'duration',0)
	caption = validateKey(p,'caption','')
	
	if id is None or directurl is None:
		return False
	else:
		c.execute("INSERT OR IGNORE INTO posts "\
			"(id,blog,type,timestamp,tags,directurl,thumbnailurl,sourceurl,duration,caption) VALUES (?,?,?,?,?,?,?,?,?,?)",(
			id,blog,type,timestamp,str(tags),directurl,thumbnailurl,sourceurl,int(duration),caption))
		return True


def savePhotoPost(p):
	
	id = validateKey(p,'id',None)
	blog = blogName
	type = 'photo'
	timestamp = validateKey(p,'timestamp',0)
	tags = validateKey(p,'tags','')
	directurl = validateKey(p['photos'][0]['original_size'],'url',None)
	thumbnailurl = validateKey(p,'thumbnail_url','')
	sourceurl = validateKey(p,'source_url','')
	duration = 0
	caption = validateKey(p,'caption','')
	
	if id is None or directurl is None:
		return False
	else:
		c.execute("INSERT OR IGNORE INTO posts "\
			"(id,blog,type,timestamp,tags,directurl,thumbnailurl,sourceurl,duration,caption) VALUES (?,?,?,?,?,?,?,?,?,?)",(
			id,blog,type,timestamp,str(tags),directurl,thumbnailurl,sourceurl,int(duration),caption))
		return True







#der name vom blog (als subdomain)
blogName = 'pems' #falls nix angegeben, da dieser blog leer ist
blogName = raw_input("\nSubdomain vom Blog angeben: ")
blog = getBlog()
postCount = int(blog['posts'])
pageCount = int(math.ceil(postCount / 20.0))

print "Der Blog '\033[1m%s\033[0;0m.tumblr.com' enthält \033[1m%d Posts\033[0;0m auf \033[1m%d Seiten\033[0;0m."%(blogName,postCount,pageCount)

#anzahl zu ladener Seiten auslesen und ggf auf 500 (als max.) setzen
nPages = input("Wieviele Seiten sollen geladen werden? (0 = alle): ")
if(nPages == 0 or nPages > pageCount):
	nPages = pageCount
cPage = 1


#Open Database und Blog Tabelle erstellen
conn = sqlite3.connect('tumblr.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS blogs (name text primary key, title text, description text, posts integer, updated integer)")
c.execute("CREATE TABLE IF NOT EXISTS posts (id integer unique, blog text, type text, timestamp integer, tags text, directurl text, thumbnailurl text, sourceurl text, duration integer, caption text)")

#abfragen ob blog bereits in tabelle
c.execute("select updated from blogs where name='%s'"%blogName)
data = c.fetchone()
if data is None:
	#Blog noch nicht abgespeichert
	c.execute("INSERT INTO blogs (name,title,description,posts,updated) VALUES (?,?,?,?,?)",(
		str(blog['name']),
		str(re.sub(r"[^\x00-\x7F]+", " ", blog['title'])),
		str(re.sub(r"[^\x00-\x7F]+", " ", blog['description'])),
		str(blog['posts']),
		str(blog['updated'])))
#elif int(data[0])<int(blog['updated']):
	#TODO
	#print "blog hat neue einträge"
	#hier jetzt nur ein paar neue
#elif int(data[0])==int(blog['updated']):
	#TODO
	#print "bereits eingetragen"
	#hier muss nix gemacht werden



#counter initieren
cVideos = 0
cPhotos = 0


#1,2,3,4...
while cPage <= nPages:
	postsList = getPosts((cPage-1)*20)
	
	for post in postsList:
		if post['type']=='video':
			saveVideoPost(post)
			cVideos += 1
		
		if post['type']=='photo':
			savePhotoPost(post)
			cPhotos += 1
		
	
	print "Seite %d von %d gespeichert" % (cPage,nPages)
	cPage = cPage + 1
	


print "Total wurden \033[1m%d Videos\033[0;0m und \033[1m%d Fotos\033[0;0m gespeichert.\n" % (cVideos,cPhotos)

# SQLite commiten und schliessen
conn.commit()
conn.close()