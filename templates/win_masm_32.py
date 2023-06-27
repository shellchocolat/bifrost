#!/usr/bin/env python
import os, sys
from datetime import datetime
from configobj import ConfigObj
import re
from colorama import Fore

global RED, RESET
RED = Fore.RED
RESET = Fore.RESET

def makeIt(config, appType):

    if config["appType2"] == "executable":
        appType2 = "/MERGE:.rdata=.text %prog%.obj > nul"
    elif config["appType2"] == "dll":
        appType2 = "/DLL DEF:%prog%.def %prog%.obj > nul"
    else:
        appType2 = "/MERGE:.rdata=.text %prog%.obj > nul"

    makeItCode = r"""
@echo off

set prog={}

if exist %prog%.exe del %prog%.exe

\masm32\bin\ml /c /coff /nologo %prog%.asm
\masm32\bin\Link /SUBSYSTEM:{} {}

del %prog%.obj

pause
""".format(config["projectName"], appType, appType2)

    return makeItCode

def mainFunc(config):
    include = r"""
;include \masm32\include\windows.inc
include \masm32\include\masm32rt.inc
"""
    for dll in config["imports"]['dll']:
        if ".dll" in dll.lower():
            dll = re.sub(".dll",".inc", dll)
        include += r"include \masm32\include\{}".format(dll)
        include += "\n"
    else:
        pass

    includelib = r"""
;includelib \masm32\lib\masm32.lib
"""
    for dll in config["imports"]['dll']:
        if ".dll" in dll.lower():
            dll = re.sub(".dll",".lib", dll)
        includelib += r"includelib \masm32\lib\{}".format(dll)
        includelib += "\n"
    else:
        pass

    functionLabel = r""
    func_found = False
    for func in config["imports"]['function']:

        # find the number of argument of the function
        # find in each DLL if the function exist then find arguments
        for dll in config["imports"]['dll']:
            if ".dll" in dll.lower():
                dll = re.sub(".dll",".inc", dll)
            else:
                dll += ".inc"

            fp = open("./templates/masm32_include/"+dll.lower(), "r")

            lines = fp.readlines()
            fp.close()
            for line in lines:
                if func.lower() in line.lower(): # the CHECK is HERE !!!
                    # we count the number of : to determine the number of argument of the function
                    num_arg = line.count(":")
                    func_found = True
                    break
                else:
                    num_arg = -1
                    func_found = False

            if func_found == True: # if the function is found so break
                break
        else:
            num_arg = -1 # no dll provided, so function cannot be found, so num_arg = -1
        
        if num_arg != -1:
            arg = ""
            for i in range(0,num_arg):
                arg += """
    push"""

            functionLabel += """
_{}:
    {}
    call    {}
""".format(func, arg, func)

        else:
            print((RED+"[-] the function "+func+" has not been found into the DLLs provided"+RESET))

    functionLabel += """
; Exit the process gracefully
_ExitProcess:

    xor     eax, eax
    push    eax
    call    ExitProcess
"""

    projectCode = r"""
.586
;.model flat, stdcall
option casemap:none
{}
{}

.data

include strings.inc
include equates.inc
include datas.inc
include protos.inc

.code

include procedures.inc

start:
_SIGNATURE:
    push    offset author
    push    offset email
    push    offset date
    push    offset society
    pop     eax
    pop     eax
    pop     eax
    pop     eax

{}

end start
""".format(include, includelib, functionLabel)

    return projectCode

def moreStrings(config, genDate):
    moreStr = ""
    for strings_key in config["strings"]:
        moreStr += r"""
{}      db  '{}', 0""".format(strings_key, config["strings"][strings_key])

    stringsCode = r"""
author      db  '{}',0
email       db  '{}', 0
date        db  '{}',0
society     db  '{}',0

{}
""".format(config["author"], config["email"], genDate, config["society"], moreStr)

    return stringsCode


def equates():
    equatesCode = r"""
    """

    return equatesCode

def datas():
    datasCode = r"""
    """

    return datasCode

def protos():
    protosCode = r"""
    """

    return protosCode

# at procdures.inc creation 
def procedures():
    proceduresCode = r"""
    """

    return proceduresCode

