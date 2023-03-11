#!/bin/bash
SSL_INCLUDE=/opt/homebrew/Cellar/openssl@3/3.0.7/include ;
SSL_LIBS=/opt/homebrew/Cellar/openssl@3/3.0.7/lib;

clang++ server.cc -o web_srvr -std=c++11 -I $SSL_INCLUDE -L $SSL_LIBS -lssl -lcrypto;
./web_srvr;

