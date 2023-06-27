#!/usr/bin/env python
import os, sys
from datetime import datetime
from configobj import ConfigObj
import re
from colorama import Fore

global RED, RESET
RED = Fore.RED
RESET = Fore.RESET

def makeIt(config):
    defaultLib = ""
    for lib in config["imports"]["dll"]:
        defaultLib += "/defaultlib:\"" + config["libPath"] + lib + ".lib\" ^\n"

    if config["appType"] == "console":
        appType = "console"
    elif config["appType"] == "gui":
        appType = "window"
    else:
        appType = "console"


    compilerPath = config["compilerPath"]
    libPath = config["libPath"]
    
    if config["out"] == "release":
        release = "/release"
    elif config["out"] == "debug":
        release = "/debug"
    else:
        release = "/debug"


    if config["appType2"] == "executable":
        entry = "Start"
        makeItCode = r"""
@echo off

set prog={}

if exist %prog%.exe del %prog%.exe

"{}" ^
%prog%.asm /link ^
/subsystem:{} ^
{}
/entry:{} ^
/LARGEADDRESSAWARE:NO ^
/out:%prog%.exe ^
{} 

del *.obj
del *.lnk

pause
""".format(config["projectName"], compilerPath, appType, defaultLib, entry, release)


    elif config["appType2"] == "dll":
        entry = "LibMain"

        makeItCode = r"""
@echo off

set prog={}

if exist %prog%.exe del %prog%.exe
if exist %prog%.dll del %prog%.dll

"{}" ^
%prog%.asm /link ^
{}
/entry:{} ^
/out:%prog%.dll ^
{} ^
/DLL /DEF:dll.def

del *.obj
del *.lib
del *.exp
del *.lnk

pause
""".format(config["projectName"], compilerPath, defaultLib, entry, release)

    else:
        makeItCode = r"""
        """

    return makeItCode


def mainExeFunc(config):
    extrn = ""
    functionLabel = ""
    list_func = []
    for func in config["imports"]['function']:
        function_name = func
        num_parameter = config["imports"]["function"][func]

        if function_name not in list_func:
            list_func.append(function_name)
            extrn += "extrn {} :PROC\n".format(function_name)

        functionLabel += """
_{}:
""".format(function_name)
        try:

            if num_parameter == 0:
                s = 0
                functionLabel += """   
    ; DB 0CCh            
    CALL    {}
    ; CALL    GetLastError
""".format(function_name)
            elif num_parameter == 1:
                s = 1
                functionLabel += """   
    ;???     rcx, ?
    ; DB 0CCh
    CALL    {}
    ; CALL    GetLastError
""".format(function_name)
            elif num_parameter == 2:
                s = 2
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ; DB 0CCh
    CALL    {}
    ; CALL    GetLastError
""".format(function_name)
            elif num_parameter == 3:
                s = 3
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    ; DB 0CCh
    CALL    {}
    ; CALL    GetLastError
""".format(function_name)
            elif num_parameter == 4:
                s = 4
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    ;???     r9, ?
    ; DB 0CCh
    CALL    {}
    ; CALL    GetLastError
""".format(function_name)
            else:
                s = (num_parameter) * 8

                stack = ""
                for i in range(num_parameter-4):
                    stack += "    MOV     [rsp+{}], rax\n".format(32+(i*8))

                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    ;???     r9, ?
    SUB     rsp, {} ; {} more parameters
    XOR     rax, rax
{}  
    ; DB 0CCh
    CALL    {}
    ; CALL    GetLastError
    ADD     rsp, {}
""".format(s, num_parameter, stack, function_name, s)
        except Exception as e:
            print(str(e))


    projectCode = r"""
; {}.asm

extrn GetLastError :PROC
extrn ExitProcess :PROC
{}

include structures.inc

.data
include strings.inc
include datas.inc

.code
include procedures.inc

Start PROC
    SUB     rsp, 28h ; shadow space

    DB      0CCh ; INT3 - breakpoint

{}

; Exit the process gracefully
_exit:
    XOR     rcx, rcx
    CALL    ExitProcess

Start ENDP
End
""".format(config["projectName"], extrn, functionLabel)

    return projectCode

