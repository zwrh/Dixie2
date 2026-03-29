import socket
import struct
import time


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


def ping_batch(targets, timeout=5):
    """Ping multiple targets using a single socket with unique sequence numbers.

    Args:
        targets: list of IP address strings
        timeout: seconds to wait for all replies

    Returns:
        dict mapping IP address to bool (True if JOLTEON_ALIVE, False/None otherwise)
    """
    results = {ip: None for ip in targets}
    if not targets:
        return results

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(timeout)
    except PermissionError:
        return results

    seq = 0x1337
    icmp_type = 8
    icmp_code = 0
    icmp_id = 0
    header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, seq)
    csum = _checksum(header)
    header = struct.pack("!BBHHH", icmp_type, icmp_code, csum, icmp_id, seq)

    for ip in targets:
        try:
            sock.sendto(header, (ip, 0))
        except OSError:
            pass

    # Collect replies until timeout or all answered
    pending = set(targets)
    deadline = time.monotonic() + timeout

    try:
        while pending:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            sock.settimeout(remaining)

            data, addr = sock.recvfrom(1024)
            src_ip = addr[0]
            if src_ip not in pending:
                continue

            ip_hdr_len = (data[0] & 0x0F) * 4
            icmp_data = data[ip_hdr_len:]
            if len(icmp_data) < 8:
                continue

            reply_type, reply_code, reply_csum, reply_id, reply_seq = struct.unpack(
                "!BBHHH", icmp_data[:8]
            )

            if reply_type == 0 and reply_seq == seq:
                payload = icmp_data[8:].decode(errors="replace")
                results[src_ip] = payload == "JOLTEON_ALIVE"
                pending.discard(src_ip)
    except (socket.timeout, OSError):
        pass
    finally:
        sock.close()

    return results
