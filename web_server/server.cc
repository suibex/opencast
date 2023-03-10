
#include <stdio.h>
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netdb.h>
#include <assert.h>
#include <vector>
#include <fcntl.h>
#include <iostream>



/*
  
  Add SSL encryption

  Request types:
    GET DEVICE {IP} - returns a list of devices connected on that ip address.
    POST DEVICE {IP} - saves a device to the list with that ip address.

*/

std::vector<std::string> split(std::string str,std::string del){
	
  std::vector<std::string>dele;
	ssize_t beg,pos=0;
	while((beg=str.find_first_not_of(del,pos)) !=std::string::npos){
		pos = str.find_first_of(del,pos+1);
		dele.push_back(str.substr(beg,pos-beg));  
	}

	return dele;
}


class WebServer{

    public:

      int port ; 
      int sockfd;
      int clifd;

      WebServer(int p){
        port = p ;

      }
      void dispatch(){
        
        struct addrinfo *ptr,*res,hints;
        memset(&hints,0x00,sizeof(hints));
        
        hints.ai_family =AF_UNSPEC;
        hints.ai_protocol = IPPROTO_TCP;
        hints.ai_flags = AI_PASSIVE;

        getaddrinfo(NULL,std::to_string(port).c_str(),&hints,&res);
        for(ptr = res; ptr!= NULL; ptr=ptr->ai_next){
            
            sockfd = socket(ptr->ai_family,ptr->ai_socktype,ptr->ai_protocol);
            assert(sockfd != -1);
            int ret = bind(sockfd,ptr->ai_addr,(int)ptr->ai_addrlen);
            assert(ret != -1 && "Binding socket failed.");
            break;

            
        } 
        freeaddrinfo(res);
        listen(sockfd,0xFFFF);
  
        struct sockaddr_storage *their = (struct sockaddr_storage *)malloc(sizeof(struct sockaddr_storage));
        socklen_t len = sizeof(struct sockaddr_storage);

        while(1){
            
             clifd = accept(sockfd,(struct sockaddr*)their,&len);
             if(clifd< 0 ){
                break;
             }
             if(fork() == 0 ){

                  close(sockfd);
                  std::string request = "" ;

                  while(1){
                    
                    char dat[4];
                    int ss = recv(clifd,dat,4,0);
                    std::string db = "";
                    db+=dat[0];
                    db+=dat[1];
                    db+=dat[2];
                    db+=dat[3];

                    request+=db;
                    if(db == "\r\n\r\n"){
                        break;
                    }
     
                  }

                  std::vector<std::string> req  = split(request,"\r\n");
                  std::vector<std::string> type = split(req[0]," ");
                  if(type[0] == "GET"){

                  }

                  


                  close(clifd);
                  exit(1);
            
             }
             close(clifd);

        }

      
       close(sockfd);
      } 
    

};


int main(){
  
  WebServer *srv = new WebServer(444);
  srv->dispatch();

}


