import os


def getFiles(username):
	from vacation_config_paths import FORWARD_FILE, FORWARD_MSG_FILE
	from string import Template
	ffile = Template(FORWARD_FILE).safe_substitute(username = username)	
	msgfile = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	forward = None
	msg = None	
	if 	os.path.isfile(ffile):
		forward = open(ffile).read()
	if 	os.path.isfile(msgfile):
		msg = open(msgfile).read()
	return {'forward': forward, 'msg': msg}



def generateFiles(username, msg, forwardTemplate):
	from vacation_config_paths import FORWARD_FILE, FORWARD_MSG_FILE, VACATION_PATH
	from string import Template
	ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
	msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	ffile = open(ffilename, "w")
	ffile.write(forwardTemplate.render(username=username, vacationPath=VACATION_PATH ))
	ffile.close()
	msgfile= open(msgfilename, "w")
	msgfile.write(msg)
	msgfile.close()

def deleteFiles(username, keepMsg):
	from vacation_config_paths import FORWARD_FILE, FORWARD_MSG_FILE
	from string import Template
	ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
	msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	if(os.path.isfile(ffilename)):
		os.remove(ffilename)
	if(not keepMsg and os.path.isfile(msgfilename)):
		os.remove(msgfilename)


