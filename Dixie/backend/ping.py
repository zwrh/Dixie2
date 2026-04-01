import socket
import struct
import threading

def listen_icmp(callback, magic_id=0xBEEF, magic_seq=0x1337):
    """Listen for ICMP echo requests matching magic id/seq.

    Args:
        callback: function(src_ip, id, seq, payload) called on match
        magic_id: expected ICMP identifier (or None to accept any)
        magic_seq: expected ICMP sequence (or None to accept any)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    while True:
        data, addr = sock.recvfrom(1024)
        src_ip = addr[0]

        # Parse IP header length
        ip_hdr_len = (data[0] & 0x0F) * 4
        icmp_data = data[ip_hdr_len:]

        if len(icmp_data) < 8:
            continue

        icmp_type, icmp_code, checksum, pkt_id, pkt_seq = struct.unpack(
            "!BBHHH", icmp_data[:8]
        )

        # Filter for echo requests (type 8)
        if icmp_type != 8:
            continue

        # Check magic values if specified
        if magic_id is not None and pkt_id != magic_id:
            continue
        if magic_seq is not None and pkt_seq != magic_seq:
            continue

        payload = icmp_data[8:]
        callback(src_ip, pkt_id, pkt_seq, payload)


def start_icmp_listener(callback, magic_id=0xBEEF, magic_seq=0x1337):
    """Start ICMP listener in a background thread."""
    thread = threading.Thread(
        target=listen_icmp,
        args=(callback, magic_id, magic_seq),
        daemon=True
    )
    thread.start()
    return thread