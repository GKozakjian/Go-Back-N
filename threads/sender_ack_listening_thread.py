import threading
import socket
import pickle
from sender.sender_node import *
import time
import random


class sender_ack_thread(threading.Thread):
    conn = socket.socket()
    sender_instance = None
    delay = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.estimate_channel_delay()
        self._stop_event = threading.Event()

    def stop_t(self):
        self._stop_event.set()

    def estimate_channel_delay(self):
        self.delay = random.randint(3, 7)
        print(" 1- Sender Estimating Channel Delay: ")
        print("          + Sender: Channel Delay is: " + str(self.delay))

    def set_ack_receiver_connection(self, tcp_connection):
        self.conn = tcp_connection

    def set_sender_instance(self, sender_instance):
        self.sender_instance = sender_instance

    def run(self):
        while not self._stop_event.is_set():
            # if transmission over, stop ack thread

            if not self._stop_event.is_set():
                received_data = self.conn.recv(1024)
                ack_packet = pickle.loads(received_data)

            if not self._stop_event.is_set() and ack_packet['next_to_send'] == self.sender_instance.base_window_sn + 1:
                self.sender_instance.receive_timer = time.time() + random.randint(1, 4)
                print("          + Sender (ACK) at [" +time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.sender_instance.receive_timer)) +"]: " + str(ack_packet))
                if self.sender_instance.receive_timer - self.sender_instance.send_timer < self.delay:
                    self.increment_sequence_number()
                    self.sender_instance.index = ack_packet['next_to_send']
                    self.sender_instance.receiver_late_ack = False
                else:
                    print(self.sender_instance.receive_timer - self.sender_instance.send_timer)

                    self.sender_instance.next_window_sn = self.sender_instance.base_window_sn
                    self.sender_instance.receiver_late_ack = True
                    self.sender_instance.index = ack_packet['data_index']
            else:
                self.sender_instance.next_window_sn = self.sender_instance.base_window_sn
        while True:
            print("stopped")
            time.sleep(60)


    def increment_sequence_number(self):
        self.sender_instance.base_window_sn += 1
        self.sender_instance.base_window_sn = (self.sender_instance.base_window_sn) % self.sender_instance.sender_window_size
