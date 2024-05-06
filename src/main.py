import sched
import time
import api

def repeat_task():
    api_wrapper.start("Lünen")
    scheduler.enter(3, 1, repeat_task) #every 3 seconds


api_wrapper = api.Api_wrapper()

scheduler = sched.scheduler(time.time, time.sleep)
repeat_task()
scheduler