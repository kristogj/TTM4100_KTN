from pydub import AudioSegment
from socket import *
import argparse as ap
import struct
import time

def int16ToBytesBigEndien(a):
    b = bytearray([0, 0])
    b[1] = a & 0xFF
    a = a >> 8
    b[0] = a & 0xFF
    return b

def int32ToBytesBigEndien(a):
    b = bytearray([0, 0, 0, 0])
    b[3] = a & 0xFF
    a = a >> 8
    b[2] = a & 0xFF
    a = a >> 8
    b[1] = a & 0xFF
    a = a >> 8
    b[0] = a & 0xFF
    return b

def send_packet(i, seq, data, data_size, frame_size, frame_period, server_socket, pt):
    #RTP header fields
    #See https://tools.ietf.org/html/rfc3550#section-5.1
    version = 2
    padding = 0
    extension = 0
    cc = 0
    marker = 0
    payload_type = pt
    sequence_number = 0
    timestamp = 0
    ssrc = 0xfc03a85e #Just a random number

    if i < data_size:
        packet = bytearray()

        sequence_number = seq
        #timestamp be a monotonically increasing number
        timestamp = i

        #See https://tools.ietf.org/html/rfc3550#section-5.1
        #Set the first 2 bits, bits 0 and 1, indicating RTP version to header_byte, the first byte of the header.
        header_byte = (version & 0x03) << 6
        #Set bit 2 for the padding field in the first byte of the header
        header_byte = header_byte | ((padding & 0x01) << 5)
        #Set bit 3 for the extension field in the first byte of the header
        header_byte = header_byte | ((extension & 0x01) << 4)
        #Set bits 4 to 7 for the CC field in the first byte of the header
        header_byte = header_byte | (cc & 0x0F)
        packet.append(header_byte) #Append the 1st byte to the packet

        #Reuse the variable header_byte.
        header_byte = 0
        #Set bit 0 for the marker field in the second byte of the header
        header_byte = (marker & 0x01) << 7
        #Set bits 1 to 7 for the payload type field in the second byte of the header
        header_byte = header_byte | (payload_type & 0x7F)
        packet.append(header_byte) #2nd byte

        #Unpack the 16-bit sequence number to big-endien bytes
        tmp = int16ToBytesBigEndien(sequence_number)
        for j in range(0, len(tmp)):
            packet.append(tmp[j]) #3rd and 4th bytes
        #Unpack the 32-bit timestamp to big-endien bytes
        tmp = int32ToBytesBigEndien(timestamp)
        for j in range(0, len(tmp)):
            packet.append(tmp[j]) #5th - 8th bytes
        #Unpack the 32-bit SSRC to big-endien bytes
        tmp = int32ToBytesBigEndien(ssrc)
        for j in range(0, len(tmp)):
            packet.append(tmp[j]) #9th - 12th bytes
        #We do not append CSRC list identifier to the header as it's optional and there is no need.

        #Now the payload starts
        #Append each byte of an audio frame to the packet
        for j in range(i, i+frame_size):
            if j < data_size:
                packet.append(data[j])

        #Send the packet to the client
        client_address = (args.client_ip, args.client_port)
        server_socket.sendto(packet, client_address)

DEFAULT_PAYLOAD_TYPE = 'l16_2'

parser = ap.ArgumentParser(description='A test RTP server application')
parser.add_argument('-f', '--file', dest='audio_file', required=True, metavar='<audio_file>')
parser.add_argument('-c', '--client', dest='client_ip', required=True, metavar='<client_ip>')
parser.add_argument('-p', '--port', dest='client_port', type=int, default=5004, metavar='<client_port>')
parser.add_argument('-t', '--payload-type', dest='payload_type', default=DEFAULT_PAYLOAD_TYPE, metavar='<payload_type>')
args = parser.parse_args()

#See payload type definitions in https://tools.ietf.org/html/rfc3551#page-32
payload_types = {
    'l16_1':{'sample_width':2, 'frame_rate':44100, 'channels':1, 'code':11},
    'l16_2':{'sample_width':2, 'frame_rate':44100, 'channels':2, 'code':10},
    'pcmu':{'sample_width':1, 'frame_rate':8000, 'channels':1, 'code':0},
    'pcma':{'sample_width':1, 'frame_rate':8000, 'channels':1, 'code':8}
}

audio = AudioSegment.from_file(args.audio_file)
if args.payload_type != DEFAULT_PAYLOAD_TYPE:
    audio = audio.set_frame_rate(payload_types[args.payload_type]['frame_rate'])
    audio = audio.set_sample_width(payload_types[args.payload_type]['sample_width'])
    audio = audio.set_channels(payload_types[args.payload_type]['channels'])
#The default raw audio data of AudioSegment is in PCM format; any input format will be automatically converted to PCM or WAV.
data = audio.raw_data
data_size = len(data)

#A PCM frame consists of one sample per channel.
#A sample width is in bytes, e.g., 8 bits -> 1 byte, 16 bits -> 2 bytes.
frame_size = audio.sample_width * audio.channels
#The frame rate determines how fast a frame is replaced by the next one when played back, in Hz or frames/duration_seconds
#The frame period is 1/frame_rate in seconds
frame_period = 1.0 / audio.frame_rate

N_FRAMES = 1000 #The number of audio frames per packet
SENDING_INTERVAL_MODIFIER = 4

seq = 0
frames_size = frame_size * N_FRAMES
frames_period = frame_period * N_FRAMES
server_socket = socket(AF_INET, SOCK_DGRAM)

for j in range(0, data_size, frames_size):
    send_packet(j, seq, data, data_size, frames_size, frames_period, server_socket, payload_types[args.payload_type]['code'])
    seq += 1
    #Adjust the sending interval to be a little faster/shorter than the frames period to compensate the communication delay and processing delay at the receiver/client.
    time.sleep(frames_period-frames_period/SENDING_INTERVAL_MODIFIER)

server_socket.close()
