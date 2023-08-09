# -*- mode: python; indent-tabs-mode: t; tab-width: 8 -*-
import os 
import shutil
from os import listdir
from os.path import isfile,isdir, join
import errno
import json
import logging as log
from time import sleep
from sys import exit, argv
import getopt
import tarfile

# If you have a non-standard path to your Splunk install, be sure to set
# SPLUNK_HOME
splunkPath = None

if "SPLUNK_HOME" in os.environ:
	splunkPath = os.environ["SPLUNK_HOME"]

if splunkPath is None:
	splunkPath = "/opt/splunk"
	
if "SPLUNK_DB" not in os.environ:
	os.environ["SPLUNK_DB"] = "%s/var/lib" % splunkPath

pythonPath = "%s/lib/python3.7/site-packages/" % splunkPath
import sys; sys.path.insert(0, pythonPath)
import splunk.clilib.cli_common

import requests

#######
##
## Usage: splunk cmd python app_vet.py <APP DIRECTORY>
##
## Updated Splunkbase usernames prior to running\ 
##
#######

__version__ = 1.6
__author__ = 'Splunk CPS'

# Splunkbase UserNames
import configparser
script_directory = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(f'{script_directory}/setup.conf')
username = config.get('credential', 'username')
password = config.get('credential', 'password')
#
#######

fileslog   = []
WorkingDir = os.getcwd()
VettedDir  = WorkingDir + "/Vetted"
users_dir  = WorkingDir + "/users" 
LocalOnly  = ""
IgnoreLocal = ""
BinDelete  = ""
	
#######
# Variables governing behavior set by CLI switches
LocalOnly = None
IgnoreLocal = None
PrivateApp = None
BinDelete = None
appName = None

try:
	os.mkdir(WorkingDir + "/Vetted/")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise  # raises the error again

def login(username,password):
    url = 'https://api.splunk.com/2.0/rest/login/splunk'
    try:
      http_req = requests.get(url, auth=(username,password))
      if http_req.status_code == 200: 
        json_obj = json.loads(http_req.text)
        auth_token=json_obj['data']['token']
        return(auth_token) # Return JSON Blob
      elif http_req.status_code == 401: 
        log.error('Access Denied. Check API Credentials')
        exit(0)
      else: log.info('API Connection Failure. Status code: {}'.format(http_req.status_code))
    except Exception as err:
      log.error('API Access Error: {}'.format(err))
      exit(0)

def getStatus(auth_token,appInspectGUID):
    url = 'https://appinspect.splunk.com/v1/app/validate/status/{}'.format(appInspectGUID)
    status = "PENDING"
    while status != "SUCCESS":
      sleep(2)
      try:
        headers = {'Authorization': "bearer %s" % (auth_token)}
        http_req = requests.get(url, headers=headers)
        if http_req.status_code == 200: 
          json_obj = json.loads(http_req.text)
          status=json_obj['status']
          
      except Exception as err:
        log.error('Status Access Error: {}'.format(err))
        exit(0)
    
    if 'info' not in json_obj:
    	"FAILED"
    else:
    	return(json_obj['info'])

def getReport(auth_token,appInspectGUID):
    
    appInspectStatus = getStatus(auth_token, appInspectGUID)

    url = 'https://appinspect.splunk.com/v1/app/report/{}'.format(appInspectGUID)
    
    try:
      headers = {'Content-Type': "application/json", 'Authorization': "bearer %s" % (auth_token)}
      http_req = requests.get(url, headers=headers)
      if http_req.status_code == 200: 
        json_obj = json.loads(http_req.text)
        report=json_obj['reports']
        
    except Exception as err:
      log.error('Status Access Error: {}'.format(err))
      exit(0)

    return(report[0])

def getHtmlReport(auth_token,appInspectGUID):
    
    appInspectStatus = getStatus(auth_token,appInspectGUID)
	
    url = 'https://appinspect.splunk.com/v1/app/report/{}'.format(appInspectGUID)
    
    try:
      headers = {'Content-Type': "text/html", 'Authorization': "bearer %s" % (auth_token)}
      http_req = requests.get(url, headers=headers)
      if http_req.status_code == 200: 
        report = http_req.text
        
    except Exception as err:
      log.error('Status Access Error: {}'.format(err))
      exit(0)

    return(report)

