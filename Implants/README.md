# Implants

## Disclaimer

This software is provided strictly for **educational and authorized research purposes only**. It is designed as a learning tool to understand how kernel-level rootkits and remote management agents operate at a low level.

**By using this software, you agree to the following:**

- You will only deploy this software on systems that **you own** or have **explicit written authorization** to test.
- You will **not** use this software for unauthorized access, data theft, espionage, or any other malicious activity.
- You understand that deploying rootkits on systems without authorization is **illegal** in most jurisdictions and may violate laws such as the Computer Fraud and Abuse Act (CFAA), the Computer Misuse Act, and equivalent legislation worldwide.
- The authors and contributors of this project bear **no responsibility** for any misuse, damage, or legal consequences resulting from the use of this software.

**If you do not agree with these terms, do not use this software.**

## Overview

This directory contains kernel-level implants that communicate with the Dixie backend via ICMP. Each implant responds to ICMP Echo Requests with a `JOLTEON_ALIVE` payload to signal that the client is active and responsive.

## Requirements

- Linux kernel headers for your target kernel version
- Root privileges for loading kernel modules
- A controlled lab environment (VMs, containers, or isolated networks)
