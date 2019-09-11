#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##########################################################
#  valSPIDjreg 0.4                                       #
#--------------------------------------------------------#
#   Validates SPID's new registry JSON-based entries     #
#--------------------------------------------------------#
#    GNU (GPL) 2019 Walter Arrighetti, PhD, CISSP, CCSP  #
#    coding by: Walter Arrighetti                        #
#               <walter.arrighetti@agid.gov.it>          #
#  < https://github.com/AgID/valSPIDjsonreg >  #
#                                                        #
##########################################################
import datetime
import os.path
import json
import sys
import re

SPIDregistry_URLbase = "https://registry.spid.gov.it/metadata/sp/spid-sp-"
_entities = ['ipaEntityCode','entityName','entityId','metadataUrl','metadataType','notes']

__VERSION = "0.4"


def create_secondary_registry(registry, pathname):
	mdR = registry
	mdR['dateTime'] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
	for n in range(registry['totalRecords']):
		mdR['metadata'][n]['metadataUrl'] = SPIDregistry_URLbase + mdR['metadata'][n]['ipaEntityCode'].strip() + ".xml"
	try:	mdfile = open(pathname,'w')
	except:
		print("[reg]\tUnable to create registry-entries file \"%s\"."%os.path.split(pathname)[1])
		return False
	#mdfile.write(json.dumps( {'agidSpid':mdR}, indent='\t'))
	mdfile.write(json.dumps( {'agidSpid':mdR}) )
	mdfile.close()
	return mdR


def generate_PgSQL_query(entry):
	Qbase = 'INSERT INTO "configurazioni" ("codice_entita", "entityid", "tipologia", "data_invio", "valutazione", "data_notifica_idp", "note", "url", "status") VALUES ('
	Q = []
	for n in range(entry['totalRecords']):
		Q.append( Qbase + "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"%(
			entry['metadata'][n]['ipaEntityCode'], 
			entry['metadata'][n]['entityId'], 
			"SAML", 
			entry['dateTime'][:11], 
			"CCOR", 
			entry['dateTime'][:11], 
			entry['metadata'][n]['notes'], 
			entry['metadata'][n]['metadataUrl'], 
			entry['metadata'][n]['metadataType'], 
			))
		print(Q[-1] + '\n')
	return Q


