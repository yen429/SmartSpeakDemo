#ifndef __IFLY_H__
#define __IFLY_H__

#if 0
#ifdef __cplusplus
extern "C" {
#endif 
#endif

typedef enum {
    RC_OK = 0,              //** operation successful
    RC_ERROR = 3,           //** operation fail, check error information via ifly_get_error_information
    RC_UNRECOGNIZE = 4      //** unrecognized request
} IFLY_RESPONSE_CODE;



typedef enum {
    SERVICE_UNKNOWN = 0,
    SERVICE_MUSICX,
    SERVICE_WEATHER,
    SERVICE_PM25,
    SERVICE_FLIGHT,
    SERVICE_TRAIN,
    SERVICE_TELEPHONE,
    SERVICE_NUMBER_MASTER,
    SERVICE_POETRY,
    SERVICE_STORY,
    SERVICE_JOKE,
    SERVICE_RADIO,
    SERVICE_NEWS,
    SERVICE_COOKBOOK,
    SERVICE_CHAT,
    SERVICE_CALC,
    SERVICE_DATETIME,
    SERVICE_YHJG,
    SERVICE_TCYL,
    SERVICE_DATA_TRANSFER,
    SERVICE_LLB,
    SERVICE_ZDCX,
    SERVICE_MYCX,
    SERVICE_TELEPHONE_FEE,
    SERVICE_TCCX,
    SERVICE_DZFP,
    SERVICE_ROBOT_ACTION,
    SERVICE_CMD,
    SERVICE_DISH_ORDER,
    SERVICE_MOVIE,
    SERVICE_LIVE,
    SERVICE_OPEN_QA,
    SERVICE_AIUI_CYCLOPEDI,
} IFLY_SERVICE_ID;


/* The ifly_data structure: */
typedef struct ifly_data
{
    struct ifly_data *next;
    struct ifly_data *prev;
    char *content;
    char *title;
} ifly_data;

/* new struction design */
typedef struct ifly_joke_data
{
    struct ifly_data *next;
    struct ifly_data *prev;
    char *content;
    char *title;
} ifly_joke_data;

typedef struct ifly_weather_data
{
    struct ifly_data *next;
    struct ifly_data *prev;
    char *content;
    char *title;
} ifly_weather_data;

// ---------------------------------------------------------------------------------
//#define USE_CJSON
#define USE_RAPIDJSON

// ---------------------------------------------------------------------------------
#ifdef USE_CJSON
#include "ifly_cjson.h"
#else
#ifdef USE_RAPIDJSON
#include "ifly_rapidjson.h"
#endif //USE_CJSON
#endif //USE_CJSON
// ---------------------------------------------------------------------------------

/* internal linked-list utility */
void ifly_list_insert(char *title, char *content);
void ifly_list_delete(ifly_data *current, char *title, char *content);
void ifly_list_print(ifly_data *current);
bool ifly_list_find(ifly_data *current, char *title, char *content);
void ifly_list_free(void);

#if 0
#ifdef __cplusplus
}
#endif 
#endif

#endif
