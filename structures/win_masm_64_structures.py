#/usr/bin/env python

THREADENTRY32 = r"""
_THREADENTRY32 STRUCT
    dwSize          DD ? 
    cntUsage        DD ? 
    th32ThreadID    DD ? 
    th32OwnerProcessID DD ? 
    tpBasePri       DD ? 
    tpDeltaPri      DD ? 
    dwFlags         DD ? 
_THREADENTRY32 ENDS
"""

CONTEXT = r"""
_CONTEXT STRUCT 16 ; align (16)
    P1Home      DQ ?
    P2Home      DQ ? 
    P3Home      DQ ?
    P4Home      DQ ?
    P5Home      DQ ?
    P6Home      DQ ?
    ContextFlags DD ?
    MxCsr       DD ?
    SegCs       DW ?
    SegDs       DW ?
    SegEs       DW ?
    SegFs       DW ?
    SegGs       DW ?
    SegSs       DW ?
    EFlags      DD ?
    _Dr0         DQ ?
    _Dr1         DQ ?
    _Dr2         DQ ?
    _Dr3         DQ ?
    _Dr6         DQ ?
    _Dr7         DQ ?
    _Rax         DQ ?
    _Rcx         DQ ?
    _Rdx         DQ ?
    _Rbx         DQ ?
    _Rsp         DQ ?
    _Rbp         DQ ?
    _Rsi         DQ ?
    _Rdi         DQ ?
    _R8          DQ ?
    _R9          DQ ?
    _R10         DQ ?
    _R11         DQ ?
    _R12         DQ ?
    _R13         DQ ?
    _R14         DQ ?
    _R15         DQ ?
    _Rip         DQ ?
    FltsSave    DB 200h DUP (?) ; dt -v _XSAVE_FORMAT
    Header      DB 20h DUP (?)  ; 2*_M128A ; dt -v _M128A 
    Legacy      DB 80h DUP (?)  ; 8*_M128A ; dt -v _M128A 
    _Xmm0        DB 10h DUP (?)  ; _M128A
    _Xmm1        DB 10h DUP (?)  ; _M128A
    _Xmm2        DB 10h DUP (?)  ; _M128A
    _Xmm3        DB 10h DUP (?)  ; _M128A
    _Xmm4        DB 10h DUP (?)  ; _M128A
    _Xmm5        DB 10h DUP (?)  ; _M128A
    _Xmm6        DB 10h DUP (?)  ; _M128A
    _Xmm7        DB 10h DUP (?)  ; _M128A
    _Xmm8        DB 10h DUP (?)  ; _M128A
    _Xmm9        DB 10h DUP (?)  ; _M128A
    _Xmm10       DB 10h DUP (?)  ; _M128A
    _Xmm11       DB 10h DUP (?)  ; _M128A
    _Xmm12       DB 10h DUP (?)  ; _M128A
    _Xmm13       DB 10h DUP (?)  ; _M128A
    _Xmm14       DB 10h DUP (?)  ; _M128A
    _Xmm15       DB 10h DUP (?)  ; _M128A
    VectorRegister      DB 260h DUP (?) ; 26*_M128A
    VectorControl       DQ ?
    DebugControl        DQ ?
    LastBranchToRip     DQ ?
    LastBranchFromRip   DQ ?
    LastExceptionToRip  DQ ?
    LastExceptionFromRip DQ ?
_CONTEXT ENDS
"""

STARTUPINFOA = r"""
; https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-startupinfoa
_STARTUPINFOA STRUCT
	cb    			DWORD ? ; 4
	padding1		DB 4 DUP (?) ; 8
	lpReserved    	QWORD ? ; 16
	lpDesktop    	QWORD ? ; 24
	lpTitle    		QWORD ? ; 32
	dwX    			DWORD ? ; 36
	dwY    			DWORD ? ; 40
	dwXSize    		DWORD ?	; 44
	dwYSize    		DWORD ? ; 48
	dwXCountChars   DWORD ?	; 52
	dwYCountChars   DWORD ?	; 56
	dwFillAttribute DWORD ?	; 60
	dwFlags    		DWORD ? ; 64
	wShowWindow    	WORD ? 	; 66
	cbReserved2    	WORD ? ; 68
	padding2		DB 4 DUP (?) ; 72
	lpReserved2    	QWORD ? ; 80
	hStdInput    	QWORD ? ; 88
	hStdOutput    	QWORD ? ; 96
	hStdError    	QWORD ? ; 104
_STARTUPINFOA ENDS
"""

