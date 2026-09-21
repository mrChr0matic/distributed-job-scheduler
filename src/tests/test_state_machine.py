from base.state_machine import StateMachine
import pytest 

def test_get_states():
    sm = StateMachine()
    assert sm.get_state() == 'PENDING'
    
    sm.change_state('QUEUED')
    assert sm.get_state() == 'QUEUED'
    
    sm.change_state('RUNNING')
    assert sm.get_state() == 'RUNNING'
    
    sm.change_state('SUCCESS')
    assert sm.get_state() == 'SUCCESS'


def test_failure_retry_lifecycle():
    sm = StateMachine()

    sm.change_state("QUEUED")
    sm.change_state("RUNNING")
    sm.change_state("FAILED")
    sm.change_state("RETRY")
    sm.change_state("QUEUED")

    assert sm.get_state() == "QUEUED"
    
def test_timeout_retry_lifecycle():
    sm = StateMachine()

    sm.change_state("QUEUED")
    sm.change_state("RUNNING")
    sm.change_state("TIMEOUT")
    sm.change_state("RETRY")
    sm.change_state("QUEUED")

    assert sm.get_state() == "QUEUED"

def test_cancellation():
    sm = StateMachine()

    sm.change_state("QUEUED")
    sm.change_state("RUNNING")
    sm.change_state("CANCELLED")

    assert sm.get_state() == "CANCELLED"

def test_invalid_transition():
    sm = StateMachine()

    with pytest.raises(ValueError):
        sm.change_state("RUNNING")

    sm.change_state("QUEUED")

    with pytest.raises(ValueError):
        sm.change_state("SUCCESS")

def test_terminal_states():
    sm = StateMachine()

    sm.change_state("QUEUED")
    sm.change_state("RUNNING")
    sm.change_state("SUCCESS")

    with pytest.raises(ValueError):
        sm.change_state("RUNNING")