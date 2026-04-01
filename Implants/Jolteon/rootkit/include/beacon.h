#ifndef BEACON_H
#define BEACON_H

#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/inet.h>

void beacon_start(void);
void beacon_stop(void);

#endif