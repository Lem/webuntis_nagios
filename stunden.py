#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Executed in Shell with LANG=en_US.ISO-8859-15

import webuntis
import pprint
import datetime
import pickle
import sys, getopt
import urllib2

# Aufbau von Listen in einem Directory
old, new = {"ausfall": [], "vertretung": []}, {"ausfall": [], "vertretung": []}


# Jeden Aktuellen Vorfall speichern, wenn alt dann return False
def not_old(string, typ):
	global new
	global old

	# add string to new list
	new[typ].append(string)

	if string not in old[typ]:
		return True
	else:
		return False

def main(klasse, user, server, pw, school):
	global new
	global old

	klasse_file = "/tmp/webuntis_"+school+"_"+klasse+".p"

	try:
		# Alte Vorfaelle laden
		old = pickle.load(open(klasse_file,"rb"))
	except IOError:
		pass

	try:
		# Login
		s = webuntis.Session(
			username = user.decode("iso-8859-15"),
			password=pw,
			server=server,
			school=school,
			useragent='Nagios-Modul',
		).login()
	except webuntis.errors.BadCredentialsError:
		print "bad credentials"
		sys.exit(3)
	except urllib2.HTTPError, e:
		print "HTTP-ERROR: " + str(e.code) + ": " + e.reason
		sys.exit(2)

	# Automatisch heute + 2 Wocchen
	anfang = datetime.date.today()
	ende = anfang + datetime.timedelta(days=14)

	# Stundenlplan holen
	plan = s.timetable(klasse=s.klassen().filter(name=klasse)[0], start=anfang, end=ende)
	# Ein paar Variablen
	curr = {"ausfall": [], "vertretung": []}
	vertretung = 0
	ausfall = 0
	# Jedes Period-Object des Plans durchgehen
	for e in plan:

		#Ausfall
		if e.code == "irregular":
			pass
		elif e.code != None:
			txt = e.start.strftime("%d.%m. %H%M") + " " + e.subjects[0].name + "(" + e.teachers[0].name +")"

			if not_old(txt,"ausfall"):
				curr["ausfall"].append(txt)
				ausfall += 1

		# Vertretung
		elif len(e._data['te'][0]) != 1:
			txt = e.start.strftime("%d.%m. %H%M") + " " + e.subjects[0].name + " " + s.teachers().filter(id=e._data['te'][0]['orgid'])[0].name  + "->" + e.teachers[0].name
			
			if not_old(txt,"vertretung"):
				curr["vertretung"].append(txt)
				vertretung += 1

	# Ausloggen
	s.logout()

	# Ueberschreiben der alten Vorfalle mit den neuen
	pickle.dump(new, open(klasse_file, "wb" ))

	# Wenn Elemente in einer der Listen
	if vertretung > 0 or ausfall > 0:
		# Wass ist alles passiert
		if ausfall > 0:
			print  "Ausf. " + ' '.join(curr["ausfall"]),

		if vertretung > 0:
			print "Vertr. " + ' '.join(curr["vertretung"]),

		print '\b|ausfall=' + str(ausfall) + ',vertretung=' + str(vertretung)
		sys.exit(2)
	elif vertretung == 0 and ausfall == 0:
		# Alles ok :D
		print 'OK' + '|ausfall=' + str(ausfall) + ',vertretung=' + str(vertretung)
		sys.exit(0)
	else:
		# Sollte nicht passieren...
		print 'UNKNOWN :('
		sys.exit(3)

if __name__ == "__main__":
	klasse = user = server = pw = school = None

	try:
		opts, args = getopt.getopt(sys.argv[1:], "k:u:s:p:n:")
	except getopt.GetoptError as err:
		print err
		sys.exit(3)

	for o, a in opts:
		# Option ohne Wert?
		if not a: 
			print "Bitte "+ o +" angeben!"
			sys.exit(3)

		if o == "-k":
			klasse = a
		elif o == "-u":
			user = a
		elif o == "-s":
			server = a
		elif o == "-p":
			pw = a
		elif o == "-n":
			school = a

	# Eine benoetigte Option ohne Wert?
	if any (None == s for s in [klasse, user, server, pw, school]):
		print "Ein Argument fehlt!"
		sys.exit(3)

	main(klasse, user, server, pw, school)
