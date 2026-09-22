attempts = 0

def execute(**inputs):
    global attempts
    attempts += 1

    if attempts == 1:
        raise RuntimeError("intentional first failure")

    return inputs["value"] * 2