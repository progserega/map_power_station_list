#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
#import httplib
import sys
import os
import psycopg2
import psycopg2.extras
import db_config as config
import math
import tempfile

def get_node_info(node_id):
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select latitude,longitude from nodes where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id=%(node_id)d limit 1""" % {"node_id":node_id} )
		cur.execute("""select latitude,longitude from nodes where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id=%(node_id)d limit 1""" % {"node_id":node_id} )
		data = cur.fetchone()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	node={}
	node["lat"]=((float) (data[0]) )/10000000
	node["lon"]=((float) (data[1]) )/10000000
	node["id"]=node_id
	node["map_url"]="http://map.prim.drsk.ru/#map=17/%(lat)f/%(lon)f&layer=Mo&poi=Ia1" % {"lat":node["lat"], "lon":node["lon"]}
	return node

def get_node_by_way(way_id):
	node_id=-1
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select node_id from way_nodes where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id=%(way_id)d limit 1""" % {"way_id":way_id } )
		cur.execute("""select node_id from way_nodes where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id=%(way_id)d limit 1""" % {"way_id":way_id } )
		node_id=cur.fetchone()[0]
	except:
		print ("I am unable fetch data from db (41)");sys.exit(1)
	if node_id==-1:
		print ("way_id=%d not have nodes!" % way_id);sys.exit(1)
	return node_id

def get_station_as_nodes(power_stations):
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='station')) and k='name'""" )
		cur.execute("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='station')) and k='name'""" )
		# Загоняем значения в set(), преобразуя из списка, т.к. в set() будут только уникальные значения:
		nodes = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	for node in nodes:
		station={}
		station["station_name"]=node[1]
		station["node"]=get_node_info(node[0])
		# Добавляем данные о линии только если такой линии там нет (она могла быть добавлена как отношение):
		if not station["station_name"] in power_stations:
			power_stations[station["station_name"]]=station
	return power_stations

def get_station_as_ways(power_stations):
	try:
		# Берём список идентификаторов линий и наименований этих линий, которым принадлежит эта точка:
		if config.debug==True:
			print("""select way_id,v from way_tags where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id in (select way_id from way_tags where (k='power' and v='station')) and k='name'""" )
		cur.execute("""select way_id,v from way_tags where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id in (select way_id from way_tags where (k='power' and v='station')) and k='name'""" )
		ways = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	for way in ways:
		station={}
		station["way_id"]=way[0]
		station["node"]=get_node_info(get_node_by_way(way[0]))
		station["station_name"]=way[1]
		# берём первую точку в линии и по ней определяем координаты и т.п. информацию:

		# Добавляем данные о линии только если такой линии там нет (она могла быть добавлена как отношение):
		if not station["station_name"] in power_stations:
			power_stations[station["station_name"]]=station
	return power_stations


def print_text_power_stations(power_stations):
	print("---------------------------" )
	print("| way_id	|	Имя подстанции" )
	print("---------------------------" )
	for station_name in power_stations:
		station=power_stations[station_name]
	#	if len(station["way_id"]) == 0:
	#		continue
		#print("| %d | %s |" % (station["way_id"], station_name) )
		print("'%s'" % (station_name) )

def print_html_power_stations(lines):
	print("""
		<TABLE BORDER>
		<TR>    
				<TH COLSPAN=3>Текущий список подстанций, полученный из базы данных карты map.prim.drsk.ru</TH>
		</TR>
		<TR>
		<TH>№</TH>
		<TH>Наименование подстанции</TH>
		<TH>Ссылка на карту</TH>
		</TR>""")
	index=1
	for station_name in power_stations:
		station=power_stations[station_name]

		print("""<TR>
			 <TD>%(index)d</TD>
			 <TD>%(station_name)s</TD>
			 <TD><a target="_self" href="%(map_url)s">карта</a></TD>
			 </TR>""" % \
			 {"index":index, \
			 "map_url":station["node"]["map_url"], \
			 "station_name":station_name} )
		index+=1

	print("</TABLE>")



# ======================================= main() ===========================

# параметры, переданные скрипту через url:
# http://angel07.webservis.ru/perl/env.html
#param=os.getenv("QUERY_STRING_UNESCAPED")
param=os.getenv("QUERY_STRING")
#param=os.getenv("HTTP_USER_AGENT")
node_id_to_find=0

# Убираем 'n':
#if config.debug:
	#node_id_to_find=19
#	node_id_to_find=16036
#else:
#	node_id_to_find=int(param.strip("n"))


#print "Content-Type: text/html\n\n"; 
if not config.debug:
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
#print("parameters: %s, node_id_to_find=%s" % (param, node_id_to_find) )


try:
	if config.debug:
		print("connect to: dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	conn = psycopg2.connect("dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	cur = conn.cursor()
except:
    print ("I am unable to connect to the database");sys.exit(1)

power_stations={}

# Берём все Подстанции как линии:

# Добавляем простые линии, если их не добавили как отношения:
get_station_as_ways(power_stations)
get_station_as_nodes(power_stations)

# Печатаем список подстанций:
if config.debug:
	print_text_power_stations(power_stations)
else:
	print_html_power_stations(power_stations)	
sys.exit(0)
