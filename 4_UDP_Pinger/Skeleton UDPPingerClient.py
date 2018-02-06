# This skeleton is valid for both Python 2.7 and Python 3.
# You should be aware of your additional code for compatibility of the Python version of your choice.

from socket import *
import time
from sys import argv

# Get the server hostname and port as command line arguments
address = (argv[1],int(argv[2]))
host = address[0]
port = address[1]
timeout = 1 # in seconds
 
# Create UDP client socket
# FILL IN START		
clientSocket = socket(AF_INET,SOCK_DGRAM)
# Note the second parameter is NOT SOCK_STREAM
# but the corresponding to UDP

# Set socket timeout as 1 second
clientSocket.settimeout(timeout)

# FILL IN END

# Sequence number of the ping message
ptime = 0  

# Ping for 10 times
while ptime < 10: 
    ptime += 1
    # Format the message to be sent as in the Lab description
    ntime = time.asctime()
    s = "Ping " + str(ptime) + " " + str(ntime)
    data = s.encode()

    try:
        # FILL IN START
        # Record the "sent time"
        sent_time = time.time()

        # Send the UDP packet with the ping message
        print("Sending UDP Packet")
        print("SENT DATA: ",data.decode())
        clientSocket.sendto(data,(host,port))

        # Receive the server response
        print("Recv Response")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

        # Record the "received time"
        recv_time = time.time()

        # Display the server response as an output
        print("RESPONSEMESSAGE: ",modifiedMessage.decode())
        print("SERVERADRESS: ",serverAddress[0])
        print("SERVERPORT: ",serverAddress[1])

        # Round trip time is the difference between sent and received time
        rtt = recv_time - sent_time
        print("Round Trip Time: ",rtt)
        print("\n###############################\n")
        # FILL IN END
    except:
        # Server does not response
        # Assume the packet is lost
        print("\n")
        print("Request timed out.")
        print("\n###############################\n")

        continue

# Close the client socket
clientSocket.close()