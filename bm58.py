#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script Name: bm58.py
# Type:        Python Script
# Version:     1.0.0017
# Created:     2016-04-26
# Description: Reads data from Beurer BM-58 blood pressure meter
# Author:      Norbert Richter <norbert.richter@p-r-solution.de>
#
# Parameter:   try "bm58.py -h" for usage help
#
# Changes:
# Version      Date         Author     Modification
# ------------ ------------ ---------- ----------------------------------------
#
# Example:
#   ./bm58.py --device /dev/ttyUSB0 --memory 1 --format mysql --host localhost --db bm58 --table data --user bm58 --password password


import sys
import serial
import MySQLdb

# Internationalize
text_dic = \
{
	"en_EN": 
	{
		"Description":"Read data from 'Beurer BM-58' blood pressure meter as text, csv or into MySQL db (v1.0.0017)",
		"Epilog":"PR Solution - Norbert Richter <norbert.richter@p-r-solution.de>", 
		"SettingsGroupBM58":"BM-85 settings",
		"SettingsDeviceHelp":"Use the specific device for communication", 
		"SettingsMemoryHelp":"Memory place",
		"SettingsGroupFormat":"Output settings",
		"SettingsFormatHelp":"Output format",
		"SettingsDelimiterHelp":"CSV format delimiter",
		"SettingsDelimiterDefault":",",
		"SettingsGroupMYSQL":"MySQL database",
		"SettingsMYSQLHostHelp":"MySQL host",
		"SettingsMYSQLUserHelp":"MySQL username",
		"SettingsMYSQLPasswordHelp":"MySQL password",
		"SettingsMYSQLDBHelp":"MySQL db",
		"SettingsMYSQLTableHelp":"MySQL table",
		"ErrorPort":"ERROR: Could not open BM-58 serial port %s",
		"SelectedMemory":"Selected memory: U%d",
		"ErrorNoRespond":"Beurer BM-58 did not respond.\nConnect the BM-58 to your computer, switch it to ON, then press MEM and try again",
		"DeviceName":"Device name: %s",
		"AvailableRecords":"Available records: %d",
		"CSVHeading":"Memory;Date;Systole;Diastole;Pulse",
		"Systole":"Systole",
		"Diastole":"Diasole",
		"Pulse":"Pulse",
		"WarningNoRecord":"WARNING: not available",
		"ErrorMYSQLInsert":"ERROR: Could not insert data into database '%s'",
		"ErrorNoData":"ERROR: Only %d bytes received, 1 or 9 expected"
	},
	"de_DE":
	{
		"Description":"Daten des Beurer BM-58 Blutdruckmessgerätes auslesen (v1.0.0017)",
		"Epilog":"PR Solution - Norbert Richter <norbert.richter@p-r-solution.de>",
		"SettingsGroupBM58":"BM-85 Parameter",
		"SettingsDeviceHelp":"BM-58 Kommunikationsschnittstelle", 
		"SettingsMemoryHelp":"Speicherplatz",
		"SettingsGroupFormat":"Ausgabeparameter",
		"SettingsFormatHelp":"Ausgabeformat", 
		"SettingsDelimiterHelp":"CSV Separator",
		"SettingsDelimiterDefault":";",
		"SettingsGroupMYSQL":"MySQL Datenbank",
		"SettingsMYSQLHostHelp":"MySQL Host",
		"SettingsMYSQLUserHelp":"MySQL Benutzer",
		"SettingsMYSQLPasswordHelp":"MySQL Passwort",
		"SettingsMYSQLDBHelp":"MySQL Datenbankname",
		"SettingsMYSQLTableHelp":"MySQL Tabelle",
		"ErrorPort":"FEHLER: Konnte die BM-58 Kommunikationsschnittstelle %s nicht öffnen",
		"SelectedMemory":"Ausgewählter Speicherplatz: U%d",
		"ErrorNoRespond":"Beurer BM-58 reagiert nicht.\nBitte das BM-58 anschliessen, Schiebeschalter auf ON stellen, anschliessend MEM drücken",
		"DeviceName":"Gerätename: %s",
		"AvailableRecords":"Vorhandene Datensätze: %d",
		"CSVHeading":"Speicherplatz;Datum;Systole;Diastole;Puls",
		"Systole":"Systole",
		"Diastole":"Diasole",
		"Pulse":"Puls",
		"WarningNoRecord":"Hinweis: Datensatz nicht vporhanden",
		"ErrorMYSQLInsert":"ERROR: Could not insert data into database '%s'",
		"ErrorNoData":"FEHLER: 1 oder 9 bytes erwartet, nur %d bytes empfangen"
	}
}


