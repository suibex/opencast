#!/bin/bash
clang++ copy.mm -framework AppKit -std=c++11 -fPIC -shared -o clip.so
