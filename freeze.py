""" 
 @file
 @brief cx_Freeze script to build OpenShot package with dependencies (for Mac and Windows)
 @author Jonathan Thomas <jonathan@openshot.org>
 
 @section LICENSE
 
 Copyright (c) 2008-2014 OpenShot Studios, LLC
 (http://www.openshotstudios.com). This file is part of
 OpenShot Video Editor (http://www.openshot.org), an open-source project
 dedicated to delivering high quality video editing and animation solutions
 to the world.
 
 OpenShot Video Editor is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 OpenShot Video Editor is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with OpenShot Library.  If not, see <http://www.gnu.org/licenses/>.
 """
 
 # Syntax to build redistributable package:  python3 freeze.py build
 #
 # Troubleshooting: If you encounter an error while attempting to freeze
 # the PyQt5/uic/port_v2, remove the __init__.py in that folder. And if 
 # you are manually compiling PyQt5 on Windows, remove the -strip line
 # from the Makefile.
 #
 # Mac Syntax to Build App Bundle:
 # 1) python3 freeze.py bdist_mac --include-frameworks "/usr/local/Cellar/qt5/5.3.1/Frameworks/QtCore.framework,/usr/local/Cellar/qt5/5.3.1/Frameworks/QtGui.framework,/usr/local/Cellar/qt5/5.3.1/Frameworks/QtMultimedia.framework,/usr/local/Cellar/qt5/5.3.1/Frameworks/QtMultimediaWidgets.framework,/usr/local/Cellar/qt5/5.3.1/Frameworks/QtNetwork.framework,/usr/local/Cellar/qt5/5.3.1/Frameworks/QtWidgets.framework" --qt-menu-nib="/usr/local/Cellar/qt5/5.3.1/plugins/platforms/" --iconfile=../openshot.icns --custom-info-plist=installer/Info.plist --bundle-name="OpenShot Video Editor"
 # 2) change Contents/Info.plist to use launch-mac.sh as the Executable name
 # 3) manually fix rsvg executable: 
 #    sudo dylibbundler -od -of -b -x ~/apps/rsvg/rsvg-convert -d ./rsvg-libs/ -p @executable_path/rsvg-libs/


import glob, os, sys, subprocess, fnmatch
from cx_Freeze import setup, Executable

# Determine which JSON library is installed
json_library = None
try:
    import json
    json_library = "json"
except ImportError:
    import simplejson as json
    json_library = "simplejson"
    
# Determine absolute PATH of OpenShot folder
PATH = os.path.dirname( os.path.realpath( __file__) ) # Primary openshot folder

# Find files matching patterns
def find_files(directory, patterns):
	""" Recursively find all files in a folder tree """ 
	for root, dirs, files in os.walk(directory):
		for basename in files:
			for pattern in patterns:
				if fnmatch.fnmatch(basename, pattern):
					filename = os.path.join(root, basename)
					yield filename

# GUI applications require a different base on Windows
base = None
src_files = []
external_so_files = []

if sys.platform == "win32":
    base = "Win32GUI"
    external_so_files = []
    
elif sys.platform == "linux":
	# Find all related SO files
	for filename in find_files('/usr/local/lib/', ['*openshot*.so*']):
		if "python" not in filename:
			external_so_files.append((filename, filename.replace('/usr/local/lib/', '')))
            
elif sys.platform == "darwin":
	# Copy required ImageMagick files
	for filename in find_files('/usr/local/Cellar/imagemagick/6.8.9-5/lib/ImageMagick/', ['*']):
		external_so_files.append((filename, filename.replace('/usr/local/Cellar/imagemagick/6.8.9-5/lib/', '')))
	for filename in find_files('/usr/local/Cellar/imagemagick/6.8.9-5/etc/ImageMagick-6/', ['*']):
		external_so_files.append((filename, filename.replace('/usr/local/Cellar/imagemagick/6.8.9-5/etc/ImageMagick-6/', 'ImageMagick/etc/configuration/')))
	for filename in find_files('/Users/jonathan/apps/rsvg/', ['*']):
		external_so_files.append((filename, filename.replace('/Users/jonathan/apps/rsvg/', '')))
		
	# Copy openshot.py Python bindings
	src_files.append(("/usr/local/lib/python3.3/site-packages/openshot.py", "openshot.py"))
	src_files.append((os.path.join(PATH, 'installer', 'launch-mac.sh'), "launch-mac.sh"))



# Get list of all Python files
for filename in find_files('src', ['*.py','*.settings','*.project','*.svg','*.png','*.ui','*.blend','*.html','*.css','*.js','*.xml']):
	src_files.append((filename, filename.replace('src/', '').replace('src\\', '')))

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = { "packages" : ["os", "sys", "PyQt5", "openshot", "time", "uuid", "shutil", "threading", "subprocess", "re", "math", "subprocess", "xml", "urllib", "webbrowser", json_library],
					  "include_files" : src_files + external_so_files  }

# Create distutils setup object
setup(  name = "OpenShot Video Editor",
		version = "2.0",
		description = "Non-Linear Video Editor for Linux, Windows, and Mac",
		options = {"build_exe": build_exe_options },
		executables = [Executable("src/launch.py", base=base)])
	