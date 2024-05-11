from state_controller import CartStateMachine
import time
from request_interface import send_audio_text

sm = CartStateMachine(allow_event_without_transition=True)

def process_command(command, product):
    return {
        "Go": lambda: go(product),
        "Finish": lambda: finish(),
        "Cancel": lambda: cancel()
    }.get(command)

def go(product):
    sm.go(product)
    return "Going to", product

def finish():
    sm.stop()
    return "Finishing"

def cancel():
    sm.stop()
    return "Cancelling"

def check_time(released_time):
    if time.time() - released_time > 600:
        send_audio_text("User inactive, stopping.")
        return True
    return False
