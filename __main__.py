#!/usr/bin/env python
import lib.frame as f
import lib.video_analysis as va
import cv2
import Tkinter as tk
from lib.testGUI import GUI
import sys

# video = sys.argv[1]
# f.debug(video)

root = tk.Tk()
root.wm_title('Gaitor')
x = GUI(92, 170, 400, root)

# assign module to run on main loop
root.after(0, x.update_main)

# x.dostuff()

# begin main loop
root.mainloop()

if __name__ == '__main__':
	pass