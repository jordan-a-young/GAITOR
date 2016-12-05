#!/usr/bin/env python
import lib.frame as f
import cv2
import Tkinter as tk
from lib.testGUI import GUI
import sys

# Initialize GUI
root = tk.Tk()
root.wm_title('Gaitor')
gui = GUI(root)

# Assign module to run on main loop
root.after(0, gui.update_main)

# Exiting
root.protocol('WM_DELETE_WINDOW', gui.quit)

# Begin main loop
root.mainloop()

if __name__ == '__main__':
	pass