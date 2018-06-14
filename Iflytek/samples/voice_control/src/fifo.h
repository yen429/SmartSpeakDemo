#ifndef __FIFO_H__
#define __FIFO_H__

int fifo_init(const char *fifo_file);
int fifo_write(int fd ,const char *message, int message_size);
void fifo_close(int fd);

#endif