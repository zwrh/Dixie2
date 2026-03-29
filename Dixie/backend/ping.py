import socket
import struct


def _checksum(data):
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def ping(dest, seq=0x1337, timeout=5):
    """Send an ICMP Echo Request and return the reply payload string, or None on failure."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(timeout)
    except PermissionError:
        return None

    icmp_type = 8
    icmp_code = 0
    icmp_id = 0
    header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, seq)
    csum = _checksum(header)
    header = struct.pack("!BBHHH", icmp_type, icmp_code, csum, icmp_id, seq)

    try:
        sock.sendto(header, (dest, 0))

        while True:
            data, addr = sock.recvfrom(1024)
            if addr[0] != dest:
                continue
            ip_hdr_len = (data[0] & 0x0F) * 4
            icmp_data = data[ip_hdr_len:]

            reply_type, reply_code, reply_csum, reply_id, reply_seq = struct.unpack(
                "!BBHHH", icmp_data[:8]
            )

            if reply_type == 0 and reply_seq == seq:
                payload = icmp_data[8:].decode(errors="replace")
                return payload == "JOLTEON_ALIVE"
    except (socket.timeout, OSError):
        return None
    finally:
        sock.close()
