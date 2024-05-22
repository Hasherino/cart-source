from statemachine import StateMachine, State
import threading
import virtual_map
from motor_controller import send_instructions, stop
from request_interface import send_audio_text

class CartStateMachine(StateMachine):
    idle = State('Idle', initial=True)
    going = State('Going')

    go = idle.to(going)
    stop = going.to(idle)

    def on_go(self, product):
        print("Transitioning to Going state")
        virtual_map.set_product(product)
        self.start_timer(product)

    def on_stop(self):
        print("Transitioning to Idle state")
        stop()
        self.stop_timer()

    def start_timer(self, product):
        def print_and_reschedule():
            print("Going to", product)
            res = send_instructions(virtual_map.path)
            if res == 1:
                send_audio_text(product + " reached!")
                self.stop()
            else:
                self.start_timer(product)

        self.timer = threading.Timer(1.0, print_and_reschedule)
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
