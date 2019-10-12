//written by Aidan Haile, 2019
//uses the cJSON library, found at https://github.com/DaveGamble/cJSON
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include "Colosseum.h"

void (*broadcastFunc)(const cJSON&);
void (*requestFunc)(const cJSON&, cJSON*);
void (*resetFunc)();

int sockfd;

//small helper function for recvall
int countOccurences(char* str, char val, int len)
{
	int count = 0;
	for(int i = 0; i < len; i++)
	{
		if(char[i] == '\0') break;
		if(char[i] == val)
			count++;
	}
	return count;
}

int recvall(int fd, char* buffer, int maxlen)
{
	int recvd = recv(fd, (void*)buffer, maxlen, 0);
	if(recvd == 0)
		return 0; //server has disconnected us
	int depth = countOccurences(buffer, '{', recv) - countOccurences(buffer, '}', recv);
	while(depth > 0 && recvd < maxlen)
	{
		int temprecv += recv(fd, (void*)(buffer + recvd), maxlen - recvd, 0);
		if(temprecv == 0)
			return 0;
		recvd += temprecv;

		depth += countOccurences((buffer + recvd), '{', maxlen - recvd) - countOccurences((buffer + recvd), '}', maxlen - recvd);
	}

	return recvd;
}

int sendall(int fd, char* buffer, int len)
{
	int sent = 0;
	while(sent < len)
	{
		int tempsent += send(fd, buffer, len - sent, 0);
		if(tempsent == -1)
		{
			fprintf(stderr, "error sending to client, dying\n");
			exit(EXIT_FAILURE);
		}
	}
}

int registerBroadcast(cJSON* (*callback)(const cJSON&))
{
	if(callback == NULL)
		return 0;
	broadcastFunc = callback;
	return 1;
}

int registerRequest(cJSON* (*callback)(const cJSON&, cJSON*))
{
	if(callback == NULL)
		return 0;
	requestFunc = callback;
	return 1;
}

int registerReset(void (*callback)())
{
	if(callback == NULL)
		return 0;
	resetFunc = callback;
	return 1;
}

int connect(char* host, char* port, char* user, char* pass)
{
	struct addrinfo hints, *servinfo, *p;
	int rv;

	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;

	if((rv = getaddrinfo(host, port, &hints, &servinfo)) != 0)
	{
		fprintf(stderr, "error with getaddrinfo\n");
		return -1;
	}

	for(p = servinfo; p != NULL; p = p->ai_next)
	{
		if((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1)
			continue;
		if(connect(sockfd, p->ai_addr, p->ai_addrlen) == -1)
			continue;

		break;
	}

	if(p == NULL)
	{
		fprintf(stderr, "client failed to connect\n");
		return -2;
	}

	freeaddrinfo(servinfo);

	char buf[BUFSIZ];
	int recvd = recv_all(sockfd, buf, BUFSIZ);

	if(recv == 0)
	{
		fprintf(stderr, "server disconnected");
		return 0;
	}

	cJSON *req;
	if((*req = cJSON_Parse(buffer)) == NULL)
	{
		fprintf(stderr, "cJSON error\n");
		return -1;
	}

	cJSON* subtype = cJSON_GetObjectItem(req, "subtype");
	if(!(type != NULL && cJSON_IsString(subtype) && subtype->valuestring != NULL && strncmp(subtype->valuestring, "loginRequest", strlen("loginRequest")) == 0))
	{
		fprintf(stderr, "received unexpected response from server\n");
		return -1;
	}
	cJSON_Delete(req);

	char response[BUFSIZ];
	sprintf(response, "{'user' : '%s', 'pass' : '%s'}", user, pass);
	sendall(sockfd, pass, strlen(response));

	memset(buf, 0, BUFSIZ);
	int recvd = recvall(sockfd, buf, BUFSIZ);
	if(recvd == 0)
	{
		fprintf(stderr, "server disconnected\n");
		return -1;
	}

	cJSON* resp;
	if((resp = cJSON_Parse(buf)) == NULL)
	{
		fprintf(stderr, "cJSON error\n");
		return -1;
	}

	subtype = cJSON_GetObjectItem(resp, "subtype");
	if(!(type != NULL && cJSON_IsString(subtype) && subtype->valuestring != NULL))
	{
		fprintf(stderr, "received unexpected response from server\n");
		return -1;
	}

	if(strncmp(subtype->valuestring, "loginAccept", strlen("loginAccept")) == 0)
	{
		cJSON_Delete(resp);
		return 1;
	}
	else
	{
		cJSON_Delete(resp);
		return 0;
	}
	return 0;
}

void beginPlay()
{
	while(true)
	{
		char buffer[BUFSIZ];
		if(recvall(sockfd, buf, BUFSIZ) == 0)
		{
			printf("server has disconnected you\n");
			return;
		}

		cJSON* svmsg = cJSON_Parse(buffer);

		cJSON* type = cJSON_GetObjectItem(svmsg, "type");
		if(type == NULL || cJSON_IsString(type) || type->valuestring == NULL)
		{
			fprintf(stderr, "unknown/malformed response from server\n");
			return;
		}

		cJSON* move = cJSON_CreateObject();

		if(strncmp(type->valuestring, "BROADCAST", strlen(BROADCAST)) == 0)
		{
			broadcastFunc(svmsg);
			cJSON_Delete(svmsg);
			cJSON_Delete(move);
			continue; //if a broadcast is received, it hasn't been asked for a response. Mush like current years "see"
		}
		else if(strncmp(type->valuestring, "RESET", strlen("RESET")) == 0)
		{
			resetFunc();
		}
		else
		{
			requestFunc(svmsg, move);
		}

		char* response = cJSON_Print(move);
		if(response == NULL)
		{
			fprintf(stderr, "cJSON error, exiting");
			exit(EXIT_FAILURE);
		}
		sendall(sockfd, response, strlen(response));
		cJSON_Delete(move);
		cJSON_Delete(svmsg);
	}
}