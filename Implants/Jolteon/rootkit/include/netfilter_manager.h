#ifndef HEADER_NETFILTER_MANAGER
#define HEADER_NETFILTER_MANAGER

#include <linux/kernel.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/module.h>
#include <linux/version.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <net/icmp.h>
#include <net/route.h>

int register_netfilter_hook(void);
void unregister_netfilter_hook(void);

#define MAGIC_SEQ 0x1337

#endif