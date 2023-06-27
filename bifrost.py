#!/usr/bin/env python
import os
import sys
import json
from datetime import datetime
import optparse
from colorama import Fore
import re
folder = os.path.dirname(os.path.abspath(__file__))+"/templates/"
sys.path.append(folder)
#import win_masm_32
import win_masm_64
folder = os.path.dirname(os.path.abspath(__file__))+"/procedures/"
sys.path.append(folder)
import win_masm_32_procedures
import win_masm_64_procedures
folder = os.path.dirname(os.path.abspath(__file__))+"/structures/"
sys.path.append(folder)
import win_masm_64_structures
import shutil

global configFileName
configFileName = "config.json"

global WHITE, GREEN, RED, YELLOW, CYAN, MAGENTA, RESET
WHITE = Fore.WHITE
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
RESET = Fore.RESET

global genDate
genDate = datetime.date(datetime.now())

global config
with open("./"+configFileName) as fp:
    config = json.load(fp)

global projectPath
projectPath = r'./projects/'+config["projectName"]
if not os.path.exists(projectPath):
    os.makedirs(projectPath)
else:
    print((YELLOW+"[*] project "+config["projectName"]+" already exist"))
    r = input(YELLOW+"[*] would you like to overwrite? [y/N] ")
    if r.lower() == "y":
        def removeFolder(path):
            # check if folder exists
            if os.path.exists(path):
                 # remove if exists
             shutil.rmtree(path)
        removeFolder(projectPath)
        os.makedirs(projectPath)
    else:
        print(RESET)
        sys.exit(1)


def createFile(filename, data):
    try:
        fp = open(filename, "w")
        if data != "":
            fp.write(data)
            print((GREEN+"[+] file "+filename+": CREATED"+RESET))
        else:
            print((RED+"[-] file "+filename+": CREATED but data EMPTY"+RESET))
        fp.close()
        return True
    except:
        print((RED+"[-] file "+filename+": NOT CREATED"+RESET))
        return False

def copyConfigFile(dst):
    try:
        shutil.copyfile("./"+configFileName, dst)
        print((GREEN+"[+] "+configFileName+" file: COPIED"+RESET))
    except:
        print((RED+"[-] "+configFileName+" file: NOT COPIED"+RESET))
        return False

def addToFile(filename, data):
    try:
        fp = open(filename, "a")
        if data != "":
            fp .write(data)
        fp.close()
        return True
    except Exception as e:
        print(str(e))
        print((RED+"[-] data NOT ADDED to "+filename+RESET))
        return False


def addProcedure64(filename, procedure):
    return getattr(win_masm_64_procedures, procedure)

def addStructure64(filename, structure):
    return getattr(win_masm_64_structures, structure)

def addData64(key, value):
    r = "\t{}\t\t\t{}\n".format(key, value)
    return r

def masmProjectWin64():

    try:
        
        copyConfigFile(projectPath+"/mlw.conf")

        createFile( projectPath+"/makeit.bat", win_masm_64.makeIt(config) )
        if config["appType2"] == "executable":
            createFile( projectPath+"/"+config["projectName"]+".asm", win_masm_64.mainExeFunc(config) )
        elif config["appType2"] == "dll":
            createFile( projectPath+"/"+config["projectName"]+".asm", win_masm_64.mainDllFunc(config) )
            createFile( projectPath+"/dll.def", win_masm_64.dlldef(config) )
        else:
            createFile( projectPath+"/"+config["projectName"]+".asm", win_masm_64.mainExeFunc(config) )
        createFile( projectPath+"/strings.inc", win_masm_64.moreStrings(config, genDate) )
        createFile( projectPath+"/datas.inc", win_masm_64.datas() )
        createFile( projectPath+"/structures.inc", win_masm_64.structures() )
        createFile( projectPath+"/procedures.inc", win_masm_64.procedures() )
        createFile( projectPath+"/README.md", "# "+config["projectName"] )
        
        try:
            for proc in config["procedures"]:
                try:
                    if proc != "":
                        addToFile( projectPath+"/procedures.inc", addProcedure64(projectPath+"/"+config["projectName"], proc) )
                        print((GREEN+"[+] procedure '"+proc+"' ADDED to "+projectPath+"/procedures.inc"+RESET))
                except Exception as e:
                    print(str(e))
                    print((RED+"[-] procedure '"+proc+"' NOT ADDED to "+projectPath+"/procedures.inc"+RESET))
        except:
            pass

        try:
            for struct in config["structures"]:
                try:
                    if struct != "":
                        addToFile( projectPath+"/structures.inc", addStructure64(projectPath+"/"+config["projectName"], struct) )
                        print((GREEN+"[+] structure '"+struct+"' ADDED to "+projectPath+"/structures.inc"+RESET))
                except Exception as e:
                    print(str(e))
                    print((RED+"[-] structure '"+struct+"' NOT ADDED to "+projectPath+"/structures.inc"+RESET))
        except:
            pass

        try:
            for key in config["datas"]:
                try:
                    if config["datas"][key] != "":
                        addToFile( projectPath+"/datas.inc", addData64(key, config["datas"][key]))
                        print((GREEN+"[+] data '"+key+" "+config["datas"][key]+"' ADDED to "+projectPath+"/datas.inc"+RESET))
                except Exception as e:
                    print(str(e))
                    print((RED+"[-] data '"+config["datas"][key]+"' NOT ADDED to "+projectPath+"/datas.inc"+RESET))
        except:
            pass
        return True
    except:
        return False



def main():

    ############################
    #
    # WINDOWS
    #
    ############################
    if config["os"] == "windows":
        print((GREEN+"[+] os selected: WINDOWS"+RESET))
        if config["architecture"] == "32":
            print((GREEN+"[+] 32 bits app: OK"+RESET))
            if config["language"] == "masm":
                print((GREEN+"[+] assembly language used: MASM32"+RESET))
                try:
                    #masmProjectWin32()
                    print((YELLOW+"\n[*] ok, let's have some fun now()"+RESET))
                except:
                    print((RED+"[-] some errors occured, i let you find why .."+RESET))

        elif config["architecture"] == "64":
            print((GREEN+"[+] 64 bits app: OK"+RESET))
            if config["language"] == "masm":
                print((GREEN+"[+] assembly language used: MASM64"+RESET))
                try:
                    masmProjectWin64()
                    print((YELLOW+"\n[*] ok, let's have some fun now()"+RESET))
                except:
                    print((RED+"[-] some errors occured, i let you find why .."+RESET))

        else:
            print((RED+"[-] 32 or 64"+RESET))

    ############################
    #
    # LINUX
    #
    ############################
    elif config["os"] == "linux":
        print((GREEN+"[+] os selected: LINUX"+RESET))

    ############################
    #
    # ANDROID
    #
    ############################
    elif config["os"] == "android":
        print((GREEN+"[+] os selected: ANDROID"+RESET))

    else:
        print((RED+"[-] os not supported"+RESET))


if __name__ == '__main__':
    main()
    print(RESET)