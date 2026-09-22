import time

def execute(**args):
    time.sleep(args["seconds"])
    return args["seconds"]