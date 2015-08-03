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
			from app_config import autoresponse_type
			if(autoresponse_type == "procmail"):
				from procmail_handler import getFiles
				res = getFiles(username)
				return env.get_template('mainProcmail.html').render(username=username,forward=res["forward"],procmail=res["procmail"],msg=res["msg"])
			elif(autoresponse_type == "vacation"):
				from vacation_handler import getFiles
				res = getFiles(username)
				return env.get_template('mainVacation.html').render(username=username,forward=res["forward"],msg=res["msg"])
		return open(os.path.join(rootpath,"html", "login.html"))

	@cherrypy.expose
	def generate(self, msg="I am on vacation"):
		if cherrypy.session.get("username"):
			username = cherrypy.session.get("username")
			from app_config import autoresponse_type
			if(autoresponse_type == "procmail"):
				from procmail_handler import generateFiles
				generateFiles(username, msg, env.get_template('forwardProcmail'), env.get_template('procmail'))
			elif(autoresponse_type == "vacation"):
				from vacation_handler import generateFiles
				generateFiles(username, msg, env.get_template('forwardVacation'))
		raise cherrypy.HTTPRedirect("/%s" % appcontext)

	@cherrypy.expose
	def delete(self,action):
		if cherrypy.session.get("username"):
			username = cherrypy.session.get("username")
			from app_config import autoresponse_type
			if(autoresponse_type == "procmail"):
				from procmail_handler import deleteFiles
				deleteFiles(username, action=="keep")
			elif(autoresponse_type == "vacation"):
				from vacation_handler import deleteFiles
				deleteFiles(username, action=="keep")
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
##static dir configured in apache
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

