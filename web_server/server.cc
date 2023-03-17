
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
#include <fstream>
#include <dirent.h>
#include <sys/stat.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#define CERTPATH "./cert.pem"
#define KEYPATH "./key.pem"
using std::string;
using std::endl;
using std::vector;
using std::ostream;
using std::cout;

#define LOWERCASE "abcdefghijklmnopqrstuvwxyz1234567890._"
#define UPPERCASE "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890._"

/*
  
  Add SSL encryption

  Request types:
    GET /{IP} HTTPS - returns all opencast devices on the network.
    POST /{ip} HTTPS -  adds the device to the network 

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

std::string get_device_list(std::string ip){

    if(access(("./redundant_data/"+ip).c_str(),F_OK)){
        return "{\"result\":[\"NO_DEVICES_FOUND\"]}";
    }

    FILE *a = fopen(("./redundant_data/"+ip).c_str(),"r");
    fseek(a,0,SEEK_END);
    int size= ftell(a);
    fseek(a,0,SEEK_SET);
    char *cont = (char*)malloc(sizeof(char)*size);
    fread(cont,size,1,a);
    std::string content;
    for(int i = 0 ;i <size;i++){
      content+=cont[i];
    }
    std::string devs = "{\"result\":[";
    std::vector<std::string> devices = split(content,"\n");
    for(int i = 0 ;i < devices.size();i++){
      std::string device = devices[i];
      std::string devi = "\""+device+"\"";
      if(i  != devices.size()-1){
        devi+=",";
      }
      devs+=devi;

    }
    devs+="]}";
    fclose(a);
    return devs;
}   
/*

  Queue system:

    POST /getQueue {'ip':127.0.0.1,'device':'Kurcina'} - gets a current URL that is being played.
    POST /setQueue {'ip':'127.0.0.1','device':'kurcina','url':'https://github.com/nitrodegen'}



*/
class WebServer{

    public:

      int port ; 
      int sockfd;
      int clifd;

      
      WebServer(int p){
        port = p ;

      }
      int write_cast_device(vector<string> data){

          string host = data[0];
          string ip = data[1];

          if((access(("./redundant_data/"+ip).c_str(),F_OK)) == -1){

            
            FILE *a = fopen(("./redundant_data/"+ip).c_str(),"w");
            if(a == NULL){
              return -1;
            }
            fwrite(host.c_str(),host.length(),1,a);
            fclose(a);

            return  0; 
          }

          return -1;

      }
      std::vector<std::string> fetch_data_from_json(std::string json){

          std::vector<std::string> result;
          string dat = json.substr(json.find("dev_info")+10);
          vector<string> elems = split(dat,",");
          vector<string>new_elems ; 
          for(auto const& th: elems){
            string dot = "";
            for(int i = 0 ;i <th.length();i++){
              bool found = false;
              for(int j = 0 ;j < strlen(LOWERCASE);j++){
                if(th[i] == LOWERCASE[j] || th[i] == UPPERCASE[j]){
                  found= true;
                }
              }
              if(found == true){
                dot+=th[i];
              }
     
            }

            new_elems.push_back(dot);

          }
          return new_elems;

      }
      std::string construct_https_result(std::string dat){
        std::string req = "";
        req+="HTTP/1.1 200 OK\r\n";
        req+="Date: Mon, 27 Jul 2022 12:28:53 GMT\r\n";
        req+="Server:opencast/1.0a\r\n";
        req+="Last-Modified: Wed, 22 Jul 2022 19:15:56 GMT\r\n";
        req+="Content-Length: "+std::to_string(dat.length())+"\r\n";
        req+="Content-Type: application/json\r\n";
        req+="Connection: Closed\r\n\r\n";
        return req;
      }

      SSL_CTX *init_ctx(void){

          SSL_CTX *ctx;
          OpenSSL_add_all_algorithms();  /* load & register all cryptos, etc. */
          SSL_load_error_strings();   /* load all error messages */

          ctx = SSL_CTX_new(TLS_server_method());
          assert(ctx != NULL);
          return ctx;

      }

