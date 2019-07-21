from receiver.receiver_node import *
from sender.sender_node import *
import time
import sys
from utils import Channel_Lose_Simulator


def main(argv1_file, argv2_cong_prob, argv3_pack_prob):
    #create the receiver node and start it
    receiver_node_01 = receiver_node("localhost", 22222, argv2_cong_prob, argv3_pack_prob)
    receiver_node_01.start()
    time.sleep(2)

    #create the sender node and start it
    sender_node_01 = sender_node("localhost", 22222, argv1_file)
    sender_node_01.start()


    #join the threads, so that the main does not exit
    receiver_node_01.join()
    sender_node_01.join()


    #finish execution when both child threads join
    exit()


# simulator starting point
    # take the arguments, and initialize the nodes
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