def mainDllFunc(config):
    extrn = ""
    functionLabel = ""
    for func in config["imports"]['function']:
        function_name = func
        num_parameter = config["imports"]['function'][func]

        extrn += "extrn {} :PROC\n".format(function_name)

        functionLabel += """
_{}:
""".format(function_name)
        try:

            if num_parameter == 0:
                s = 0
                functionLabel += """   
    CALL    {}
""".format(function_name)
            elif num_parameter == 1:
                s = 1
                functionLabel += """   
    ;???     rcx, ?
    CALL    {}
""".format(function_name)
            elif num_parameter == 2:
                s = 2
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    CALL    {}
""".format(function_name)
            elif num_parameter == 3:
                s = 3
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    CALL    {}
""".format(function_name)
            elif num_parameter == 4:
                s = 4
                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    ;???     r9, ?
    CALL    {}
""".format(function_name)
            else:
                s = (num_parameter - 4) * 8

                stack = ""
                for i in range(num_parameter-4):
                    stack += "    MOV     [rsp+{}], rax\n".format(32+(i*8))

                functionLabel += """   
    ;???     rcx, ?
    ;???     rdx, ?
    ;???     r8, ?
    ;???     r9, ?
    SUB     rsp, {} ; {} more parameters
    XOR     rax, rax
{}  
    CALL    {}
    ADD     rsp, {}
""".format(s, num_parameter - 4, stack, function_name, s)
        except Exception as e:
            print(str(e))


    projectCode = r"""
; {}.asm

extrn ExitProcess :PROC
{}

include structures.inc

.data
include strings.inc
include datas.inc

.code
include procedures.inc

LibMain PROC
    PUSH    rcx ; hInstDLL
    PUSH    rdx ; fdwReason
    PUSH    r8 ; lpReserved

    CMP     rdx, 1
    JE      DLL_PROCESS_ATTACH 
    CMP     rdx, 3
    JE      DLL_THREAD_DETACH
    CMP     rdx, 2
    JE      DLL_THREAD_ATTACH
    CMP     rdx, 0
    JE      DLL_PROCESS_DETACH
    JMP     _exit_ko

DLL_PROCESS_ATTACH:
    ;CALL    ...
    JMP     _exit_ok
DLL_THREAD_DETACH:
    ;CALL    ...
    JMP     _exit_ok
DLL_THREAD_ATTACH:
    ;CALL    ...
    JMP     _exit_ok
DLL_PROCESS_DETACH:
    ;CALL    ...
    JMP     _exit_ok

{}

_exit_ok:
    POP     r8 ; lpReserved
    POP     rdx ; fdwReason
    POP     rcx ; hInstDLL
    MOV     rax, 1  ; If the Windows loader receives a return code of 0 from DllMain, 
                    ; it will unload the library and call it a wash so the proper return value is critical.
    RET
_exit_ko:
    POP     r8 ; lpReserved
    POP     rdx ; fdwReason
    POP     rcx ; hInstDLL
    XOR     rax, rax
    RET

LibMain ENDP
End
""".format(config["projectName"], extrn, functionLabel)

    return projectCode


def moreStrings(config, genDate):
    moreStr = ""
    for strings_key in config["strings"]:
        moreStr += r"""
    {}      DB '{}', 0""".format(strings_key, config["strings"][strings_key])

    stringsCode = r"""
; strings

    author      DB '{}',0
    email       DB '{}', 0
    date        DB '{}',0
    society     DB '{}',0

    {}
""".format(config["author"], config["email"], genDate, config["society"], moreStr)

    return stringsCode

def dlldef(config):
    datasCode = r"""
LIBRARY {}
EXPORTS LibMain
""".format(config["projectName"])

    return datasCode

def datas():
    datasCode =  r"""
; datas.inc

"""

    return datasCode

def structures():
    structuresCode = r"""
; structures.inc

"""

    return structuresCode

# at procdures.inc creation 
def procedures():
    proceduresCode = r"""
; procedures.inc

"""

    return proceduresCode