def submitApp(auth_token,appLocation):
    
    fin = open(appLocation, 'rb')
    files = {'app_package': fin}
    headers = {'Authorization': "bearer %s" % (auth_token)}

    # From the docs:
    # private_app	Identifies checks that are both cloud and self-service.
    if (PrivateApp):
      data = {'included_tags': 'private_app'}
    else:
      data = {'included_tags': 'cloud'}

    try:
      r = requests.post('https://appinspect.splunk.com/v1/app/validate', headers=headers,  data=data, files=files)
      responseJSON = json.loads(r.text)
      return (responseJSON['request_id'])
    finally:
      fin.close()

    return(0)

def packageApp(appName):
	global fileslog

	# Tar Up App
	splFile = os.getcwd() + "/"+ appName + ".spl"

	if os.path.isfile(splFile):
		os.remove(splFile)

	tar = tarfile.open(splFile, "w:")

	makeTempApp(appName,appName+"_temp")
	cleanAppConf(appName+"_temp/default/app.conf",appName)
	cleanAppMeta(appName+"_temp/metadata/default.meta",appName)

	# Clean garbage files
	for (dirpath, dirnames, filenames) in os.walk(appName+"_temp"):
		for file in filenames:
			os.chmod(os.path.join(dirpath,file), 0o0664)
			if file.startswith(".") or "default.old" in dirpath or "local.meta" in file:
				os.remove(os.path.join(dirpath,file))
				#print "Skipping %s" % (file)
			else:
				fileslog.append(os.path.join(dirpath,file))

	tar.add(appName+"_temp",appName)
	tar.close()

	return(splFile)


def getErrors(resultsJSON):
    errors = {}

    for group in resultsJSON['groups']:
      for check in group['checks']:
        if check['result'] == 'failure' or check['result'] == 'error':
          errors[check['name']] = check['description']

    return(errors)

def mergeConf(originDefault,originLocal,destination):

	local_parsed   = splunk.clilib.cli_common.readConfFile(originLocal)
	#print "%s : %s \n" % (originDefault,originLocal)
	if(os.path.isfile(originDefault)):
		default_parsed = splunk.clilib.cli_common.readConfFile(originDefault)

		merged_parsed = default_parsed
		for key, value in local_parsed.items():
			if key in default_parsed:
				for subKey, value in local_parsed[key].items():
					merged_parsed[key][subKey] = local_parsed[key][subKey]
			else:
				merged_parsed[key] = value

	else:
		merged_parsed = local_parsed
	
	splunk.clilib.cli_common.writeConfFile(destination,merged_parsed)

def cleanAppConf(conf,AppName):
	AppConf = splunk.clilib.cli_common.readConfFile(conf)
	
	if "install" in AppConf.keys():	
		if "install_source_checksum" in AppConf["install"].keys(): 
			del AppConf["install"]["install_source_checksum"]
		if "install_source_local_checksum" in AppConf["install"].keys():
			del AppConf["install"]["install_source_local_checksum"]

	if "package" in AppConf.keys():
		if not "id" in AppConf["package"].keys():
			AppConf["package"]["id"] = AppName
	else:
		AppConf["package"] = {}
		AppConf["package"]["id"] = AppName

	if not "ui" in AppConf.keys():
		AppConf["ui"] = {}
		AppConf["ui"]["label"] = AppName
	elif not "label" in AppConf["ui"].keys():
		AppConf["ui"]["label"] = AppName

	if not "launcher" in AppConf.keys():
		AppConf["launcher"] = {}
		AppConf["launcher"]["version"] = "1.0.0"
	elif not "version" in AppConf["launcher"].keys():
		AppConf["launcher"]["version"] = "1.0.0"
	elif AppConf["launcher"]["version"] == "":
		AppConf["launcher"]["version"] = "1.0.0"
		

	splunk.clilib.cli_common.writeConfFile(conf,AppConf)


