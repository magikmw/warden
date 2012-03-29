from distutils.core import setup
import py2exe

setup(
	console=['__main__.py'],
	options={
		"py2exe":{
			"unbuffered": True,
			"optimize": 1,
			"bundle_files": 1
		}
	}
)