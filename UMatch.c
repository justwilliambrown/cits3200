#include "message.h"

static connection_t *connList = NULL;


connection_t *connection_new_incoming(int sock,
                                      struct sockaddr *addr,
                                      size_t addrLen)
{
   connection_t *connP;

   connP = (connection_t *)malloc(sizeof(connection_t));

   if(connP != NULL)
   {
      connP->sock = sock;
      memcpy(&(connP->addr), addr, addrLen);
      connP->addrLen = addrLen;
      connP->next = connList;
   }

   return connP;
}

void broadcast_msg(const char *data, short Length)
{
   connection_t *connP;

   connP = connList;

   while(connP != NULL)
   {
      if(connP->player.init == 1)
      {
         // boradcase message to all connected clients
         writen(connP->sock, data, Length);
      }

      connP = connP->next;
   }
}

void fd_set_all(fd_set *readfds)
{
   connection_t *connP;

   connP = connList;

   while(connP != NULL)
   {
      if(connP->sock > 0)
      {
         FD_SET(connP->sock, readfds);
      }

      connP = connP->next;
   }
}

void connect_fd_isset(fd_set *readfds)
{
   connection_t *connP;
   uint8_t buffer[BUFF_SIZE] = {0};
   int numBytes = 0;

   connP = connList;

   while(connP != NULL)
   {
      memset(buffer, 0, sizeof(buffer));
      numBytes = 0;

      if(FD_ISSET(connP->sock, readfds))
      {
         numBytes = read(connP->sock, buffer, BUFF_SIZE - 1);

         if(numBytes > 0)
         {
            buffer[numBytes] = 0;
            fprintf(stdout, "%s\n", buffer);

            connect_handle(connP, buffer, numBytes);
         }
         else if(numBytes == 0)
         {
            close(connP->sock);

            char s[INET6_ADDRSTRLEN] = {0};
            s[0] = 0;
            struct sockaddr_in *saddr = (struct sockaddr_in *)&connP->addr;
            inet_ntop(AF_INET, &saddr->sin_addr, s, INET6_ADDRSTRLEN);
            fprintf(stdout, "disconnect from [%d]-[%s]\n", connP->sock, s);

            connection_delete(connP);
            break;
         }
      }

      connP = connP->next;
   }
}

void socket_fd_isset(int socket_fd)
{
   struct sockaddr_in connection_addr = {0};
   socklen_t connection_addr_len = INET6_ADDRSTRLEN;

   // accept connection
   int connection_fd = accept(socket_fd, (struct sockaddr *)&connection_addr, &connection_addr_len);

   if(connection_fd < 0)
   {
      perror("accept error");
      return;
   }

   char s[INET6_ADDRSTRLEN] = {0};
   in_port_t port = 0;
   connection_t *connP = NULL;

   s[0] = 0;
   struct sockaddr_in *saddr = (struct sockaddr_in *)&connection_addr;
   inet_ntop(AF_INET, &saddr->sin_addr, s, INET6_ADDRSTRLEN);
   port = saddr->sin_port;

   fprintf(stdout, "accept from [%d]-[%s]:%hu\n", connection_fd, s, ntohs(port));

   connP = connection_new_incoming(connection_fd, (struct sockaddr *)&connection_addr, connection_addr_len);

   if(connP != NULL)
   {
      connList = connP;
   }
}

void stdin_fd_isset()
{
   uint8_t buffer[BUFF_SIZE] = {0};
   int numBytes = 0;

   numBytes = read(STDIN_FILENO, buffer, BUFF_SIZE - 1);

   if(numBytes > 1)
   {
      buffer[numBytes] = 0;
      fprintf(stdout, "%s", buffer);
   }
   else
   {
      fprintf(stdout, "\n");
   }
}

int main(int argc, char **argv)
{
   if(argc != 2)
   {
      return -1;
   }

   fd_set readfds;
   int result;

   signal(SIGALRM, game_timer);

   int socket_fd = socket(AF_INET, SOCK_STREAM, 0);

   if(socket_fd < 0)
   {
      perror("socket error");
      return -1;
   }

   // init father socket sockaddr_in
   struct sockaddr_in server_addr;
   server_addr.sin_family = AF_INET;
   server_addr.sin_port = htons(atoi(argv[1]));

   server_addr.sin_addr.s_addr = INADDR_ANY;

   // bind socket
   if(bind(socket_fd, (struct sockaddr *)&server_addr, sizeof server_addr) < 0)
   {
      perror("bind error");
      return -1;
   }

   // scoket start listening
   if(listen(socket_fd, MAX_CONNECTION) < 0)
   {
      perror("listen error");
      return -1;
   }

   while(1)
   {
      FD_ZERO(&readfds);

      FD_SET(STDIN_FILENO, &readfds);
      FD_SET(socket_fd, &readfds);

      fd_set_all(&readfds);

      result = select(FD_SETSIZE, &readfds, 0, 0, NULL);

      if(result < 0)
      {
         if(errno != EINTR)
         {
            fprintf(stderr, "Error in select(): %d\n", errno);
         }
      }
      else if(result > 0)
      {
         if(FD_ISSET(STDIN_FILENO, &readfds))
         {
            stdin_fd_isset();
         }
         else if(FD_ISSET(socket_fd, &readfds))
         {
            socket_fd_isset(socket_fd);
         }
         else
         {
            connect_fd_isset(&readfds);
         }
      }
   }

   close(socket_fd);
   connection_free();
}