##############
def cleanAppMeta(conf,AppName):
	AppConf = splunk.clilib.cli_common.readConfFile(conf)

	BadMetaKeys = [ "version", "modtime" ]
	if "app/install/install_source_checksum" in AppConf.keys():
		for k in BadMetaKeys:
			if k in AppConf["app/install/install_source_checksum"].keys():
				del AppConf["app/install/install_source_checksum"][k]
		del AppConf["app/install/install_source_checksum"]

	splunk.clilib.cli_common.writeConfFile(conf,AppConf)

##############

def makeTempApp(appLocation,tempLocation):
	
	if os.path.isdir(tempLocation):
		shutil.rmtree(tempLocation)

	# Copy the Working App InBound
	try:
		shutil.copytree(appLocation, tempLocation)
	
	# Directories are the same
	except shutil.Error as e:
		if e.errno != errno.EEXIST:
			print('Directory not copied. Error: %s %s ' % (e,e.errno))
			raise
    # Any error saying that the directory doesn't exist
	except OSError as e:
		if e.errno != errno.EEXIST:
			print('Directory not copied. Error: %s' % e)
			raise

    # Make a MetaDirectory 
	try:
		os.mkdir(tempLocation + "/metadata")
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise  # raises the error again
	
	if LocalOnly == 1:
		# Remove the /default dir from the copy no scripts will be used		
		if(os.path.isdir(tempLocation + "/default")):
			try:
				shutil.rmtree(tempLocation + "/default")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again

		# Remove the /appserver dir from the copy no scripts will be used		
		if(os.path.isdir(tempLocation + "/appserver")):
			try:
				shutil.rmtree(tempLocation + "/appserver")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again

		# Remove the /static dir from the copy no scripts will be used		
		if(os.path.isdir(tempLocation + "/static")):
			try:
				shutil.rmtree(tempLocation + "/static")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again

		# Remove the /static dir from the copy no scripts will be used		
		if(os.path.isdir(tempLocation + "/scripts")):
			try:
				shutil.rmtree(tempLocation + "/scripts")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again
	
		if(os.path.isfile(tempLocation + "/metadata/default.meta")):
			try:
				os.remove(tempLocation + "/metadata/default.meta")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again

		# Make a Default
		try:
			os.mkdir(tempLocation + "/default")
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise  # raises the error again

	# Move /local/data dir over
	# This directory does not support merging, so any duplicates 
	# will need to be overwritten from default

	if IgnoreLocal != 1:
		if(os.path.isdir(appLocation+"/local/data") and not os.path.isdir(tempLocation+"/default/data")):
			try:
				shutil.copytree(appLocation+"/local/data",tempLocation+"/default/data")
			# Directories are the same
			except shutil.Error as e:
				if e.errno != errno.EEXIST:
					print('Directory not copied. Error: %s %s ' % (e,e.errno))
					raise
				else:
					print(e.errno)

		    # Any error saying that the directory doesn't exist
			except OSError as e:
				if e.errno != errno.EEXIST:
					print('Directory not copied. Error: %s' % e)
					raise
				else:
					print(e.errno)
		else:
			for src_dir, dirs, files in os.walk(appLocation+"/local/data"):
			    dst_dir = src_dir.replace(appLocation+"/local/data", tempLocation+"/default/data", 1)
			    if not os.path.exists(dst_dir):
			        os.makedirs(dst_dir)
			    for file_ in files:
			        src_file = os.path.join(src_dir, file_)
			        dst_file = os.path.join(dst_dir, file_)
			        if os.path.exists(dst_file):
			            # in case of the src and dst are the same file
			            if os.path.samefile(src_file, dst_file):
			                continue
			            os.remove(dst_file)
			        shutil.copy(src_file, dst_dir)

	# Remove the /local dir from the copy 
	# We will use the origin app for merging to default
	try:
		shutil.rmtree(tempLocation + "/local")
		os.remove(tempLocation + "/metadata/local.meta")
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise  # raises the error again

	if BinDelete == 1:
		# Remove the /bin dir from the copy no scripts will be used		
		if(os.path.isdir(tempLocation + "/bin")):
			try:
				shutil.rmtree(tempLocation + "/bin")
			except OSError as e:
				if e.errno != errno.ENOENT:
					raise  # raises the error again

	# Clean Files From Temp Directory
	for (dirpath, dirnames, filenames) in os.walk(tempLocation):
		
		if "default.old" in dirpath:
			defaultDir = dirpath.split("/")
			try:
				shutil.rmtree(defaultDir[0] + "/" + defaultDir[1])
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise  # raises the error again

    
	if IgnoreLocal != 1:
		# Merge Files from Local 
		for (dirpath, dirnames, filenames) in os.walk(appLocation):
			for file in filenames:
				if "local" in dirpath and ".conf" in file:
					
					if "inputs.conf" in file:
						continue

					#print "Merging local %s" % (file)
					local_Config = os.path.join(dirpath,file)
					
					if LocalOnly == 1:
						default_Config = ""
					else:
						default_Config = local_Config.replace("/local/","/default/",1)

					merged_Config = tempLocation + "/default/" + file
					
					mergeConf(default_Config,local_Config,merged_Config)

				elif "local.meta" in file:
					
					#print "Merging meta %s" % (file)

					localMeta = os.path.join(dirpath,file)
					
					defaultMeta = localMeta.replace("local","default")
					merged_meta = tempLocation + "/metadata/default.meta"
					
					mergeConf(localMeta,defaultMeta,merged_meta)	

