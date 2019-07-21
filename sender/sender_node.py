from threads.sender_ack_listening_thread import *
from enum import Enum
import threading
import random
import pickle
import time


class sender_node(threading.Thread):
    base_window_sn = 0
    next_window_sn = 0
    sender_window_size = None
    request_number = 0
    remote_host_ip = None
    remote_host_port = None
    sender_tcp_socket = socket.socket()
    ack_receiver_thread_01 = sender_ack_thread()
    send_timer = None
    receive_timer = None
    receiver_late_ack = False
    BUFFER_Size = None
    FILE_NAME = None
    file_to_be_transferred = None
    buffered_file = None
    buffered_file_array = []
    file_iterator_index = 0
    index = 0
    sender_stopped = False

    def __init__(self):

        self.BUFFER_Size = 1024
        self.FILE_NAME = "Files/test.txt"
        pass

    def __init__(self, remote_host_ip, remote_host_port, a1):
        threading.Thread.__init__(self)
        self.sender_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote_host_ip = remote_host_ip
        self.remote_host_port = remote_host_port
        self.sender_base_window_sn = 0
        self.sender_max_window_sn = 0
        self.FILE_NAME = "Files/test.txt"
        self.BUFFER_Size

    def run(self):
        self.start_connection()

    def start_connection(self):
        try:
            # initiate connect  to the receiver
            self.sender_tcp_socket.connect((self.remote_host_ip, int(self.remote_host_port)))

            # perform three way handshake
            if self.start_three_way_handshake():
                print("          + Sender: Three Way Handshake Completed")
                self.negotiaite_window_size()
            # if three way handshake fails, close the connection
            else:
                self.sender_tcp_socket.close()
        except:
            print("Could Not Establiish Connection To Receiver Node")

    def start_three_way_handshake(self):
        # three way handshake phase 1
            # send the SYN packet to initialize the handshake
        payload = \
            {
                "type": "handdshake",
                "phase": "SYN"
            }
        three_way_handshake_data_01 = pickle.dumps(payload)
        self.sender_tcp_socket.send(three_way_handshake_data_01)

        # three way handshake phase 2
            # wait for SYNACK from remote node
        received_data = self.sender_tcp_socket.recv(4096)
        three_way_handshake_data_02 = pickle.loads(received_data)

        # send final ACK to finish the handshake
        if three_way_handshake_data_02['phase'] == 'SYNACK':
            payload = \
                {
                    "type": "handdshake",
                    "phase": "ACK"
                }
            three_way_handshake_data_03 = pickle.dumps(payload)
            self.sender_tcp_socket.send(three_way_handshake_data_03)
        else:
            return False

        # handshake completed
        return True

    def negotiaite_window_size(self):
        #negotiate here
        supported_window_01 = random.randint(1, 4)
        supported_window_02 = random.randint(1, 4)
        supported_window = [supported_window_01, supported_window_02]
        print("          + Sender: Supported Window Sizes: " + str(supported_window))

        send_data = pickle.dumps(supported_window)

        self.sender_tcp_socket.send(send_data)
        received_data = self.sender_tcp_socket.recv(1024)
        final_window_size = pickle.loads(received_data)
        print("          + Sender: Window Size Negotiated: " + str(final_window_size))

        # #set window size for receiver
        self.sender_window_size = final_window_size

        #start the session
        self.ack_receiver_thread_01.set_sender_instance(self)
        self.ack_receiver_thread_01.set_ack_receiver_connection(self.sender_tcp_socket)
        self.ack_receiver_thread_01.start()

        # start sending data
        print(" 6- Data Communication Started Between The Two Nodes")
        self.start_sender()

    def start_sender(self):

        # get the data from higher layer (reads file and loads into array to start transmitting)
        self.get_data_from_application_layer()

        # start transfering the file
        while self.file_iterator_index < len(self.buffered_file_array):
            # if late ACK, inform receiver to reset expected sequence number
            if self.receiver_late_ack:
                print(self.receiver_late_ack)
                self.file_iterator_index = self.index
                # get previous packet
                payload =\
                    {
                        "type": "data",
                        "is_repeated": True,
                        "message": chr(self.buffered_file_array[self.file_iterator_index]),
                        "sn": self.next_window_sn,
                        "has_next": True,
                        "data_index": self.file_iterator_index
                    }

                self.increment_sequence_number()
                self.send_timer = time.time()
                # send the data
                self.sender_tcp_socket.send(pickle.dumps(payload))

                # print out the packet information
                print("          + sender (new packet) at [" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.send_timer)) + "]:" + str(payload))

            # if normal ACK, send normal packet
            else:
               # construct payload
                payload =\
                    {
                        "type": "data",
                        "is_repeated": False,
                        "message": chr(self.buffered_file_array[self.file_iterator_index]),
                        "sn": self.next_window_sn,
                        "has_next": True,
                        "data_index": self.file_iterator_index
                    }
                self.increment_sequence_number()
                self.send_timer = time.time()
                # send the data
                self.sender_tcp_socket.send(pickle.dumps(payload))

                # print out the packet information
                print("          + sender (new packet) at [" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.send_timer)) + "]:" + str(payload))
                self.file_iterator_index +=1

            # sleep so that the communication speed is not very fast
            time.sleep(1)

        # notify receiver that file transport is over
            # terminate the receive ACK thread
        self.ack_receiver_thread_01.stop_t()

        fin_payload =\
            {
                "type": "operation",
                "message": "",
                "is_repeated": False,
                "has_next": False,

            }

        self.sender_tcp_socket.send(pickle.dumps(fin_payload))
        # finished transferign data, close the session with three way handshake disconnection

        if self.start_three_way_fin_handshake():
            print(" 7- Sender: Starting Three Way Disconnect Handshake")
            print("          + Sender: Three Way Disconnect Handshake Completed")
            self.sender_tcp_socket.close()
            exit()
        else:
            self.sender_tcp_socket.close()
            exit()

    def start_three_way_fin_handshake(self):

        # three way handshake phase 1
        # send the FIN packet to initialize the handshake
        payload = \
            {
                "type": "handdshake",
                "phase": "FIN"
            }
        three_way_handshake_data_01 = pickle.dumps(payload)
        self.sender_tcp_socket.send(three_way_handshake_data_01)
        print("im here")

        # three way handshake phase 2
        # wait for SYNACK from remote node
        received_data = self.sender_tcp_socket.recv(1024)
        three_way_handshake_data_02 = pickle.loads(received_data)
        print(three_way_handshake_data_02)
        # send final ACK to finish the handshake
        if three_way_handshake_data_02['phase'] == 'FINACK':

            payload = \
                {
                    "type": "handdshake",
                    "phase": "ACK"
                }
            three_way_handshake_data_03 = pickle.dumps(payload)
            self.sender_tcp_socket.send(three_way_handshake_data_03)
        else:
            return False

        # handshake completed
        return True

    def get_data_from_application_layer(self):
        # try to open the file and read it to an array
        try:
            self.file_to_be_transferred = open(self.FILE_NAME, 'rb')
            with open(self.FILE_NAME, 'rb') as ins:
                self.buffered_file = self.file_to_be_transferred.read()
                for x in self.buffered_file:
                    self.buffered_file_array.append(x)

        except IOError as e:
            print(" >> An Error Occured While trying to open file: " + e.strerror)

    def increment_sequence_number(self):
        self.next_window_sn += 1
        self.next_window_sn = (self.next_window_sn) % self.sender_window_size


class bandwidth_supported(Enum):
    WS10 = 1
    WS20 = 2
    WS30 = 3
    WS40 = 4
