# Go-Back-N

## Introduction
The transport layer is responsible for end-to-end packet delivery between two nodes, over a communication medium. At first one might think that packet delivery is trivial and nothing wrong can go with it—machine A just puts the packet on the communication channel, and machine B just takes them off. Unfortunately, communication channels in real life are not ideal, and they make error occasionally. Also, they have a finite bandwidth, and propagation delay, which contribute negatively on designing efficient data transmission channels.
Hence, transmissions are prone to errors, and realistic systems need to be designed with the consideration that errors may occur, and may have drastic effects on the transmitted information. Hence, `error detection` and `correction schemes` need to be integrated in transmission systems from day one of their design (also known as error control schemes or methods).


Also, since the rate at which the receiver can process received data frames is much slower than the rate of transmission, due to the fact that it has to check and process each frame for errors, and send an acknowledgment or not. For this reason, each receiver has to have a buffer to store incoming data until they are processed. However, if the buffer begins to fill up, the sender must be notified to slow down or halt transmissions. The methods or techniques used to restrict the amount of data that a sender can send before waiting for acknowledgment is known as `flow control`.


Hence, at the data link or transport layer, flow control and error control need to be combined to achieve efficient delivery of data from one node to another. There are three protocols to achieve both techniques, which are subset of ARQ: `(1) stop-and-wait ARQ`, `(2) Go-Back-N ARQ`, `(3) Selective Repeat ARQ`. 


## Implementation& Code
This implementation tries to simulate the Go-Back-N ARQ protocol with individual acknowledgments with timouts. It also tires to mimic a shared packet-switched communication medium, that is prone to errors, and tries to recover from them by re-transmitting the corrupted packets. this simple Go-back-N implementation also threads and TCP sockets to carry out the conversation between two nodes. 

The Code is written in Python, and includes a good documentation to build on, or translate to other programming languages.


## Read More about it
Please read more in the "Report" directory.


## Developers 
George Kozakjian
