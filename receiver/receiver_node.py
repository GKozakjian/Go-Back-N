from enum import Enum
import threading
from threads.receiver_node_per_connection_thread import *
import pickle
import random


class receiver_node(threading.Thread):
    local_host_ip = None
    local_host_port = None
    receiver_tcp_socket = socket.socket()
    established_tcp_connection = None
    established_tcp_connection_address = None
    timer = None

    def __init__(self, local_host_ip, local_host_port, a1, a2):
        threading.Thread.__init__(self)
        self.receiver_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_host_ip = local_host_ip
        self.local_host_port = local_host_port

    def run(self):
        self.bind_socket()

    def bind_socket(self):
        self.receiver_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver_tcp_socket.bind((self.local_host_ip, int(self.local_host_port)))
        self.start_listening()

    def start_listening(self):
        self.receiver_tcp_socket.listen(100)
        print(" 2- Receiver Starting Listener Service: ")
        print("          + Receiver: Started Listening On IP Address: "
              + self.local_host_ip
              + " And Port Number: "
              + str(self.local_host_port)
              )
        self.start_accepting()

    def start_accepting(self):
        while True:
            print(" 3- Receiver: Started Accepting New Connections: ")
            try:
                # accept new connection
                self.established_tcp_connection, self.established_tcp_connection_address = self.receiver_tcp_socket.accept()
                print("          + Receiver: Accepted New TCP Connection With Remote Host: " + str(self.established_tcp_connection_address))

                # create a new thread for the new accepted connection
                _receiver_node_per_thread = receiver_node_per_connection_thread()
                _receiver_node_per_thread.set_tcp_connection(self.established_tcp_connection)

                # perform three way handshake
                print(" 4- Sender: Starting Three Way Handshake")
                if self.start_three_way_handshake():
                    print("          + Receiver: Three Way Handshake Completed")

                    # negotiate window size for the new accepted connection and set it
                    print(" 5- Sender: Started Window Size Negotiation")
                    final_window_size = (self.negotiaite_window_size()) * 10
                    _receiver_node_per_thread.set_max_window_size(final_window_size)

                    # start the constructed receiver thread
                    _receiver_node_per_thread.start()

                # if three way handshake fails, close the connection
                else:
                    self.established_tcp_connection.close()
            except socket.error as msg:
                print("Connection Could Not Be Established because " + str(msg))

    def start_three_way_handshake(self):
        # three way handshake phase 2
            # wait for SYN from remote node
        received_data_01 = self.established_tcp_connection.recv(4096)
        three_way_handshake_data_01 = pickle.loads(received_data_01)

            # send SYNACK to finish the handshake
        if three_way_handshake_data_01['phase'] == 'SYN':
            payload = \
                {
                    "type": "handdshake",
                    "phase": "SYNACK"
                }
            three_way_handshake_data_02 = pickle.dumps(payload)
            self.established_tcp_connection.send(three_way_handshake_data_02)
        else:
            return False

        # three way handshake phase 3
            # wait for ACK to finish the handshake
        received_data_02 = self.established_tcp_connection.recv(4096)
        three_way_handshake_data_02 = pickle.loads(received_data_02)
        if three_way_handshake_data_02['phase'] == 'ACK':
            # handshake completed
            return True
        else:
            return False

    def negotiaite_window_size(self):
        # negotiate here
        received_data = self.established_tcp_connection.recv(4096)
        receiver_supported_window_sizes = pickle.loads(received_data)

        # generate window sizes
        supported_window_01 = random.randint(1, 4)
        supported_window_02 = random.randint(1, 4)
        sender_supported_window_sizes = [supported_window_01, supported_window_02]

        # print supported window sizes
        print("          + Receiver: Supported Window Sizes: " + str(sender_supported_window_sizes))

        # compare and decide on final window size
        receiver_max_supported_window_size = receiver_supported_window_sizes[0] if (receiver_supported_window_sizes[0] > receiver_supported_window_sizes[1]) else receiver_supported_window_sizes[1]
        sender_max_supported_window_size = sender_supported_window_sizes[0] if (sender_supported_window_sizes[0] > sender_supported_window_sizes[1]) else sender_supported_window_sizes[1]
        final_windoow_size = sender_max_supported_window_size if (receiver_max_supported_window_size > sender_max_supported_window_size) else receiver_max_supported_window_size

        # send final window size to sender mode
        self.established_tcp_connection.send(pickle.dumps(final_windoow_size * 10))

        # return and set final window in receiver
        return final_windoow_size


class bandwidth_supported(Enum):
    WS10 = 1
    WS20 = 2
    WS30 = 3
    WS40 = 4
