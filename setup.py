from distutils.core import setup
import py2exe
import sys
import cv2
import numpy
import Tkinter
import tkFileDialog
from lib.ROIManager import ROIManager
from lib.Manager import Manager
from lib.Tracker import Tracker
from lib.Analyzer import Analyzer

sys.argv.append('py2exe')

setup(
	windows=[r'main.py'],
	options={'py2exe': {
					'bundle_files':1,
					"dll_excludes": [
						"MSVFW32.dll",
						"AVIFIL32.dll",
						"AVICAP32.dll",
						"ADVAPI32.dll",
						"CRYPT32.dll",
						"WLDAP32.dll"]
				}
			},
	zipfile=None		
)