if __name__ == '__main__':
	import argparse
	import locale

	try:
		lang = text_dic[locale.getdefaultlocale()[0]]
	except:
		lang = text_dic['en_EN']
		
	parser = argparse.ArgumentParser(add_help=True,
		description = lang['Description'],
		epilog = lang['Epilog']
	)

	parser.add_argument("-U", "--memory",
		choices=range(1, 3),
		dest = "memory",
		type = int,
		help = lang['SettingsMemoryHelp'],
		default = 1
	)

	serialargs = parser.add_argument_group(lang['SettingsGroupBM58'])
	serialargs.add_argument("-F", "--device",
		dest = "device",
		help = lang['SettingsDeviceHelp'],
		default = '/dev/ttyUSB0'
	)

	formatargs = parser.add_argument_group(lang['SettingsGroupFormat'])
	formatargs.add_argument("-f", "--format",
		choices = ['plain', 'print', 'csv', 'mysql'],
		dest = "format",
		help = lang['SettingsFormatHelp'],
		default = 'print'
	)

	formatargs.add_argument("--delimiter",
		dest = "delimiter",
		help = lang['SettingsDelimiterHelp'],
		default = ','
	)

	mysqlargs = parser.add_argument_group(lang['SettingsGroupMYSQL'])
	mysqlargs.add_argument("-a", "--host",
		dest = "host",
		help = lang['SettingsMYSQLHostHelp'],
		default = 'localhost'
	)
	mysqlargs.add_argument("-u", "--user",
		dest = "user",
		help = lang['SettingsMYSQLUserHelp'],
		default = 'bm58'
	)
	mysqlargs.add_argument("-p", "--password",
		dest = "password",
		help = lang['SettingsMYSQLPasswordHelp'],
		default = ''
	)
	mysqlargs.add_argument("-n", "--db",
		dest = "db",
		help = lang['SettingsMYSQLDBHelp'],
		default = 'bm58'
	)
	mysqlargs.add_argument("-t", "--table",
		dest = "table",
		help = lang['SettingsMYSQLTableHelp'],
		default = 'data'
	)

	args = parser.parse_args()

	try:
		serialport = serial.Serial(port=args.device,
			baudrate=4800,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=0.5)
	except:
		print lang['ErrorPort'] % args.device
		exit(1)

	# Send "Attention"
	serialport.write(chr(0xAA))
	response = serialport.read(1)
	if ord(response) != 0x55:
		print lang['ErrorNoRespond']
		exit(2)

	# Request Device ID
	serialport.write(chr(0xA4))
	response = serialport.read(128)
	print lang['DeviceName'] % response

	print lang['SelectedMemory'] % args.memory

	# Request number of records
	serialport.write(chr(0xA2))
	response = serialport.read(1)
	records=ord(response)
	print lang['AvailableRecords'] % records

	if args.format == 'csv':
		print lang['CSVHeading']

	db =  None
	cur = None
	if args.format == 'mysql':
		try:
			db = MySQLdb.connect(host=args.host,
								 user=args.user,
								 passwd=args.password,
								 db=args.db)
			try:
				cur = db.cursor()
			except:
				cur = None
		except:
			db = None

		if db is not None and cur is not None:
			try:
				cur.execute("CREATE TABLE IF NOT EXISTS `data` ("
							"	`memory` ENUM('1','2') NOT NULL DEFAULT '1',"
							"	`ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
							"	`systole` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,"
							"	`diastole` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,"
							"	`pulse` TINYINT(3) UNSIGNED NULL DEFAULT NULL,"
							"	PRIMARY KEY (`memory`, `ts`)"
							")")
				db.commit()
			except:
				print

	# Request records
	for i in xrange(1, records+1):
		serialport.write(chr(0xA3)+chr(i))
		response = serialport.read(9)
		if (len(response) == 9) & (response[0] == chr(0xAC)):
			if args.format == 'plain':
				print "%2d - %2002d-%02d-%02d %02d:%02d S=%3d  D=%3d  P=%d" % \
															( i
															 ,ord(response[8])
															 ,ord(response[4])
															 ,ord(response[5])
															 ,ord(response[6])
															 ,ord(response[7])
															 ,ord(response[1])+25
															 ,ord(response[2])+25
															 ,ord(response[3])
															)
			if args.format == 'print':
				print "%2d - %2002d-%02d-%02d %02d:%02d: %s %3d  %s %3d  %s %d" % \
															( i
															 ,ord(response[8])
															 ,ord(response[4])
															 ,ord(response[5])
															 ,ord(response[6])
															 ,ord(response[7])
															 ,lang['Systole'],ord(response[1])+25
															 ,lang['Diastole'],ord(response[2])+25
															 ,lang['Pulse'],ord(response[3])
															)
			if args.format == 'csv':
				print "%2d;%2002d-%02d-%02d %02d:%02d;%d;%d;%d" % \
															( i
															 ,ord(response[8])
															 ,ord(response[4])
															 ,ord(response[5])
															 ,ord(response[6])
															 ,ord(response[7])
															 ,ord(response[1])+25
															 ,ord(response[2])+25
															 ,ord(response[3])
															)
			if args.format == 'mysql':
				line="INSERT IGNORE INTO `%s` SET memory='%d', ts='20%02d-%02d-%02d %02d:%02d', systole=%d, diastole=%d, pulse=%d" % \
															( args.table,args.memory
															 ,ord(response[8])
															 ,ord(response[4])
															 ,ord(response[5])
															 ,ord(response[6])
															 ,ord(response[7])
															 ,ord(response[1])+25
															 ,ord(response[2])+25
															 ,ord(response[3])
															)
				print line+";"
				try:
					if db is not None:
						if cur is not None:
							cur.execute(line)
						db.commit()
				except:
					print lang['ErrorMYSQLInsert'] % args.db

		elif (len(response) == 1) & (response[0] == chr(0xA9)):
			print "  " + lang['WarningNoRecord']
		else:
			print "  " + lang['ErrorNoData'] % len(response)

	if db is not None:
		db.close()
