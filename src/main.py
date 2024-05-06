import sched
import time
import api_wrapper

def repeat_task():
    api_wrapper.start("Lünen")
    scheduler.enter(3, 1, repeat_task)


api_wrapper = api_wrapper.Api_wrapper()

scheduler = sched.scheduler(time.time, time.sleep)
repeat_task()
scheduler.run()