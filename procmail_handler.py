import os


def getFiles(username):
	from procmail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE
	from string import Template
	ffile = Template(FORWARD_FILE).safe_substitute(username = username)	
	pmfile = Template(FORWARD_PROCMAIL_FILE).safe_substitute(username = username)	
	msgfile = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	forward = None
	procmail = None
	msg = None	
	if 	os.path.isfile(ffile):
		forward = open(ffile).read()
	if 	os.path.isfile(pmfile):
		procmail = open(pmfile).read()
	if 	os.path.isfile(msgfile):
		msg = open(msgfile).read()
	return {'forward': forward, 'procmail': procmail, 'msg': msg}



def generateFiles(username, msg, forwardTemplate, procmailTemplate):
	from procmail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE, PROCMAIL_PATH, SENDMAIL_PATH, MAIL_DIR, NEW_MAIL_FOLDER, DOMAIN_NAME
	from string import Template
	ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
	pmfilename = Template(FORWARD_PROCMAIL_FILE).safe_substitute(username = username)	
	msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	ffile = open(ffilename, "w")
	ffile.write(forwardTemplate.render(username=username, procfilepath=pmfilename, procmailPath=PROCMAIL_PATH ))
	ffile.close()
	pmfile = open(pmfilename, "w")
	pmfile.write(procmailTemplate.render(username=username, msgfilepath=msgfilename, sendmailPath=SENDMAIL_PATH, mailDir=MAIL_DIR, newMailFolder = NEW_MAIL_FOLDER, domainname=DOMAIN_NAME ))
	pmfile.close()
	msgfile= open(msgfilename, "w")
	msgfile.write(msg)
	msgfile.close()

def deleteFiles(username, keepMsg):
	from procmail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE
	from string import Template
	ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
	pmfilename = Template(FORWARD_PROCMAIL_FILE).safe_substitute(username = username)	
	msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
	if(os.path.isfile(ffilename)):
		os.remove(ffilename)
	if(os.path.isfile(pmfilename)):
		os.remove(pmfilename)
	if(not keepMsg and os.path.isfile(msgfilename)):
		os.remove(msgfilename)


