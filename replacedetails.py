import os
import sys
filepath = os.getcwd() + "/config.py"
file = open(filepath, "r")
f = file.read()
file.close()
f = f.replace("REPLACEME", sys.argv[1] + ":" + sys.argv[2] + "@localhost")
file = open(filepath, "w+")
file.write(f)
file.close()
