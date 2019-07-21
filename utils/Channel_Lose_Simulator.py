import threading
import sys
import time
from threads import receiver_node_per_connection_thread


def main():
    while True:
        text = input("Press Any Key to simulate a channel lose")

        # stop the receiver from sending ACK, to simulate failure
        receiver_node_per_connection_thread.channel_lost()
        time.sleep(2)

        # resume the receiver to send ACKs
        receiver_node_per_connection_thread.channel_lost()
        print(text)


if __name__ == "__main__":
    main()
