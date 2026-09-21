VALID_TRANSITIONS = {
    "PENDING" : ["QUEUED"],
    "QUEUED" : ["RUNNING"],
    "RUNNING" : ["SUCCESS", "FAILED", "CANCELLED", "TIMEOUT"],
    "TIMEOUT" : ["RETRY"],
    "FAILED" : ["RETRY"],
    "RETRY" : ["QUEUED"],
    "SUCCESS" : [],
    "CANCELLED" : [],
}

class StateMachine:
    def __init__(self):
        self.state = "PENDING"
    def change_state(self, next_state):
        if next_state not in VALID_TRANSITIONS[self.state]:
            raise ValueError(f"Invalid state transition requested {self.state} -> {next_state}")
        self.state = next_state
    def get_state(self):
        return self.state