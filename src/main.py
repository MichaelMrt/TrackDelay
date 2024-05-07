import sched
import time
import api_wrapper
import os

def repeat_task():
    try:
     api_wrapper.start("Lünen")
     api_wrapper.start("Dortmund")
     api_wrapper.start("Münster")
     api_wrapper.start("Ennepetal")
    except Exception as e:
       error_log_path = os.path.join('logs','error.log')
       with open(error_log_path,'a') as error_log:
          error_log.write(str(e))
          
    scheduler.enter(10, 1, repeat_task)


api_wrapper = api_wrapper.Api_wrapper()

scheduler = sched.scheduler(time.time, time.sleep)
repeat_task()
scheduler.run()