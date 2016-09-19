#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import os
import time
import sys

def deg2grad_min_sec(deg):
	# Получаем целую часть:
	#grad=math.fabs(deg)
	# все способы сокращают до целого, в большую сторону, а на нам нужно именно точно:
	grad=int(("%f" % deg).split(".")[0])
	ost=deg-grad
	minutes=int(("%f" % (ost*60)).split(".")[0])
	ost=ost*60-minutes
	sec=ost*60
	return """%d°%d'%.2f" """ % (grad,minutes,sec)

stand_alone_page=True
if len(sys.argv) > 1:
	if sys.argv[1] == "noheader":
		stand_alone_page=False

if not stand_alone_page:
	print"""
<HEAD>
<STYLE TYPE="text/css">
<!--
@page { size: 21cm 29.7cm; margin: 2cm }
P { margin-bottom: 0.21cm }
-->
</STYLE>

<style>
   .normaltext {
   }
</style>
<style>
   .ele_null {
    color: red; /* Красный цвет выделения */
   }
</style>
<style>
   .selected_node {
    color: green; /* Зелёный цвет выделения */
	background: #D9FFAD;
	font-size: 150%;
   }
</style>

</HEAD>
<BODY LANG="ru-RU" LINK="#000080" VLINK="#800000" DIR="LTR">
"""
else:
	print"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
<TITLE>Список подстанций</TITLE>
<META NAME="GENERATOR" CONTENT="OpenOffice.org 3.1  (Linux)">
<META NAME="AUTHOR" CONTENT="Сергей Семёнов">
<META NAME="CREATED" CONTENT="20100319;10431100">
<META NAME="CHANGEDBY" CONTENT="Сергей Семёнов">
<META NAME="CHANGED" CONTENT="20100319;10441400">
<STYLE TYPE="text/css">
<!--
@page { size: 21cm 29.7cm; margin: 2cm }
P { margin-bottom: 0.21cm }
-->
</STYLE>

<style>
   .normaltext {
   }
</style>
<style>
   .ele_null {
    color: red; /* Красный цвет выделения */
   }
</style>
<style>
   .selected_node {
    color: green; /* Зелёный цвет выделения */
	background: #D9FFAD;
	font-size: 150%;
   }
</style>

</HEAD>
<BODY LANG="ru-RU" LINK="#000080" VLINK="#800000" DIR="LTR">
"""

station_list="/var/osm/fires/station_list.csv"
#station_list="station_list.csv"

mod_time_station=time.strftime("%d.%m.%Y %H:%M", time.localtime(os.stat(station_list).st_mtime) )

print("""
		<TABLE BORDER>
		<TR>    
				<TH COLSPAN=5>Текущий список подстанций, полученный из базы данных карты map.prim.drsk.ru в %s</TH>
		</TR>
		<TR>
		<TH>№</TH>
		<TH>Наименование подстанции</TH>
		<TH>Ссылка на карту</TH>
		<TH>Десятичные координаты</TH>
		<TH>Координаты в градусах,минутах и секундах</TH>
		</TR>""" % mod_time_station)
index=0
for line in open(station_list):
	lon,lat,name=line.split("|")
	index+=1
	print("""<TR>
		 <TD>%(index)d</TD>
		 <TD>%(name)s</TD>
		 <TD><a target="_self" href="http://map.prim.drsk.ru/#map=17/%(lat)f/%(lon)f&layer=Mo&poi=Ia1">карта</a></TD>
		 <TD>%(lat).6f, %(lon).6f</TD>
		 <TD>%(lat_grad_min_sec)s, %(lon_grad_min_sec)s</TD>
		 </TR>""" % \
		 {"index":index, \
		 "lat":float(lat), \
		 "lon":float(lon), \
		 "lat_grad_min_sec":deg2grad_min_sec(float(lat)), \
		 "lon_grad_min_sec":deg2grad_min_sec(float(lon)), \
		 "name":name} )

print("</TABLE>")

print("""
</body>
""")
if stand_alone_page:
	print("""
</html>
""")

