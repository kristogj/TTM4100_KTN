from pydub import AudioSegment
from socket import *
import argparse as ap
import time
import pyaudio

def extract_header_payload(data, nbytes):
    header = data[0 : HEADER_SIZE]
    payload = data[HEADER_SIZE : HEADER_SIZE + (nbytes - HEADER_SIZE)]
    return header, payload

def bigEndienBytesToInt16(b):
    a = b[0] << 8
    a = a | b[1]
    return a

def bigEndienBytesToInt32(b):
    a = b[0] << 24
    a = a | b[1] << 16
    a = a | b[2] << 8
    a = a | b[3]
    return a

def get_version(header):
    version = (header[0] & 0xC0) >> 6
    return version

def get_padding(header):
    padding = (header[0] & 0x20) >> 5
    return padding

def get_extension(header):
    extension = (header[0] & 0x10) >> 4
    return extension

def get_cc(header):
    cc = header[0] & 0x0F
    return cc

def get_marker(header):
    marker = (header[1] & 0x80) >> 7
    return marker

def get_payload_type(header):
    payload_type = header[1] & 0x7F
    return payload_type

def get_sequence_number(header):
    sequence_number = bigEndienBytesToInt16(header[2:4])
    return sequence_number

def get_timestamp(header):
    timestamp = bigEndienBytesToInt32(header[4:8])
    return timestamp

def get_ssrc(header):
    ssrc = bigEndienBytesToInt32(header[8:12])
    return ssrc

def receive_packet(client_socket, client_ip, port, p_stream):
    data_bytes, server_address = client_socket.recvfrom(4096)
    header, payload = extract_header_payload(data_bytes, len(data_bytes))

    print("Ver, Pad, Ext, CC, M, Payload_Type, Sequence_Number,  Timestamp,       SSRC:")
    print("{0:3d}, {1:3d}, {2:3d}, {3:2d}, {4:1d}, {5:12d}, {6:15d}, {7:10d}, {8:10d}" \
        .format(get_version(header), \
                get_padding(header), \
                get_extension(header), \
                get_cc(header), \
                get_marker(header), \
                get_payload_type(header), \
                get_sequence_number(header), \
                get_timestamp(header), \
                get_ssrc(header)))

    p_stream.write(payload)

HEADER_SIZE = 12
DEFAULT_PAYLOAD_TYPE = 'l16_1'

parser = ap.ArgumentParser(description='A test RTP client application')
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

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(payload_types[args.payload_type]['sample_width']),
                channels=payload_types[args.payload_type]['channels'],
                rate=payload_types[args.payload_type]['frame_rate'],
                output=True)

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.bind((args.client_ip, args.client_port))
client_socket.settimeout(10) #Set timeout to be 10 seconds.

try:
    while True:
        receive_packet(client_socket, args.client_ip, args.client_port, stream)
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    client_socket.close()
