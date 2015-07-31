import sys,os,random
from os.path import dirname
sys.path.append(dirname(__file__))

import atexit
import threading
import cherrypy

rootpath  = os.path.abspath(os.path.dirname(__file__))
#this is the default, it will try to get env var defined in apache conf file see chpy.conf.apache-example
appcontext = "chpy"

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

def authUser(user, passw):
	import ldap
	from ldap_config import SERVER_NAME, BASE_USER, USER_ATTR
	try:
		l = ldap.open(SERVER_NAME)
		l.protocol_version = ldap.VERSION3	
		username = "uid=%s,%s" % (USER_ATTR, BASE_USER)
		l.simple_bind(username, passw)
		return True
	except ldap.LDAPError, e:
		print e
		return False



from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.join(rootpath, 'templates')))



class Root(object):



	@cherrypy.expose
	def login(self, username, password):
		#TODO test parameters
		if(authUser(username, password)):
			cherrypy.session['username'] = username
			cherrypy.log("HAS USERNAME KEY %s" % str(cherrypy.session.get("username")))
			raise cherrypy.HTTPRedirect("/%s" % appcontext)
		else:
			return open(os.path.join(rootpath,"html", "login.html"))
	

	@cherrypy.expose
	def index(self):
		cherrypy.log("HAS USERNAME2 KEY %s" % str(cherrypy.session.get("username")))
		if cherrypy.session.get("username"):
			username = cherrypy.session.get("username")
			from mail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE
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
			return env.get_template('main.html').render(username=username,forward=forward,procmail=procmail,msg=msg)
		else:
			return open(os.path.join(rootpath,"html", "login.html"))

	@cherrypy.expose
	def generate(self, msg="I am on vacation"):
		if cherrypy.session.get("username"):
			username = cherrypy.session.get("username")
			from mail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE
			from string import Template
			ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
			pmfilename = Template(FORWARD_PROCMAIL_FILE).safe_substitute(username = username)	
			msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
			ffile = open(ffilename, "w")
			#TODO replace program binary path in templates
			ffile.write(env.get_template('forward').render(username=username, procfilepath=pmfilename))
			ffile.close()
			pmfile = open(pmfilename, "w")
			pmfile.write(env.get_template('procmail').render(username=username, msgfilepath=msgfilename))
			pmfile.close()
			msgfile= open(msgfilename, "w")
			msgfile.write(msg)
			msgfile.close()
		raise cherrypy.HTTPRedirect("/%s" % appcontext)

	@cherrypy.expose
	def delete(self,action):
		if cherrypy.session.get("username"):
			username = cherrypy.session.get("username")
			from mail_config_paths import FORWARD_FILE, FORWARD_PROCMAIL_FILE, FORWARD_MSG_FILE
			from string import Template
			ffilename = Template(FORWARD_FILE).safe_substitute(username = username)	
			pmfilename = Template(FORWARD_PROCMAIL_FILE).safe_substitute(username = username)	
			msgfilename = Template(FORWARD_MSG_FILE).safe_substitute(username = username)	
			if(os.path.isfile(ffilename)):
				os.remove(ffilename)
			if(os.path.isfile(pmfilename)):
				os.remove(pmfilename)
			if(action=="del" and os.path.isfile(msgfilename)):
				os.remove(msgfilename)
		raise cherrypy.HTTPRedirect("/%s" % appcontext)


	@cherrypy.expose
	def logout(self):
		cherrypy.session.clear()
		raise cherrypy.HTTPRedirect("/%s" % appcontext)

routesConf = {
		'/': {
		    'tools.sessions.on': True,
			  'tools.sessions.storage_type': "file",
    	  'tools.sessions.storage_path': os.path.join(rootpath,"sessions"),
        'tools.sessions.timeout': 600 
		    #'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
#		'/static': {
#		    'tools.staticdir.on': True,
#		    'tools.staticdir.dir': './public'
#		}
}


def application(environ, start_response):
		cherrypy.config.update({
			#'environment': 'production',
		                    'log.error_file': os.path.join(rootpath, 'log', 'site.log'),
		                    # ...
		                    })
		if 'appcontext' in environ:
			appcontext = environ["appcontext"]
			cherrypy.log("got env var appcontext")
		cherrypy.log("APPCONTEXT has value %s" % appcontext)
		cherrypy.tree.mount(Root(), script_name="/%s" % appcontext, config=routesConf)
		return cherrypy.tree(environ, start_response)

