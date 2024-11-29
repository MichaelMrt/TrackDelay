import api_wrapper
import os
import traceback

# Paths to script
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, "..", "src", "main.py")
log_path = os.path.join(script_dir, "..","logs")
error_log_path = os.path.join(log_path, "error.log")

if not os.path.exists(log_path):
   os.makedirs(log_path)


api_wrapper = api_wrapper.Api_wrapper()

try:
   api_wrapper.start("Bonn")
   api_wrapper.start("Köln")
   api_wrapper.start("Münster")
   api_wrapper.start("Düsseldorf Hbf")
   api_wrapper.start("Duisburg")
   api_wrapper.start("Essen")
   api_wrapper.start("Wuppertal")
   api_wrapper.start("Bochum")
   api_wrapper.start("Berlin Hbf")
   api_wrapper.start("Lünen")
   api_wrapper.start("Ennepetal") 
except Exception as e:
   with open(error_log_path,'a') as error_log:
          print("ERROR")
          error_log.write("ERROR:\n")
          traceback.print_exc(file=error_log)
