/*

  @title:  macOS Pasteboard backend
  @author: nitrodegen (Gavrilo Palalic)

  Copyright (c) 2023 Gavrilo Palalic

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

*/
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <iostream>
#import <AppKit/NSPasteboard.h>
#import <AppKit/AppKit.h>
#include <iostream>
#include <assert.h>

using namespace std;

class ClipboardControl{

  public:
    bool dbg;
    NSPasteboard *board;
    ClipboardControl(bool debug){
      dbg= debug;
      board = [NSPasteboard generalPasteboard];
      [board init];

      assert((board != NULL) && "board initialized with NULL");
      if(dbg){  
        printf("\nboard initialized %p\n",board);
      }

    }
    //returns 1 (true) if data was successfully written, else returns false.
    int copy_string_to_clipboard(char *x){
      [board clearContents];
      NSString *y = [NSString stringWithCString:x encoding:NSASCIIStringEncoding];
      [board declareTypes:[NSArray arrayWithObject:NSPasteboardTypeString] owner:nil];
      return [board setString:y forType:NSPasteboardTypeString];
    } 

    char* read_clipboard(void){
        NSString * o = [board stringForType:NSPasteboardTypeString];
        const char *out = [o UTF8String];


        return (char*)out;
    }


};

//Awful c-types just doesnt support C++ classes.

extern "C"{

    int copy_string_to_clipboard(char* x,int dbg){ 
      ClipboardControl *xd = new ClipboardControl(dbg);
      return xd->copy_string_to_clipboard(x);
    };
    char* read_clipboard(int dbg){ 
      ClipboardControl *xd = new ClipboardControl(dbg);
      return xd->read_clipboard();
    };

}