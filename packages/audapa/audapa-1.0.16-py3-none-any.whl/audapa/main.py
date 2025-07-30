import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from . import loop
from . import sets
from . import play
from . import drawscroll
from . import r_offset
from . import bar
from . import forms
from . import info

def main():
	if len(sys.argv)>1:
		if sys.argv[1]=="--remove-config":
			cleanup()
			return
		sys.stdout.write("ENTRY_DEBUG marker\n")
		sys.stdout.flush()
	sets.init()
	win = Gtk.Window()
	win.set_default_size(int(sets.default_width.get_text()),int(sets.default_height.get_text()))
	if sets.maximize.get_active():
		win.maximize()
	if sets.decorated.get_active()==False:
		win.set_decorated(False)
	else:
		win.connect('close-request', quit)
	win.show()
	#while loop.n:
	play.init()
	drawscroll.init()
	box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	combo=[win,box]
	box.append(bar.init(combo))
	box.append(drawscroll.win)
	box.append(forms.init(combo))
	box.append(r_offset.init())
	win.set_child(box)
	info.win=win
	info.box=box
	loop.main.run()
def quit(win):
	loop.stop()

import os
import sys

def cleanup_dir(d):
	if os.path.isdir(d):
		return d
	return None
def cleanup_base(a):
	basepath=os.path.dirname(a)
	basepathname=os.path.basename(basepath)
	if basepathname[0]=='.' or basepathname==sets.pkgname:
		print(basepath)
		return (basepath,None)
	return (None,basepath)
def cleanup_dir_rm(d,dd,ddd):
	e=" is not empty."
	if len(os.listdir(path=d))==0:
		os.rmdir(d)   #OSError if not empty, the check was already
		r=" removed"
		print(d.__str__()+r)
		if dd:
			if len(os.listdir(path=dd))==0:
				os.rmdir(dd)
				print(dd.__str__()+r)
				if ddd:
					if len(os.listdir(path=ddd))==0:
						os.rmdir(ddd)
						print(ddd.__str__()+r)
					else:
						print(ddd.__str__()+e)
			else:
				print(dd.__str__()+e)
	else:
		print(d.__str__()+e)
def cleanup():
	#remove config and exit
	c=cleanup_dir(sets.get_config_dir())
	if c:
		f=sets.get_config_file()
		if not os.path.isfile(f):
			f=None
	p=cleanup_dir(sets.get_data_dir())
	if c or p:
		print("Would remove(dirs only if empty):");
		if c:
			if f:
				print(f)
			print(c)
			cc,ccc=cleanup_base(c)
		if p:
			print(p)
			pp,paux=cleanup_base(p)
			if pp==None:
				ppp=os.path.dirname(paux)
				if (os.path.basename(ppp))[0]=='.': #.local/share/audapa
					pp=paux
					print(pp)
					print(ppp)
			else:
				ppp=None
		print("yes ?");
		str = ""
		while True:
			x = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
			if x == '\n':
				break
			str += x
		if str=="yes":
			if c:
				if f:
					os.remove(f)
					print(f+" removed")
				cleanup_dir_rm(c,cc,None)
			if p:
				cleanup_dir_rm(p,pp,ppp)
		else:
			print("expecting \"yes\"")

if __name__ == "__main__":
    main()
