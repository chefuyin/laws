# encoding:utf-8
import os
import threading

threading.Thread(target= os.system("python court.py"))
threading.Thread(target= os.system("python tax.py"))