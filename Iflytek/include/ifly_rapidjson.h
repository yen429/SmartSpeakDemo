#ifndef __IFLY_RAPIDJSON_H__
#define __IFLY_RAPIDJSON_H__

#include <stdbool.h>
#include <cstdio>
#include "rapidjson/reader.h"
#include "rapidjson/document.h"
#include "rapidjson/pointer.h"
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <string>
#include <cerrno>

using namespace rapidjson;
using namespace std;

/* apis */
bool ifly_parser_start(const char *json);
void ifly_parser_end(void);
bool ifly_is_valid_response(void);
char *ifly_get_error_information(void);
char *ifly_get_requested_text(void);
char *ifly_get_answered_text(void);
char *ifly_get_service_name(void);
void ifly_get_content(void);

const char *ifly_get_contents(const char *json);


char *ifly_concat_strings(char *str, ...);



#endif //__IFLY_RAPIDJSON_H__
