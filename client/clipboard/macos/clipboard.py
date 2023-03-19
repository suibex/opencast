"""

    @title:  Python wrapper for NSPasteboard controller
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

"""
from ctypes import * 
import os,io,sys

class Clipboard:
    def __init__(self,dbg,path) -> None:
        self.dbg= dbg
        self.shared_lib =CDLL(path)
    
    def read_clipboard(self):
        self.shared_lib.read_clipboard.restype = POINTER(c_char)
        out = self.shared_lib.read_clipboard(self.dbg)
        out = cast(out,c_char_p).value
        return out
    
    def set_string(self,dat):
        dat = dat.encode('utf-8')
        return self.shared_lib.copy_string_to_clipboard(dat,1)

clip = Clipboard(1,"./clip.so")
clip.set_string("hello")