if __name__ == '__main__':
  
	#### START SCRIPT HERE
	

	try:
		opts, args = getopt.getopt(argv[1:],"dbla:p",["app="])
	except getopt.GetoptError:
		print('cps-appVet.py -p -d -b -l -a <APP>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-l':
			LocalOnly = 1
		elif opt == '-d':
			IgnoreLocal = 1
		elif opt == '-p':
                        PrivateApp = 1
		elif opt in ("-b"):
			BinDelete = 1
		elif opt in ("-a","--app"):
			appName = arg

	if appName is None:
		print('cps-appVet.py -p -d -b -l -a <APP>')
		sys.exit(2)
                
	
	auth_token = (login(username,password))

	App_To_Inspect = packageApp(appName)
	print("Packaged App: %s" % (App_To_Inspect))

	Logger  = open(os.getcwd()+"/" + appName + ".log", "w",1)
	HTMLReport  = open(os.getcwd()+"/AppInspect_Report_" + appName + ".html", "w",1)
	
	requestID = submitApp(auth_token,App_To_Inspect)
	appReport = getReport(auth_token,requestID)
	htmlReport = getHtmlReport(auth_token,requestID)

	fileListing = ""
	for filename in fileslog:
		fileListing = fileListing + "\n\t\t\t" + filename

	status = '''
		AppName: {}	
		SRC Package: {}
		Files: {}
		RequestID: {} 
		Manual Checks: {}
		Failures: {} 
		Error: {} 
		Warning: {} 
		HTML Report: {}
'''.format(appReport['app_name'],App_To_Inspect,fileListing,requestID,appReport['summary']['manual_check'],appReport['summary']['failure'],appReport['summary']['error'],appReport['summary']['warning'],os.getcwd()+"/AppInspect_Report_" + appName + ".html")

	print(status)
	HTMLReport.write(htmlReport)
	HTMLReport.flush()

	Logger.write(appName)
	Logger.write(status)
	Logger.flush()

	if appReport['summary']['manual_check'] > 0 or appReport['summary']['failure'] > 0 or  appReport['summary']['error'] > 0:
		print("\t\t****FAILED_VETTING****")
		Logger.write("\t\t****FAILED****\n")
		Logger.write("\t\tERRORS:\n")
		print("\t\tERRORS:")
	for name,message in getErrors(appReport).items():
		ErrorMessage = '''
      			Error Name: {} 
      			Description: {}
'''.format(name,message)
		print(ErrorMessage)
		Logger.write(ErrorMessage)
		Logger.flush()

		Logger.flush()
	else:
		print("\t\t****PASSED_VETTING****")
		Logger.write("PASSED")
		Logger.flush()
	print("\n")
	
	Logger.close()

