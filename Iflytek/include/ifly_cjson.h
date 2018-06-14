#ifndef __IFLY_CJSON_H__
#define __IFLY_CJSON_H__

#include <stdbool.h>
#include "cJSON.h"

/* apis */
bool ifly_is_valid_response(const cJSON *msg);
char *ifly_get_error_information(const cJSON *msg);
char *ifly_get_requested_text(const cJSON *msg);
char *ifly_get_answered_text(const cJSON *msg);
char *ifly_get_service_name(const cJSON *msg);
void ifly_get_content(const cJSON *result);

void ifly_get_contents(const cJSON *result);


char *ifly_concat_strings(char *str, ...);


#endif //__IFLY_CJSON_H__
