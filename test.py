import threading
import time
import random
import logging
import sys

taskQueue = ["Run", "Walk", "Talk", "Fight", "Live"]
taskToBeAdded = iter(["Jump", "Talk", "Fight"])
task = ""
status = True
iterating = False

def performTask():
    iterating = True
    for pTask in list(taskQueue):
        task = pTask
        taskPeriod = 1
        print("Performing Task: {}".format(task))
        time.sleep(taskPeriod)
        taskQueue.remove(pTask)
        print(taskQueue)
    iterating = False

i = 0
taskThread = threading.Thread(target=performTask)

while True:
    threadAlive = taskThread.is_alive()
    print("taskThread: {}".format(threadAlive))
    if (status and not threadAlive):
        i += 1
        print(i)
        taskThread.start()
        status = False
        print("Is Iterating {}".format(iterating))

    
    taskAdd = next(taskToBeAdded, '-1')
    if (taskAdd == '-1'):
        continue
    else:
        status = True
    print("\n" + taskAdd)
    taskQueue.append(taskAdd)
    time.sleep(1)
