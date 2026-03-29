#!/usr/bin/env python3
import socket
import struct
import sys

def checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

def send_icmp(dest, seq=0x1337, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(timeout)

    # ICMP Echo Request: type=8, code=0, id=0, seq=0x1337
    icmp_type = 8
    icmp_code = 0
    icmp_id = 0
    header = struct.pack('!BBHHH', icmp_type, icmp_code, 0, icmp_id, seq)
    csum = checksum(header)
    header = struct.pack('!BBHHH', icmp_type, icmp_code, csum, icmp_id, seq)

    sock.sendto(header, (dest, 0))
    print(f"Sent ICMP Echo Request to {dest} with seq=0x{seq:04x}")

    # Wait for ICMP Echo Reply
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            # Skip IP header (first 20 bytes), parse ICMP header
            ip_hdr_len = (data[0] & 0x0F) * 4
            icmp_data = data[ip_hdr_len:]

            reply_type, reply_code, reply_csum, reply_id, reply_seq = struct.unpack('!BBHHH', icmp_data[:8])

            # Check for Echo Reply (type=0) with matching sequence
            if reply_type == 0 and reply_seq == seq:
                payload = icmp_data[8:].decode(errors="replace")
                return payload == "JOLTEON_ALIVE"
    except socket.timeout:
        print("No reply received (timeout)")

    sock.close()

HOST = sys.argv[1]
print(send_icmp(HOST))
