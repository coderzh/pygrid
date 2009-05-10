from distutils.core import setup
import py2exe

setup(
	windows=[
		{
			"script" : "mainform.py",
			"icon_resources": [(1, "icon\\app.ico")]
		}],
	  options={
		  "py2exe" :
		  {
			  "includes": ["sip"],
			  "packages": ["sqlalchemy"]
		  }
	  })