STARTUPINFOEXA = r"""
; https://docs.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-startupinfoexa
_STARTUPINFOEXA STRUCT
	StartupInfo   	_STARTUPINFOA <>
	lpAttributeList QWORD ?
_STARTUPINFOEXA ENDS
"""

PROCESS_INFORMATION = r"""
; https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-process_information
_PROCESS_INFORMATION STRUCT 
	hProcess    	QWORD ?
	hThread    		QWORD ?
	dwProcessId    	QWORD ?
	dwThreadId    	QWORD ?
_PROCESS_INFORMATION ENDS
"""

PROCESS_BASIC_INFORMATION = r"""
_PROCESS_BASIC_INFORMATION STRUCT
	ExitStatus			DQ ?
    PebBaseAddress		DQ ?
    AffinityMask		DQ ?
    BasePriority		DQ ?
    UniqueProcessId		DQ ?
    InheritedFromUniqueProcessId DQ ?
_PROCESS_BASIC_INFORMATION ENDS
"""

IMAGE_FILE_HEADER = r"""
; https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_file_header
_IMAGE_FILE_HEADER STRUCT 
    Machine                 DW ?
    NumberOfSections        DW ?
    TimeDateStamp           DD ?
    PointerToSymbolTable    DD ?
    NumberOfSymbols         DD ?
    SizeOfOptionalHeader    DW ?
    Characteristics         DW ?
_IMAGE_FILE_HEADER ENDS 
"""

IMAGE_DATA_DIRECTORY = r"""
; https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_data_directory
_IMAGE_DATA_DIRECTORY STRUCT 
    VirtualAddress      DD ?
    _Size                DD ?
_IMAGE_DATA_DIRECTORY ENDS 
"""

IMAGE_OPTIONAL_HEADER64 = r"""
; https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_optional_header32
; dt _IMAGE_OPTIONAL_HEADER64
_IMAGE_OPTIONAL_HEADER64  STRUCT
    Magic               DW ?
    MajorLinkerVersion  DB ?
    MinorLinkerVersion  DB ?
    SizeOfCode          DD ?
    SizeOfInitializedData   DD ?
    SizeOfUninitializedData DD ?
    AddressOfEntryPoint     DD ?
    BaseOfCode          DD ?
    ImageBase           DQ ?
    SectionAlignment    DD ?
    FileAlignment       DD ?
    MajorOperatingSystemVersion DW ?
    MinorOperatingSystemVersion DW ?
    MajorImageVersion   DW ?
    MinorImageVersion   DW ?
    MajorSubsystemVersion   DW ?
    MinorSubsystemVersion   DW ?
    Win32VersionValue   DD ?
    SizeOfImage         DD ?
    SizeOfHeaders       DD ?
    CheckSum            DD ?
    Subsystem           DW ?
    DllCharacteristics  DW ?
    SizeOfStackReserve  DQ ?
    SizeOfStackCommit   DQ ?
    SizeOfHeapReserve   DQ ?
    SizeOfHeapCommit    DQ ?
    LoaderFlags         DD ?
    NumberOfRvaAndSizes DD ?
    DataDirectory       _IMAGE_DATA_DIRECTORY 16 DUP (<>)
_IMAGE_OPTIONAL_HEADER64  ENDS 
"""

IMAGE_NT_HEADERS64 = r"""
;https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_nt_headers32
_IMAGE_NT_HEADERS64 STRUCT
    Signature           DD ?
    FileHeader          _IMAGE_FILE_HEADER <>
    OptionalHeader64    _IMAGE_OPTIONAL_HEADER64 <> 
_IMAGE_NT_HEADERS64 ENDS
"""

IMAGE_SECTION_HEADER = r"""
; https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_section_header
_IMAGE_SECTION_HEADER STRUCT 
    Name                    DB 8 DUP (?)
    PhysicalAddress         DQ ?
    VirtualSize             DD ?
    VirtualAddress          DD ?
    SizeOfRawData           DD ?
    PointerToRawData        DD ?
    PointerToRelocations    DD ?
    PointerToLinenumbers    DD ?
    NumberOfRelocations     DW ?
    NumberOfLinenumbers     DW ?
    Characteristics         DD ?
_IMAGE_SECTION_HEADER ENDS 
"""

IMAGE_DIRECTORY_TABLE = r"""
_IMAGE_DIRECTORY_TABLE STRUCT 
    ImportLookupTableRVA    DD ?
    TimeDateStamp           DD ?
    ForwarderChain          DD ?
    NameRVA                 DD ?
    ImportAddressTableRVA   DD ?
_IMAGE_DIRECTORY_TABLE ENDS
"""