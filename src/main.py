import sched
import time
import api_wrapper
import os

def repeat_task():
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
       error_log_path = os.path.join('logs','error.log')
       with open(error_log_path,'a') as error_log:
          error_log.write(str(e)+"\n")

    scheduler.enter(30, 1, repeat_task)


api_wrapper = api_wrapper.Api_wrapper()

scheduler = sched.scheduler(time.time, time.sleep)
repeat_task()
scheduler.run()