def parse_files(pathname):
	URLre = re.compile(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
	path, filename = os.path.split(pathname)
	name, ext = os.path.splitext(filename)
	namereg = name.strip() + "_registry"
	pathenamereg = os.path.join(path,namereg+ext)
	err0, errR, reg = 0, 0, True
	if ext != ".json":
		print("[***]\tOnly JSON files can be used in new registry entries")
	if not os.path.exists(pathname):
		print("[ SP]\tJSON registry-entries file does not exist (\"%s\")."%filename)
		sys.exit(9)
	elif not os.path.exists(pathenamereg):
		print("[reg]\tJSON registry-entries file does not exists (\"%s\"). It will be created."%(namereg+ext))
		reg = False
	try:	md0 = json.load(open(pathname,'r'))
	except:
		print("[ SP]\tFile \"%s\" must be a valid JSON file."%filename)
		sys.exit(9)
	if reg:
		try:	mdR = json.load(open(pathenamereg,'r'))
		except:
			print("[reg]\tFile \"%s\" must be a valid JSON file."%(namereg+ext))
			sys.exit(9)
	if list(md0.keys()) != ['agidSpid']:	print("[ SP]\tOnly 1 'agidSpid' root element allowed.");	err0+=1
	if reg and list(mdR.keys()) != ['agidSpid']:	print("[reg]\tOnly 1 'agidSpid' root element allowed.");	errR+=1
	md0 = md0['agidSpid']
	if reg:	mdR = mdR['agidSpid']
	#else:	mdR = md0
	if set(md0.keys())!=set(['dateTime','totalRecords','metadata']):	print("[ SP]\tOnly 3 elements allowed within 'agidSpid': 'dateTime', 'totalRecords' and 'metadata'.");	err0+=1
	if reg and set(mdR.keys())!=set(['dateTime','totalRecords','metadata']):	print("[reg]\tOnly 3 elements allowed within 'agidSpid': 'dateTime', 'totalRecords' and 'metadata'.");	errR+=1
	if not datetime.datetime.strptime(md0['dateTime'],"%Y-%m-%d %H:%M:%S"):	print("[ SP]\t'dateTime' must be a well-formatted date/time string.");	err0+=1
	if reg and not datetime.datetime.strptime(md0['dateTime'],"%Y-%m-%d %H:%M:%S"):	print("[reg]\t'dateTime' must be a well-formatted date/time string.");	errR+=1
	#if type(md0['totalRecords'])!=type(1):	print("[ SP]\t'totalRecords' must be an integer.");	err0+=1
	#if reg and type(mdR['totalRecords'])!=type(1):	print("[reg]\t'totalRecords' must be an integer.");	errR+=1
	num0 = int(md0['totalRecords'])
	if reg:
		numR = int(mdR['totalRecords'])
		if num0!=numR:	print("[***]\t'totalRecords' in both JSON files should match with each others (%d != %d)."%(num0,numR));	err0+=1;	errR+=1
	if num0!=len(md0['metadata']):	print("[ SP]\t'totalRecords' (%d) must match with the number of metadata entries (%d)."%(num0,len(md0['metadata'])));	err0+=1
	if reg and numR!=len(mdR['metadata']):	print("[reg]\t'totalRecords' (%d) must match with the number of metadata entries (%d)."%(numR,len(mdR['metadata'])));	errR+=1
	for n in range(num0):
		if set(md0['metadata'][n].keys())!=set(_entities):
			print("[ SP]\tMetadata entry #%d must contain the elements "%(n+1) +(','.join(_entities))+ '.');	err0+=1
		if reg and set(mdR['metadata'][n].keys())!=set(_entities):
			print("[reg]\tMetadata entry #%d must contain the elements "%(n+1) +(','.join(_entities))+ '.');	errR+=1
		for entity in _entities:
			if type(md0['metadata'][n][entity])!=type(u""):	print("[ SP]\tMetadata entry #%d's '%s' element must be a string."%(n+1,entity));	err0+=1
			if reg and type(mdR['metadata'][n][entity])!=type(u""):	print("[reg]\tMetadata entry #%d's '%s' element must be a string."%(n+1,entity));	errR+=1
			if entity != 'notes':
				if not md0['metadata'][n][entity]:	print("[ SP]\tMetadata entry #%d's '%s' element must not be empty."%(n+1,entity));	err0+=1
				if reg and not mdR['metadata'][n][entity]:	print("[reg]\tMetadata entry #%d's '%s' element must not be empty."%(n+1,entity));	errR+=1
			if entity == 'metadataUrl':
				if not URLre.match(md0['metadata'][n][entity]):
					print("[  SP]\tMetadata entry #%d's 'metadataUrl' element must be a valid https URL."%(n+1));	err0+=1
				if reg:
					if not URLre.match(mdR['metadata'][n][entity]):
						print("[reg]\tMetadata entry #%d's 'metadataUrl' element must be a valid https URL."%(n+1));	errR+=1
					if mdR['metadata'][n][entity] != SPIDregistry_URLbase+ mdR['metadata'][n]['ipaEntityCode'].strip() +".xml":
						print("[reg]\tMetadata entry #%d's 'metadataUrl' element must be an URL within the SPID registry at [registry.spid.gov.it]"%(n+1));	errR+=1
			elif reg:
				if md0['metadata'][n][entity]!=mdR['metadata'][n][entity]:
					print("[***]\tMetadata entry #%d's '%s' element in both JSON files should match with each other."%(n+1,entity));	err0+=1;	errR+=1
			if entity == 'metadataType':
				if md0['metadata'][n][entity] not in ["prod","test","to_delete"]:
					print("[ SP]\tMetadata entry #%d's 'metadataType' must be either \"prod\" or \"test\"."%(n+1));	err0+=1
				if reg and mdR['metadata'][n][entity] not in ["prod","test","to_delete"]:
					print("[reg]\tMetadata entry #%d's 'metadataType' must be either \"prod\" or \"test\"."%(n+1));	errR+=1
			if entity == 'entityId':
				if not URLre.match(md0['metadata'][n][entity]):
					print("[ SP]\tMetadata entry #%d's 'entityId' element should be a valid https URL."%(n+1))
				if reg and not URLre.match(mdR['metadata'][n][entity]):
					print("[reg]\tMetadata entry #%d's 'entityId' element should be a valid https URL."%(n+1))
	if not reg:
		mdR = create_secondary_registry(md0,pathenamereg)
		if not mdR:	errR += 1
	if err0:	print("\n%d errors on registry-entries file (with SP-based URL) \"%s\"."%(err0,filename))
	if errR:	print("\n%d errors on registry-entries file (with registry-based URL) \"%s\"."%(errR,namereg+ext))
	if err0==errR==0:	print("No errors in either JSON registry entry files !")
	if not errR:	return mdR
	else:	sys.exit(1)

def main():
	def print_args():
		print(" Syntax:  %s  SPentriesFile.json  [registryEntriesFile.json]"%os.path.basename(sys.argv[0]))
		print('\n')
		sys.exit(9)
	print("valSPIDjreg %s - Checks the validity of SPID's SP metadata JSON-based metadata files"%__VERSION)
	print("GNU (GPL) 2019 by Walter Arrighetti  <walter.arrighetti@agid.gov.it>\n")
	if len(sys.argv) != 2:	print_args()
	entries = parse_files(sys.argv[1])
	print("\nInsert new elements into the PostgreSQL internal database:\n")
	generate_PgSQL_query(entries)
	sys.exit(0)


if __name__ == "__main__": main()
