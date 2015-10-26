# -*- coding: utf-8 -*-


#import some dope
import sys
import os
import math
import sqlite3
import datetime

def ts2dt(ts):
	 return datetime.datetime.fromtimestamp(int(ts)).strftime('%d.%m.%y, %H:%M')


#open the datebank
conn = sqlite3.connect('tumblr.db')
c = conn.cursor()


print "\nVorhandene Blogs:"
c.execute("select * from blogs order by updated desc LIMIT 0,100")
data = c.fetchall()
i=0
for blog in data:
	i += 1
	print "[%d] \033[1m%s\033[0;0m, %s" % \
		(i,blog[0],ts2dt(blog[4]))


blogID = input("\nBlog auswählen: ")
blogName = data[(blogID-1)][0]



c.execute("select directurl,timestamp,id,thumbnailurl from posts where blog='%s' and type='video' order by timestamp asc"%(blogName))
dataPosts = c.fetchall()

htmlContent = "<html><head></head><body>\n"

for post in dataPosts:
	
	uniqueID = post[0][-17:][:3].upper()
	dateString = datetime.datetime.fromtimestamp(int(post[1])).strftime('%Y-%m-%d_%H-%M')
	htmlContent += "<a href='%s'>%s_%s_%d</br><img src='%s'></a></br></br>\n"%(post[0],blogName,dateString,post[2],post[3])

htmlContent += "</html>\n"

os.system("mkdir -p dump > /dev/null 2>&1")
output = open("dump/"+blogName+".htm",'w')
output.write(htmlContent)
output.close()


# SQLite commiten und schliessen
conn.commit()
conn.close()