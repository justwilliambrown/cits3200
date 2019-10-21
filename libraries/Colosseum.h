#pragma once
#include <socket.h>
#include <cjson/cJSON.h>

int connect(char* host, int hostlen, int port, char* user, int userlen, char* pass, int passlen);
void beginPlay();

int registerBroadcast(void (*callback)( const cJSON&));
int registerRequest(void (*callback)(const cJSON&, cJSON*));
int registerReset(void (*callback));