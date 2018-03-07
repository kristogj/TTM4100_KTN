# This skeleton is valid for both Python 2.7 and Python 3.
# You should be aware of your additional code for compatibility of the Python version of your choice.

from socket import *
import argparse as ap
import getpass as gp

#Get sender_email and recipient_email as arguments to the program
parser = ap.ArgumentParser(description='A test SMTP client without authentication')
parser.add_argument('-f', '--from', dest='fromMail', required=True, metavar='<sender_email>')
parser.add_argument('-t', '--to', dest='toMail', required=True, metavar='<recipient_email>')
#If using the authentication of the SMTP server, also get a valid username (optional exercise)
#parser.add_argument('-u', '--username', dest='username', required=True, metavar='<username>')

args = parser.parse_args()
fromMail = args.fromMail #Sender's email address
toMail = args.toMail #Recipient's email address
#username = args.username #SMTP username in case you are implementing the optional exercise

#If using the authentication of the SMTP server, ask for a valid password (optional exercise)
#password = gp.getpass(prompt='Password: ')

# Message to send
msg = "I love computer networks!\r\n"
endmsg = ".\r\n"

# Our mail server is smtp.stud.ntnu.no but it allows only authenticated communications. (optional exercise)
#mailserver = 'smtp.stud.ntnu.no'
# You can run a local simple SMTP server such as "Fake SMTP Server" and communicate with it without authentication.
mailserver = 'localhost'
serverport = 12000

# Create socket called clientSocket and establish a TCP connection
# (use the appropriate port) with mailserver
#Fill in start
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver,serverport))
#Fill in end

recv = clientSocket.recv(1024)
print(recv)
if recv[:3] != b'220':
	print('0 220 reply not received from server.')

def method(command, n):
	clientSocket.send(command.encode())
	recv = clientSocket.recv(1024)
	print(recv)
	if recv[:3] != n:
		print(str(n),'reply not received from server.')


# Send HELO command and print server response.
# Can use EHLO instead since HELO is obsolete, but the latter can still be used
heloCommand = 'EHLO Hey\r\n'
method(heloCommand,b'250')

# Send MAIL FROM command and print server response.
# Fill in start
mailFromCommand = "MAIL FROM: <" + str(fromMail) + ">\r\n"
method(mailFromCommand,b'250')
# Fill in end

# Send RCPT TO command and print server response.
# Fill in start
rcptToCommand = "RCPT TO:<" + str(toMail) + ">\r\n"
method(rcptToCommand,b'250')
# Fill in end

# Send DATA command and print server response.
# Fill in start
method("DATA\r\n",b'354')
# Fill in end

# Send message data.
# Fill in start
clientSocket.send(msg.encode())
# Fill in end

# Message ends with a single period.
# Fill in start
method(endmsg,b'250')

# Send QUIT command and get server response.
# Fill in start
method("QUIT\r\n",b'221')
# Fill in end

#Note that there are more communications if you implement the optional exercise.
