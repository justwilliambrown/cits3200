#ifndef MESSAGE_H__
#define MESSAGE_H__

#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <errno.h>
#include <signal.h>
#include <libgen.h>
#include <sys/select.h>
#include "utils.h"


typedef struct _connection_t
{
   struct _connection_t   *next;
   int                     sock;
   struct sockaddr_in6     addr;
   size_t                  addrLen;

   player_t player;
} connection_t;

#endif
