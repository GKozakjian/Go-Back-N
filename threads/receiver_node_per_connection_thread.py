import threading
import socket
import time
import pickle


class receiver_node_per_connection_thread(threading.Thread):
    receiver_tcp_socket = socket.socket()
    next_window_sn = 0
    timer = None
    receiver_max_window_size = None
    channel_lost = False

    def __init__(self):
        threading.Thread.__init__(self)

    def set_tcp_connection(self, tcp_connection):
        self.receiver_tcp_socket = tcp_connection

    def set_max_window_size(self, window_size):
        self.receiver_max_window_size = window_size
        print("          + Sender: Window Size Negotiated: " + str(self.receiver_max_window_size))

    def run(self):
        self.start_receiver()

    def start_receiver(self):

        while True:
            if not receiver_node_per_connection_thread.channel_lost:
                # Receive data sent from the sender node
                received_data = self.receiver_tcp_socket.recv(4096)
                received_packet = pickle.loads(received_data)

                # check for late ACKs
                if received_packet["is_repeated"]:
                    self.next_window_sn = received_packet['sn']

                if not received_packet["has_next"]:
                    break

                # send ACK
                if received_packet["sn"] == self.next_window_sn:
                    # Slide the receiver window
                    self.increment_sequence_number()

                    # Send ACK for received packet
                    _new_ack = \
                        {
                            'type': 'ACK',
                            'next_to_send': self.next_window_sn,
                            "data_index": received_packet['data_index']
                        }
                    self.receiver_tcp_socket.send(pickle.dumps(_new_ack))

        # finished receiving so close session with three way handhsake disconnect

        if self.start_three_way_fin_handshake():
            print("          + Receiver: Three Way Disconnect Handshake Completed")
            self.receiver_tcp_socket.close()
            exit()
        else:
            self.receiver_tcp_socket.close()
            exit()


    def increment_sequence_number(self):
        self.next_window_sn += 1
        self.next_window_sn = (self.next_window_sn) % self.receiver_max_window_size

    def start_three_way_fin_handshake(self):

        # three way handshake phase 2
        # wait for SYN from remote node
        received_data_01 = self.receiver_tcp_socket.recv(4096)
        three_way_handshake_data_01 = pickle.loads(received_data_01)

        # send SYNACK to finish the handshake
        if three_way_handshake_data_01['phase'] == 'FIN':
            payload = \
                {
                    "type": "handdshake",
                    'phase': 'FINACK'
                }
            three_way_handshake_data_02 = pickle.dumps(payload)
            self.receiver_tcp_socket.send(three_way_handshake_data_02)
            time.sleep(2)
        else:
            return False

        # three way handshake phase 3
        # wait for ACK to finish the handshake
        received_data_02 = self.receiver_tcp_socket.recv(4096)
        three_way_handshake_data_02 = pickle.loads(received_data_02)
        print(three_way_handshake_data_02)
        if three_way_handshake_data_02['phase'] == 'ACK':

            # handshake completed
            return True
        else:
            return False

    @staticmethod
    def simulate_channel_lose():
        receiver_node_per_connection_thread.channel_lost = not receiver_node_per_connection_thread.channel_lost