      void dispatch(){

        SSL_library_init();
        SSL_CTX *ctx = init_ctx();
        int ret =SSL_CTX_load_verify_locations(ctx,CERTPATH,NULL);
        printf("\nret:%d",ret);
        ret = SSL_CTX_use_certificate_file(ctx, CERTPATH, SSL_FILETYPE_PEM);
        printf("\nret:%d",ret);
        ret = SSL_CTX_use_PrivateKey_file(ctx, KEYPATH, SSL_FILETYPE_PEM);
        printf("\nret:%d",ret);

        int servfd = dispatch_socket();
    

        while(1){
             struct sockaddr_in addr;
             unsigned int len = sizeof(addr);
             clifd = accept(sockfd,(struct sockaddr*)&addr, &len);
             assert(clifd != -1);
             if(fork() == 0 ){

                SSL *ssl;
                ssl = SSL_new(ctx);
                SSL_set_fd(ssl,clifd);
                int ret = 1;
                if ( (ret = SSL_accept(ssl)) <= 0){
                    printf("\ncould not accept connection.");
                    exit(1);
                }

                std::string request =  "" ;
                if(ret >0){
                  while(1){
                    char data[4];
                    int re = SSL_read(ssl,data,sizeof(data));
                    std::string dat;
                    for(int i = 0 ;i < 4;i++){
                      dat+=data[i];
                    }
                    request+=dat;
                    if(dat.find("\r\n\r\n") != std::string::npos || request.find("\r\n\r\n") != std::string::npos){
                      
                      break;
                    }
                  }

                  //And finally , process the request here.
                    std::cout<<request<<std::endl;

                    std::vector<std::string> dat = split(request,"\r\n");
                    std::vector<std::string> data = split(dat[0]," ");
                    if(data[0]  == "GET"){
                      
                      std::string cast_device_ip = data[1].substr(data[1].find("/")+1);
                      std::string out  = get_device_list(cast_device_ip);
                      out = construct_https_result(out)+out;

                      std::cout<<out<<std::endl;
                      SSL_write(ssl,out.c_str(),out.length());

                    }
                    if(data[0] == "POST"){
                      
                        if(data[1].substr(data[1].find("/")+1) == "add_device"){
                          cout<<"ADDING?"<<endl;
                          std::string post_data = "" ;
                          for(auto const& param:dat){
                            std::vector<std::string> param_args = split(param,":");
                            if(param_args[0] == "Content-Length" || param_args[0] == "content-length"){

                                int len = atoi((param_args[1].substr(param_args[1].find(" ")+1)).c_str());
                                
                                for(int i = 0 ;i < len;i++){
                                    char dat[1];
                                    SSL_read(ssl,dat,1);

                                    post_data+=dat[0];
                                }
                                
                                break;

                            }
                           
                          }
                          std::cout<<"POST:"<<post_data<<std::endl;
                          string err = "";
                          string errmsg= "";
                          if(post_data.find("dev_info") == std::string::npos){
                              errmsg="{\"result\":\"INVALID_PARAMS\"}";

                              err = construct_https_result(errmsg)+errmsg;
                              cout<<err.length()<<endl;


                              SSL_write(ssl,err.c_str(),err.length());
                          }
                          else{
                            
                              std::vector<std::string> data = fetch_data_from_json(post_data);
                              if(write_cast_device(data) == -1){
                                  cout<<"ADDEDD!!"<<endl;  
                                  errmsg = "{\"result\":\"DEVICE_ALREADY_ADDED\"}";
                                  err =  construct_https_result(errmsg)+errmsg;
                                  cout<<err<<endl;
                                   cout<<err.length()<<endl;


                                  SSL_write(ssl,err.c_str(),err.length());
                              }
                              else{
                                  cout<<"DATA:"<<data[0]<<":"<<data[1]<<endl;
                                  errmsg="{\"result\":\"OK\"}";
                                  err = construct_https_result(errmsg)+errmsg;
                                  cout<<err.length()<<endl;

                                 SSL_write(ssl,err.c_str(),err.length());
                              }
                                                   
                          }
                        }
                        

                      
                    }

                }

                SSL_shutdown(ssl);
                SSL_free(ssl);
                close(clifd);
                exit(1);

             }
             
             close(clifd);

        }

      }
      
      int dispatch_socket(void){
        
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


        return sockfd;

      
      
      } 
    

};


int main(){

  char *prt_d = getenv("SERVER_PORT");
  if(prt_d == NULL){
    printf("\nSERVER_PORT not provided.\n");
    exit(1);
  }
  int port = atoi(prt_d );
  printf("\nrunning on port %d",port);
  WebServer *srv = new WebServer(port);
  srv->dispatch();


}




