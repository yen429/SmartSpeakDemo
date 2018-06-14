#ifndef __DEBUG_H_
#define __DEBUG_H_

#define DEBUG 0
#if DEBUG == 1
#define DEBUG_MSG(format, args...) printf("[DEBUG:%s:%d] " format, __FUNCTION__, __LINE__, ##args)
#else
#define DEBUG_MSG(args...)
#endif

#define ERROR_MSG(format, args...) printf("[ERROR:%s:%d] " format, __FUNCTION__, __LINE__, ##args)
#define INFO_MSG(format, args...) printf("[INFO:%s:%d] " format, __FUNCTION__, __LINE__, ##args)

#endif