#include "../include/ftrace_manager.h"
#include <linux/kprobes.h>

MODULE_LICENSE("GPL");

// kallsyms_lookup_name no longer exported in newer kernels, use kprobes to get its address
#if LINUX_VERSION_CODE >= KERNEL_VERSION(5,7,0)
typedef unsigned long (*kallsyms_lookup_name_t)(const char *name);
static kallsyms_lookup_name_t kallsyms_lookup_name_ptr;

static int kallsyms_lookup_name_init(void)
{
        struct kprobe kp = {
                .symbol_name = "kallsyms_lookup_name",
        };
        int ret = register_kprobe(&kp);
        if (ret < 0) {
                return ret;
        }
        kallsyms_lookup_name_ptr = (kallsyms_lookup_name_t)kp.addr;
        unregister_kprobe(&kp);
        return 0;
}

static unsigned long jolteon_kallsyms_lookup_name(const char *name)
{
        if (!kallsyms_lookup_name_ptr) {
                int ret = kallsyms_lookup_name_init();
                if (ret < 0) {
                        return 0;
                }
        }
        return kallsyms_lookup_name_ptr(name);
}
#else
#define jolteon_kallsyms_lookup_name kallsyms_lookup_name
#endif

// resolving a target address for hooking
int resolve_hook_address (struct ftrace_hook *hook){
        hook->address = jolteon_kallsyms_lookup_name(hook->name);
        if (!hook->address) {
                printk(KERN_DEBUG "Unresolved symbol on resolve_hook_address(): %s\n", hook->name);
                return -ENOENT;
        }
        *((unsigned long*) hook->original) = hook->address;
        return 0;
}


void notrace ftrace_thunk(unsigned long ip, unsigned long parent_ip, struct ftrace_ops *ops, struct ftrace_regs *fregs){
    struct ftrace_hook *hook = container_of(ops, struct ftrace_hook, ops);
    struct pt_regs *regs = ftrace_get_regs(fregs);
    //If we hook a syscall and we triggered it ourselves, we could hook the hook recursively.
    //We check we are not in the parent tree of the call.

    if (!regs){
        return;
    }
    // redirecting to the hook function
    if (!within_module(parent_ip, THIS_MODULE)){
		regs->ip = (unsigned long) hook->function;
	}
    //printk(KERN_INFO "THUNK\n");
		
}


int install_hook(struct ftrace_hook *hook){
    int err;
    printk(KERN_INFO "Installing hook %s\n", hook->name);
    err = resolve_hook_address(hook);
    if(err){
		printk(KERN_DEBUG "Could not resolve hook address on install_hook()\n");
		return err;
	}
    
    //Alert ftrace that we will be using the rip register in some cases
    hook->ops.func = ftrace_thunk;
    hook->ops.flags = FTRACE_OPS_FL_SAVE_REGS| FTRACE_OPS_FL_RECURSION| FTRACE_OPS_FL_IPMODIFY;

    err = ftrace_set_filter_ip(&hook->ops, hook->address, 0, 0);
    if(err){
        printk(KERN_DEBUG "ftrace_set_filter_ip() failed: %d\n", err);
        return err;
    }
        
	err = register_ftrace_function(&hook->ops);
    if(err){
        printk(KERN_DEBUG "register_ftrace_function() failed: %d\n", err);
        return err;
    }

    printk(KERN_DEBUG "hook loaded: %s\n", hook->name);
    return 0;
}


void remove_hook(struct ftrace_hook *hook){
    int err = unregister_ftrace_function(&hook->ops);
    if(err){
        printk(KERN_DEBUG "unregister_ftrace_function() failed: %d\n", err);
    }
	err = ftrace_set_filter_ip(&hook->ops, hook->address, 1, 0);
    if(err){
        printk(KERN_DEBUG "ftrace_set_filter_ip() failed: %d\n", err);
    }
}

int install_hooks_set(struct ftrace_hook *hooks, size_t count){
    int ii;
    for (ii=0; ii<count; ii++){
        int err = install_hook(&hooks[ii]);
        if(err){
            while (ii!=0){
                remove_hook(&hooks[--ii]);
            }
            return err;
        }
            
    }
    return 0;    
}

void remove_hooks_set(struct ftrace_hook *hooks, size_t count){
    int ii;
    for (ii=0; ii<count; ii++){
        remove_hook(&hooks[ii]);
    }
        
}
