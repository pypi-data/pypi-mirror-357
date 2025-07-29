#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements a basic PE loader in python to
#    load executables in memory.
#    Copyright (C) 2025  PyPeLoader

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements a basic PE loader in python to
load executables in memory.
"""

__version__ = "1.0.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements a basic PE loader in python to
load executables in memory.
"""
__url__ = "https://github.com/mauricelambert/PyPeLoader"

__all__ = [
    "main",
    "load",
    "load_headers",
    "load_in_memory",
    "load_imports",
    "get_imports",
    "load_relocations",
    "ImportFunction",
    "get_peb",
    "modify_process_informations",
    "modify_executable_path_name",
    "set_command_lines",
]

__license__ = "GPL-3.0 License"
__copyright__ = """
PyPeLoader  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

from ctypes import (
    LittleEndianStructure,
    Structure,
    Union,
    WinDLL,
    WinError,
    get_last_error,
    wstring_at,
    cast,
    memmove,
    memset,
    sizeof,
    addressof,
    byref,
    pointer,
    POINTER,
    CFUNCTYPE,
    windll,
    c_ubyte,
    c_byte,
    c_int,
    c_uint32,
    c_uint16,
    c_uint64,
    c_uint8,
    c_long,
    c_ulong,
    c_ulonglong,
    c_void_p,
    create_unicode_buffer,
    create_string_buffer,
    c_char,
    c_wchar_p,
    c_size_t,
    c_bool,
)
from ctypes.wintypes import (
    LPVOID,
    LPCVOID,
    HMODULE,
    HANDLE,
    LARGE_INTEGER,
    DWORD,
    ULONG,
    USHORT,
    BYTE,
    BOOL,
    LPCWSTR,
    LPCSTR,
    LPWSTR,
)
from typing import Union as UnionType, Tuple, Iterable, List, Callable
from sys import argv, executable, exit, stderr
from os.path import isfile, basename, abspath
from dataclasses import dataclass
from _io import _BufferedIOBase


class IMAGE_DOS_HEADER(Structure):
    """
    This class implements the structure to parses the DOS Headers.
    """

    _fields_ = [
        ("e_magic", c_uint16),
        ("e_cblp", c_uint16),
        ("e_cp", c_uint16),
        ("e_crlc", c_uint16),
        ("e_cparhdr", c_uint16),
        ("e_minalloc", c_uint16),
        ("e_maxalloc", c_uint16),
        ("e_ss", c_uint16),
        ("e_sp", c_uint16),
        ("e_csum", c_uint16),
        ("e_ip", c_uint16),
        ("e_cs", c_uint16),
        ("e_lfarlc", c_uint16),
        ("e_ovno", c_uint16),
        ("e_res", c_uint16 * 4),
        ("e_oemid", c_uint16),
        ("e_oeminfo", c_uint16),
        ("e_res2", c_uint16 * 10),
        ("e_lfanew", c_uint32),
    ]


class IMAGE_FILE_HEADER(Structure):
    """
    This class implements the structure to parses the FILE Headers.
    """

    _fields_ = [
        ("Machine", c_uint16),
        ("NumberOfSections", c_uint16),
        ("TimeDateStamp", c_uint32),
        ("PointerToSymbolTable", c_uint32),
        ("NumberOfSymbols", c_uint32),
        ("SizeOfOptionalHeader", c_uint16),
        ("Characteristics", c_uint16),
    ]


class IMAGE_DATA_DIRECTORY(Structure):
    """
    This class implements the structure to parses data directories.
    """

    _fields_ = [("VirtualAddress", c_uint32), ("Size", c_uint32)]


class IMAGE_OPTIONAL_HEADER32(Structure):
    """
    This class implements the structure to parses x86 optional headers.
    """

    _fields_ = [
        ("Magic", c_uint16),
        ("MajorLinkerVersion", c_uint8),
        ("MinorLinkerVersion", c_uint8),
        ("SizeOfCode", c_uint32),
        ("SizeOfInitializedData", c_uint32),
        ("SizeOfUninitializedData", c_uint32),
        ("AddressOfEntryPoint", c_uint32),
        ("BaseOfCode", c_uint32),
        ("BaseOfData", c_uint32),
        ("ImageBase", c_uint32),
        ("SectionAlignment", c_uint32),
        ("FileAlignment", c_uint32),
        ("MajorOperatingSystemVersion", c_uint16),
        ("MinorOperatingSystemVersion", c_uint16),
        ("MajorImageVersion", c_uint16),
        ("MinorImageVersion", c_uint16),
        ("MajorSubsystemVersion", c_uint16),
        ("MinorSubsystemVersion", c_uint16),
        ("Win32VersionValue", c_uint32),
        ("SizeOfImage", c_uint32),
        ("SizeOfHeaders", c_uint32),
        ("CheckSum", c_uint32),
        ("Subsystem", c_uint16),
        ("DllCharacteristics", c_uint16),
        ("SizeOfStackReserve", c_uint32),
        ("SizeOfStackCommit", c_uint32),
        ("SizeOfHeapReserve", c_uint32),
        ("SizeOfHeapCommit", c_uint32),
        ("LoaderFlags", c_uint32),
        ("NumberOfRvaAndSizes", c_uint32),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * 16),
    ]


class IMAGE_OPTIONAL_HEADER64(Structure):
    """
    This class implements the structure to parses x64 optional headers.
    """

    _fields_ = [
        ("Magic", c_uint16),
        ("MajorLinkerVersion", c_uint8),
        ("MinorLinkerVersion", c_uint8),
        ("SizeOfCode", c_uint32),
        ("SizeOfInitializedData", c_uint32),
        ("SizeOfUninitializedData", c_uint32),
        ("AddressOfEntryPoint", c_uint32),
        ("BaseOfCode", c_uint32),
        ("ImageBase", c_uint64),
        ("SectionAlignment", c_uint32),
        ("FileAlignment", c_uint32),
        ("MajorOperatingSystemVersion", c_uint16),
        ("MinorOperatingSystemVersion", c_uint16),
        ("MajorImageVersion", c_uint16),
        ("MinorImageVersion", c_uint16),
        ("MajorSubsystemVersion", c_uint16),
        ("MinorSubsystemVersion", c_uint16),
        ("Win32VersionValue", c_uint32),
        ("SizeOfImage", c_uint32),
        ("SizeOfHeaders", c_uint32),
        ("CheckSum", c_uint32),
        ("Subsystem", c_uint16),
        ("DllCharacteristics", c_uint16),
        ("SizeOfStackReserve", c_uint64),
        ("SizeOfStackCommit", c_uint64),
        ("SizeOfHeapReserve", c_uint64),
        ("SizeOfHeapCommit", c_uint64),
        ("LoaderFlags", c_uint32),
        ("NumberOfRvaAndSizes", c_uint32),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * 16),
    ]


class IMAGE_NT_HEADERS(Structure):
    """
    This class implements the structure to parses the NT headers.
    """

    _fields_ = [
        ("Signature", c_uint32),
        ("FileHeader", IMAGE_FILE_HEADER),
        ("OptionalHeader", IMAGE_OPTIONAL_HEADER32),
    ]


class IMAGE_SECTION_HEADER(Structure):
    """
    This class implements the structure to parses sections headers.
    """

    _fields_ = [
        ("Name", c_char * 8),
        ("Misc", c_uint32),
        ("VirtualAddress", c_uint32),
        ("SizeOfRawData", c_uint32),
        ("PointerToRawData", c_uint32),
        ("PointerToRelocations", c_uint32),
        ("PointerToLinenumbers", c_uint32),
        ("NumberOfRelocations", c_uint16),
        ("NumberOfLinenumbers", c_uint16),
        ("Characteristics", c_uint32),
    ]


class IMAGE_IMPORT_DESCRIPTOR_MISC(Union):
    """
    This class implements the union to get the import misc.
    """

    _fields_ = [
        ("Characteristics", c_uint32),
        ("OriginalFirstThunk", c_uint32),
    ]


class IMAGE_IMPORT_DESCRIPTOR(Structure):
    """
    This class implements the structure to parses imports.
    """

    _fields_ = [
        ("Misc", IMAGE_IMPORT_DESCRIPTOR_MISC),
        ("TimeDateStamp", c_uint32),
        ("ForwarderChain", c_uint32),
        ("Name", c_uint32),
        ("FirstThunk", c_uint32),
    ]


class IMAGE_IMPORT_BY_NAME(Structure):
    """
    This class implements the structure to parses imports names.
    """

    _fields_ = [("Hint", c_uint16), ("Name", c_char * 12)]


class IMAGE_THUNK_DATA_UNION64(Union):
    """
    This class implements the union to access x64 imports values.
    """

    _fields_ = [
        ("Function", c_uint64),
        ("Ordinal", c_uint64),
        ("AddressOfData", c_uint64),
        ("ForwarderString", c_uint64),
    ]


class IMAGE_THUNK_DATA_UNION32(Union):
    """
    This class implements the union to access x84 imports values.
    """

    _fields_ = [
        ("Function", c_uint32),
        ("Ordinal", c_uint32),
        ("AddressOfData", c_uint32),
        ("ForwarderString", c_uint32),
    ]


class IMAGE_THUNK_DATA64(Structure):
    """
    This class implements the structure to parses the x64 imports values.
    """

    _fields_ = [("u1", IMAGE_THUNK_DATA_UNION64)]


class IMAGE_THUNK_DATA32(Structure):
    """
    This class implements the structure to parses the x86 imports values.
    """

    _fields_ = [("u1", IMAGE_THUNK_DATA_UNION32)]


class IMAGE_BASE_RELOCATION(Structure):
    """
    This class implements the structure to parses relocations.
    """

    _fields_ = [
        ("VirtualAddress", c_uint32),
        ("SizeOfBlock", c_uint32),
    ]


ULONG_PTR = c_uint64
SIZE_T = c_size_t
PVOID = c_void_p


class LIST_ENTRY(Structure):
    """
    This class implements the structure to parse
    modules list in memory.
    """

    # _fields_ = [("Flink", PVOID), ("Blink", PVOID)]


LIST_ENTRY._fields_ = [
    ("Flink", POINTER(LIST_ENTRY)),
    ("Blink", POINTER(LIST_ENTRY)),
]


class PEB_LDR_DATA(Structure):
    """
    This class implements the structure
    where modules list are stored.
    """

    _fields_ = [
        ("Length", ULONG),
        ("Initialized", BOOL),
        ("SsHandle", c_void_p),
        ("InLoadOrderModuleList", LIST_ENTRY),
        ("InMemoryOrderModuleList", LIST_ENTRY),
        ("InInitializationOrderModuleList", LIST_ENTRY),
        ("EntryInProgress", c_void_p),
        ("ShutdownInProgress", BOOL),
        ("ShutdownThreadId", c_void_p),
    ]


class LeapSecondFlagsBits(LittleEndianStructure):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [
        ("SixtySecondEnabled", ULONG, 1),
        ("Reserved", ULONG, 31),
    ]


class LeapSecondFlagsUnion(Union):
    """
    This class implements a structure in the PEB.
    """

    _anonymous_ = ("Bits",)
    _fields_ = [
        ("Value", ULONG),
        ("Bits", LeapSecondFlagsBits),
    ]


class TracingFlagsBits(LittleEndianStructure):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [
        ("HeapTracingEnabled", ULONG, 1),
        ("CritSecTracingEnabled", ULONG, 1),
        ("LibLoaderTracingEnabled", ULONG, 1),
        ("SpareTracingBits", ULONG, 29),
    ]


class TracingFlagsUnion(Union):
    """
    This class implements a structure in the PEB.
    """

    _anonymous_ = ("Bits",)
    _fields_ = [
        ("Value", ULONG),
        ("Bits", TracingFlagsBits),
    ]


class CallbackTableUnion(Union):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [
        ("KernelCallbackTable", c_void_p),
        ("UserSharedInfoPtr", c_void_p),
    ]


class BitFieldBits(LittleEndianStructure):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [
        ("ImageUsesLargePages", BYTE, 1),
        ("IsProtectedProcess", BYTE, 1),
        ("IsLegacyProcess", BYTE, 1),
        ("IsImageDynamicallyRelocated", BYTE, 1),
        ("SkipPatchingUser32Forwarders", BYTE, 1),
        ("SpareBits", BYTE, 3),
    ]


class BitFieldUnion(Union):
    """
    This class implements a structure in the PEB.
    """

    _anonymous_ = ("Bits",)
    _fields_ = [
        ("Value", BYTE),
        ("Bits", BitFieldBits),
    ]


class CrossProcessFlagsBits(LittleEndianStructure):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [
        ("ProcessInJob", ULONG, 1),
        ("ProcessInitializing", ULONG, 1),
        ("ProcessUsingVEH", ULONG, 1),
        ("ProcessUsingVCH", ULONG, 1),
        ("ProcessUsingFTH", ULONG, 1),
        ("ReservedBits0", ULONG, 27),
    ]


class CrossProcessFlagsUnion(Union):
    """
    This class implements a structure in the PEB.
    """

    _anonymous_ = ("Bits",)
    _fields_ = [
        ("Value", ULONG),
        ("Bits", CrossProcessFlagsBits),
    ]


class UNICODE_STRING(Structure):
    """
    This class implements the unicode strings to get
    Windows internal strings in memory.
    """

    _fields_ = [
        ("Length", USHORT),
        ("MaximumLength", USHORT),
        ("Buffer", LPWSTR),
    ]


class RTL_USER_PROCESS_PARAMETERS(Structure):
    """
    This class implements a structure to parse user paramaters
    like command line and executable full path.
    """

    _fields_ = [
        ("MaximumLength", ULONG),
        ("Length", ULONG),
        ("Flags", ULONG),
        ("DebugFlags", ULONG),
        ("ConsoleHandle", HANDLE),
        ("ConsoleFlags", ULONG),
        ("StandardInput", HANDLE),
        ("StandardOutput", HANDLE),
        ("StandardError", HANDLE),
        ("CurrentDirectoryPath", UNICODE_STRING),
        ("CurrentDirectoryHandle", HANDLE),
        ("DllPath", UNICODE_STRING),
        ("ImagePathName", UNICODE_STRING),
        ("CommandLine", UNICODE_STRING),
        ("Environment", c_void_p),
        ("StartingX", ULONG),
        ("StartingY", ULONG),
        ("CountX", ULONG),
        ("CountY", ULONG),
        ("CountCharsX", ULONG),
        ("CountCharsY", ULONG),
        ("FillAttribute", ULONG),
        ("WindowFlags", ULONG),
        ("ShowWindowFlags", ULONG),
        ("WindowTitle", UNICODE_STRING),
        ("DesktopInfo", UNICODE_STRING),
        ("ShellInfo", UNICODE_STRING),
        ("RuntimeData", UNICODE_STRING),
        ("CurrentDirectories", c_byte * 0x40),  # maxlength ~32 or 64
        ("EnvironmentSize", ULONG),
        ("EnvironmentVersion", ULONG),
        ("PackageDependencyData", c_void_p),
        ("ProcessGroupId", ULONG),
        ("LoaderThreads", ULONG),
        ("RedirectionDllName", UNICODE_STRING),
        ("HeapPartitionName", UNICODE_STRING),
    ]


class GDI_HANDLE_BUFFER(Structure):
    """
    This class implements a structure in the PEB.
    """

    _fields_ = [("Buffer", ULONG * 60)]  # 60 for 64-bit


PRTL_USER_PROCESS_PARAMETERS = POINTER(RTL_USER_PROCESS_PARAMETERS)


class PEB(Structure):
    """
    This class implements the PEB.
    """

    _anonymous_ = (
        "BitField",
        "CrossProcessFlags",
        "CallbackTable",
        "TracingFlags",
        "LeapSecondFlags",
    )
    _fields_ = [
        ("InheritedAddressSpace", BYTE),
        ("ReadImageFileExecOptions", BYTE),
        ("BeingDebugged", BYTE),
        ("BitField", BitFieldUnion),
        ("Mutant", HANDLE),
        ("ImageBaseAddress", PVOID),
        ("Ldr", POINTER(PEB_LDR_DATA)),
        ("ProcessParameters", PRTL_USER_PROCESS_PARAMETERS),
        ("SubSystemData", PVOID),
        ("ProcessHeap", PVOID),
        ("FastPebLock", PVOID),
        ("AtlThunkSListPtr", PVOID),
        ("IFEOKey", PVOID),
        ("CrossProcessFlags", CrossProcessFlagsUnion),
        ("CallbackTable", CallbackTableUnion),
        ("SystemReserved", ULONG * 1),
        ("AtlThunkSListPtr32", ULONG),
        ("ApiSetMap", PVOID),
        ("TlsExpansionCounter", ULONG),
        ("TlsBitmap", PVOID),
        ("TlsBitmapBits", ULONG * 2),
        ("ReadOnlySharedMemoryBase", PVOID),
        ("SharedData", PVOID),
        ("ReadOnlyStaticServerData", PVOID),
        ("AnsiCodePageData", PVOID),
        ("OemCodePageData", PVOID),
        ("UnicodeCaseTableData", PVOID),
        ("NumberOfProcessors", ULONG),
        ("NtGlobalFlag", ULONG),
        ("CriticalSectionTimeout", LARGE_INTEGER),
        ("HeapSegmentReserve", SIZE_T),
        ("HeapSegmentCommit", SIZE_T),
        ("HeapDeCommitTotalFreeThreshold", SIZE_T),
        ("HeapDeCommitFreeBlockThreshold", SIZE_T),
        ("NumberOfHeaps", ULONG),
        ("MaximumNumberOfHeaps", ULONG),
        ("ProcessHeaps", PVOID),
        ("GdiSharedHandleTable", PVOID),
        ("ProcessStarterHelper", PVOID),
        ("GdiDCAttributeList", ULONG),
        ("LoaderLock", PVOID),
        ("OSMajorVersion", ULONG),
        ("OSMinorVersion", ULONG),
        ("OSBuildNumber", USHORT),
        ("OSCSDVersion", USHORT),
        ("OSPlatformId", ULONG),
        ("ImageSubsystem", ULONG),
        ("ImageSubsystemMajorVersion", ULONG),
        ("ImageSubsystemMinorVersion", ULONG),
        ("ActiveProcessAffinityMask", ULONG_PTR),
        ("GdiHandleBuffer", GDI_HANDLE_BUFFER),
        ("PostProcessInitRoutine", PVOID),
        ("TlsExpansionBitmap", PVOID),
        ("TlsExpansionBitmapBits", ULONG * 32),
        ("SessionId", ULONG),
        ("AppCompatFlags", c_ulonglong),
        ("AppCompatFlagsUser", c_ulonglong),
        ("pShimData", PVOID),
        ("AppCompatInfo", PVOID),
        ("CSDVersion", UNICODE_STRING),
        ("ActivationContextData", PVOID),
        ("ProcessAssemblyStorageMap", PVOID),
        ("SystemDefaultActivationContextData", PVOID),
        ("SystemAssemblyStorageMap", PVOID),
        ("MinimumStackCommit", SIZE_T),
        ("SparePointers", PVOID * 4),
        ("SpareUlongs", ULONG * 5),
        ("WerRegistrationData", PVOID),
        ("WerShipAssertPtr", PVOID),
        ("pUnused", PVOID),
        ("pImageHeaderHash", PVOID),
        ("TracingFlags", TracingFlagsUnion),
        ("CsrServerReadOnlySharedMemoryBase", c_ulonglong),
        ("TppWorkerpListLock", PVOID),
        ("TppWorkerpList", LIST_ENTRY),
        ("WaitOnAddressHashTable", PVOID * 128),
        ("TelemetryCoverageHeader", PVOID),
        ("CloudFileFlags", ULONG),
        ("CloudFileDiagFlags", ULONG),
        ("PlaceholderCompatibilityMode", BYTE),
        ("PlaceholderCompatibilityModeReserved", BYTE * 7),
        ("LeapSecondData", PVOID),
        ("LeapSecondFlags", LeapSecondFlagsUnion),
        ("NtGlobalFlag2", ULONG),
    ]


class LDR_DATA_TABLE_ENTRY(Structure):
    """
    This class contains informations about module and list
    order to retrieves and identify modules in memory.
    """

    _fields_ = [
        ("InLoadOrderLinks", LIST_ENTRY),
        ("InMemoryOrderLinks", LIST_ENTRY),
        ("InInitializationOrderLinks", LIST_ENTRY),
        ("DllBase", PVOID),
        ("EntryPoint", PVOID),
        ("SizeOfImage", ULONG),
        ("FullDllName", UNICODE_STRING),
        ("BaseDllName", UNICODE_STRING),
    ]


class PROCESS_BASIC_INFORMATION(Structure):
    """
    This class implements the structure to get
    the PEB from NtQueryInformationProcess.
    """

    _fields_ = [
        ("Reserved1", c_void_p),
        ("PebBaseAddress", c_void_p),
        ("Reserved2", c_void_p * 2),
        ("UniqueProcessId", c_void_p),
        ("Reserved3", c_void_p),
    ]


@dataclass
class PeHeaders:
    """
    This dataclass store the PE Headers useful values.
    """

    dos: IMAGE_DOS_HEADER
    nt: IMAGE_NT_HEADERS
    file: IMAGE_FILE_HEADER
    optional: UnionType[IMAGE_OPTIONAL_HEADER32, IMAGE_OPTIONAL_HEADER64]
    sections: IMAGE_SECTION_HEADER * 1
    arch: int


@dataclass
class ImportFunction:
    """
    This dataclass store informations about a import function.
    """

    name: UnionType[int, str]
    module_name: str
    module: int
    address: int
    import_address: int
    module_container: str
    hook: Callable = None
    count_call: int = 0


IMAGE_REL_BASED_ABSOLUTE = 0
IMAGE_REL_BASED_HIGH = 1
IMAGE_REL_BASED_LOW = 2
IMAGE_REL_BASED_HIGHLOW = 3
IMAGE_REL_BASED_HIGHADJ = 4
IMAGE_REL_BASED_MIPS_JMPADDR = 5
IMAGE_REL_BASED_ARM_MOV32 = 5
IMAGE_REL_BASED_RISCV_HIGH20 = 5
IMAGE_REL_BASED_THUMB_MOV32 = 7
IMAGE_REL_BASED_RISCV_LOW12I = 7
IMAGE_REL_BASED_RISCV_LOW12S = 8
IMAGE_REL_BASED_LOONGARCH32_MARK_LA = 8
IMAGE_REL_BASED_LOONGARCH64_MARK_LA = 8
IMAGE_REL_BASED_MIPS_JMPADDR16 = 9
IMAGE_REL_BASED_DIR64 = 10

IMAGE_DIRECTORY_ENTRY_IMPORT = 0x01
IMAGE_DIRECTORY_ENTRY_BASERELOC = 0x05

MEM_RESERVE = 0x2000
MEM_COMMIT = 0x1000

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08

PAGE_GUARD = 0x100
PAGE_NOCACHE = 0x200
PAGE_WRITECOMBINE = 0x400

PROCESS_BASIC_INFORMATION_TYPE = 0

IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE = 0x0040

kernel32 = windll.kernel32
ntdll = WinDLL("ntdll")

NTSTATUS = c_long

NtQueryInformationProcess = ntdll.NtQueryInformationProcess
NtQueryInformationProcess.argtypes = [
    HANDLE,
    ULONG,
    c_void_p,
    ULONG,
    POINTER(ULONG),
]
NtQueryInformationProcess.restype = NTSTATUS

GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = HANDLE

GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.argtypes = [LPCWSTR]
GetModuleHandleW.restype = HMODULE

LoadLibraryA = kernel32.LoadLibraryA
LoadLibraryA.restype = HMODULE
LoadLibraryA.argtypes = [LPCSTR]

GetProcAddress = kernel32.GetProcAddress
GetProcAddress.argtypes = [HMODULE, LPCSTR]
GetProcAddress.restype = LPVOID

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.restype = LPVOID
VirtualAlloc.argtypes = [
    c_void_p,
    c_size_t,
    c_ulong,
    c_ulong,
]

VirtualProtect = kernel32.VirtualProtect
VirtualProtect.restype = c_bool
VirtualProtect.argtypes = [
    c_void_p,
    c_size_t,
    c_ulong,
    POINTER(c_ulong),
]

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    HANDLE,
    LPCVOID,
    LPVOID,
    c_size_t,
    POINTER(c_size_t),
]
ReadProcessMemory.restype = BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
WriteProcessMemory.argtypes = [
    HANDLE,            # hProcess
    LPVOID,            # lpBaseAddress
    LPCVOID,           # lpBuffer
    c_size_t,          # nSize
    POINTER(c_size_t)  # lpNumberOfBytesWritten
]


def get_peb() -> PEB:
    """
    This function gets PEB from NtQueryInformationProcess.
    """

    process_basic_information = PROCESS_BASIC_INFORMATION()
    return_length = ULONG()

    current_process = GetCurrentProcess()

    status = NtQueryInformationProcess(
        current_process,
        PROCESS_BASIC_INFORMATION_TYPE,
        byref(process_basic_information),
        sizeof(process_basic_information),
        byref(return_length),
    )

    if status != 0:
        raise OSError("NtQueryInformationProcess failed")

    return cast(
        process_basic_information.PebBaseAddress, POINTER(PEB)
    ).contents


def make_writable(address: int, size: int) -> int:
    """
    This function modify permissions on a memory area.
    """

    old_protect = DWORD()
    if not VirtualProtect(address, size, PAGE_READWRITE, byref(old_protect)):
        raise OSError("VirtualProtect failed")
    return old_protect.value


def restore_protection(address: int, size: int, old_protect: int) -> None:
    """
    This function restore permissions on the memory area.
    """

    temp = DWORD()
    VirtualProtect(address, size, old_protect, byref(temp))


def modify_unicode_string_from_parent(
    parent_address: POINTER, unicode_string_attribut_name: str, new_value: str
) -> None:
    """
    This function modify a unicode strings attribut from a parent
    structure pointer.
    """

    parent_structure = parent_address.contents
    structure_size = sizeof(parent_structure)

    string_size = len(new_value) * 2
    size_in_bytes = string_size + 2

    new_string_pointer = VirtualAlloc(
        None, size_in_bytes, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    if not new_string_pointer:
        raise WinError()

    buffer = create_unicode_buffer(new_value)
    memmove(new_string_pointer, buffer, size_in_bytes)

    unicode_string = getattr(parent_structure, unicode_string_attribut_name)
    old_protect = make_writable(parent_address, structure_size)

    unicode_string.Buffer = cast(new_string_pointer, c_wchar_p)
    unicode_string.Length = string_size
    unicode_string.MaximumLength = size_in_bytes

    setattr(parent_structure, unicode_string_attribut_name, unicode_string)
    restore_protection(parent_address, structure_size, old_protect)


def modify_process_informations(
    peb: PEB, executable_path: str, command_line: str
) -> None:
    """
    This function modify the unicode strings
    for command line and executable full path.
    """

    user_parameters = peb.ProcessParameters
    modify_unicode_string_from_parent(
        user_parameters, "ImagePathName", executable_path
    )
    modify_unicode_string_from_parent(
        user_parameters, "CommandLine", command_line
    )


def containing_record(
    address: int, struct_type: Structure, field_name: str
) -> POINTER:
    """
    This function parses a structure self contained
    by another structure and returns the pointer.

    It's used to get the LDR_DATA_TABLE_ENTRY from LIST_ENTRY,
    to list modules in process memory.
    """

    offset = getattr(struct_type, field_name).offset
    return cast(address - offset, POINTER(struct_type))


def get_modules_strings(
    peb: PEB,
) -> Iterable[Tuple[UNICODE_STRING, UNICODE_STRING]]:
    """
    This functions returns modules from the PEB.
    """

    loaded_module_lists = peb.Ldr.contents
    head = addressof(loaded_module_lists.InMemoryOrderModuleList)
    current = loaded_module_lists.InMemoryOrderModuleList.Flink

    while addressof(current.contents) != head:
        module = containing_record(
            addressof(current.contents),
            LDR_DATA_TABLE_ENTRY,
            "InMemoryOrderLinks",
        ).contents

        yield module.BaseDllName, module.FullDllName

        current = module.InMemoryOrderLinks.Flink


def modify_unicode_string(
    unicode_string: UNICODE_STRING, new_value: str
) -> None:
    """
    This function modify an unicode strings values.
    """

    bytes_value = new_value.encode("utf-16le")
    size_bytes_value = len(bytes_value)

    buffer = VirtualAlloc(
        None, size_bytes_value, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    if not buffer:
        raise WinError(get_last_error())

    memmove(buffer, bytes_value, size_bytes_value)

    unicode_string_address = addressof(unicode_string)
    old_protect = DWORD()

    if not VirtualProtect(
        unicode_string_address,
        sizeof(UNICODE_STRING),
        PAGE_READWRITE,
        byref(old_protect),
    ):
        raise WinError(get_last_error())

    unicode_string.Buffer = cast(buffer, LPWSTR)
    unicode_string.Length = size_bytes_value
    unicode_string.MaximumLength = size_bytes_value

    if not VirtualProtect(
        unicode_string_address,
        sizeof(UNICODE_STRING),
        old_protect.value,
        byref(old_protect),
    ):
        raise WinError(get_last_error())


def modify_executable_path_name(
    peb: PEB, module_name: str, fullpath: str
) -> None:
    """
    This function modify the executable module path and name.
    """

    for name, path in get_modules_strings(peb):
        if wstring_at(name.Buffer, name.Length // 2).endswith(".exe"):
            modify_unicode_string(name, module_name)
            modify_unicode_string(path, fullpath)


def read_memory(address: int, size: int) -> bytes:
    """
    This function reads a memory area using ReadProcessMemory.
    """

    buffer = (c_ubyte * size)()
    bytes_read_size = c_size_t()
    success = ReadProcessMemory(
        GetCurrentProcess(),
        c_void_p(address),
        buffer,
        size,
        byref(bytes_read_size),
    )
    if not success:
        raise WinError()
    return bytes(buffer[: bytes_read_size.value])


def get_stored_command_line_address(
    func_base_addr: int, instruction_bytes: bytes
) -> int:
    """
    This function returns the address
    where command line address is stored.
    """

    if len(instruction_bytes) < 7:
        raise ValueError("Instruction bytes too short")
    if instruction_bytes[0:3] != b"\x48\x8B\x05":
        raise ValueError("Unexpected opcode, expected MOV RAX, [RIP+disp32]")

    disp_bytes = instruction_bytes[3:7]
    disp32 = int.from_bytes(disp_bytes, byteorder="little", signed=True)
    next_instr_addr = func_base_addr + 7

    return next_instr_addr + disp32


def set_command_line(command_line: str, function_name: str) -> None:
    """
    This function modify the command line address for the Win32 API.
    """

    kernelbase = GetModuleHandleW("kernelbase.dll")
    address = GetProcAddress(kernelbase, function_name.encode())
    instructions = read_memory(address, 7)
    command_pointer_address = get_stored_command_line_address(
        address, instructions
    )

    if function_name.endswith("W"):
        command = create_unicode_buffer(command_line)
        command_size = sizeof(command)
    elif function_name.endswith("A"):
        command = create_string_buffer(command_line.encode())
        command_size = sizeof(command)
    else:
        raise ValueError("Invalid function name")

    buffer = VirtualAlloc(
        None, command_size, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE
    )

    if not buffer:
        raise WinError()

    memmove(buffer, command, command_size)

    address_size = sizeof(c_void_p)
    written = SIZE_T(0)

    if not WriteProcessMemory(
        GetCurrentProcess(),
        command_pointer_address,
        byref(LPVOID(buffer)),
        address_size,
        byref(written),
    ):
        raise WinError()

def set_command_lines(command_line: str) -> None:
    """
    This function modify ANSI and Unicode command lines in Win32 API.
    """

    set_command_line(command_line, "GetCommandLineW")
    set_command_line(command_line, "GetCommandLineA")


def load_struct_from_bytes(struct: type, data: bytes) -> Structure:
    """
    This function returns a ctypes structure
    build from bytes sent in arguments.
    """

    instance = struct()
    memmove(pointer(instance), data, sizeof(instance))
    return instance


def load_struct_from_file(struct: type, file: _BufferedIOBase) -> Structure:
    """
    This function returns a ctypes structure
    build from memory address sent in arguments.
    """

    return load_struct_from_bytes(struct, file.read(sizeof(struct)))


def get_data_from_memory(position: int, size: int) -> bytes:
    """
    This function returns bytes from memory address and size.
    """

    buffer = (c_byte * size)()
    memmove(buffer, position, size)
    return bytes(buffer)


def read_array_structure_until_0(
    position: int, structure: type
) -> Iterable[Tuple[Structure]]:
    """
    This function generator yields ctypes structures from memory
    until last element contains only NULL bytes.
    """

    size = sizeof(structure)
    index = 0
    data = get_data_from_memory(position, size)
    while data != (b"\0" * size):
        instance = load_struct_from_bytes(structure, data)
        yield index, instance
        index += 1
        data = get_data_from_memory(position + index * size, size)


def load_headers(file: _BufferedIOBase) -> PeHeaders:
    """
    This function returns all PE headers structure from file.
    """

    dos_header = load_struct_from_file(IMAGE_DOS_HEADER, file)
    file.seek(dos_header.e_lfanew)
    nt_headers = load_struct_from_file(IMAGE_NT_HEADERS, file)
    file_header = nt_headers.FileHeader

    if file_header.Machine == 0x014C:  # IMAGE_FILE_MACHINE_I386
        optional_header = nt_headers.OptionalHeader
        arch = 32
    elif file_header.Machine == 0x8664:  # IMAGE_FILE_MACHINE_AMD64
        file.seek(sizeof(IMAGE_OPTIONAL_HEADER32) * -1, 1)
        optional_header = load_struct_from_file(IMAGE_OPTIONAL_HEADER64, file)
        arch = 64

    section_headers = load_struct_from_file(
        (IMAGE_SECTION_HEADER * file_header.NumberOfSections), file
    )

    return PeHeaders(
        dos_header,
        nt_headers,
        file_header,
        optional_header,
        section_headers,
        arch,
    )


def allocate_memory_image(pe_headers: PeHeaders) -> int:
    """
    This function allocates memory for executable image.
    """

    relocation = (
        pe_headers.optional.DllCharacteristics
        & IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE
    )
    relocation = (
        relocation
        and pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].VirtualAddress
        and pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].Size
    )

    ImageBase = VirtualAlloc(
        None if relocation else pe_headers.optional.ImageBase,
        pe_headers.optional.SizeOfImage,
        MEM_RESERVE | MEM_COMMIT,
        PAGE_READWRITE,
    )

    if not ImageBase:
        raise RuntimeError("Failed to allocate memory for executable image.")

    return ImageBase


def load_in_memory(file: _BufferedIOBase, pe_headers: PeHeaders) -> int:
    """
    This function loads the PE program in memory
    using the file and all PE headers.
    """

    ImageBase = allocate_memory_image(pe_headers)
    old_permissions = DWORD(0)
    file.seek(0)

    memmove(
        ImageBase,
        file.read(pe_headers.optional.SizeOfHeaders),
        pe_headers.optional.SizeOfHeaders,
    )
    result = VirtualProtect(
        ImageBase,
        pe_headers.optional.SizeOfHeaders,
        PAGE_READONLY,
        byref(old_permissions),
    )

    for section in pe_headers.sections:
        position = ImageBase + section.VirtualAddress
        if section.SizeOfRawData > 0:
            file.seek(section.PointerToRawData)
            memmove(
                position,
                file.read(section.SizeOfRawData),
                section.SizeOfRawData,
            )
        else:
            memset(position, 0, section.Misc)

        if (
            section.Characteristics & 0xE0000000 == 0xE0000000
        ):  # IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_WRITE
            new_permissions = PAGE_EXECUTE_READWRITE
        elif (
            section.Characteristics & 0x60000000 == 0x60000000
        ):  # IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ
            new_permissions = PAGE_EXECUTE_READ
        elif (
            section.Characteristics & 0xC0000000 == 0xC0000000
        ):  # IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_WRITE
            new_permissions = PAGE_READWRITE
        elif (
            section.Characteristics & 0x40000000 == 0x40000000
        ):  # IMAGE_SCN_MEM_READ
            new_permissions = PAGE_READONLY

        old_permissions = DWORD(0)
        result = VirtualProtect(
            position,
            section.Misc,
            new_permissions,
            byref(old_permissions),
        )

    return ImageBase


def get_functions(
    ImageBase: int, position: int, struct: type
) -> Iterable[Tuple[int, int]]:  # LPCSTR
    """
    This function loads the PE program in memory
    using the file and all PE headers.
    """

    size_import_name = sizeof(IMAGE_IMPORT_BY_NAME)

    for index, thunk_data in read_array_structure_until_0(
        ImageBase + position, struct
    ):
        address = thunk_data.u1.Ordinal
        if not (address & 0x8000000000000000):
            data = get_data_from_memory(ImageBase + address, size_import_name)
            import_by_name = load_struct_from_bytes(IMAGE_IMPORT_BY_NAME, data)
            address = ImageBase + address + IMAGE_IMPORT_BY_NAME.Name.offset
        yield index, address  # LPCSTR(address)


def get_imports(
    pe_headers: PeHeaders, ImageBase: int, module_container: str
) -> List[ImportFunction]:
    """
    This function returns imports for a in memory module,
    this function loads modules (DLL) when is not loaded to get
    the module address and functions addresses required
    in the ImportFunction.
    """

    rva = pe_headers.optional.DataDirectory[
        IMAGE_DIRECTORY_ENTRY_IMPORT
    ].VirtualAddress
    if rva == 0:
        return []

    position = ImageBase + rva
    type_ = IMAGE_THUNK_DATA64 if pe_headers.arch == 64 else IMAGE_THUNK_DATA32
    size_thunk = sizeof(type_)
    imports = []

    for index, import_descriptor in read_array_structure_until_0(
        position, IMAGE_IMPORT_DESCRIPTOR
    ):
        module_name = LPCSTR(ImageBase + import_descriptor.Name)
        module_name_string = module_name.value.decode()
        module = LoadLibraryA(module_name)

        if not module:
            raise ImportError(
                "Failed to load the library: " + module_name_string
            )

        for counter, function in get_functions(
            ImageBase, import_descriptor.Misc.OriginalFirstThunk, type_
        ):
            function_name = LPCSTR(function & 0x7FFFFFFFFFFFFFFF)
            address = GetProcAddress(module, function_name)
            function_name_string = (
                (function & 0x7FFFFFFFFFFFFFFF)
                if function & 0x8000000000000000
                else function_name.value.decode()
            )

            function_position = (
                ImageBase + import_descriptor.FirstThunk + size_thunk * counter
            )

            imports.append(
                ImportFunction(
                    function_name_string,
                    module_name_string,
                    module,
                    address,
                    function_position,
                    module_container,
                )
            )

    return imports


def load_imports(functions: List[ImportFunction]) -> None:
    """
    This function loads imports (DLL, libraries), finds the functions addresses
    and write them in the IAT (Import Address Table).
    """

    if not functions:
        return None

    size_pointer = sizeof(c_void_p)

    for function in functions:
        old_permissions = DWORD(0)
        result = VirtualProtect(
            function.import_address,
            size_pointer,
            PAGE_READWRITE,
            byref(old_permissions),
        )
        memmove(
            function.import_address,
            function.address.to_bytes(size_pointer, "little"),
            size_pointer,
        )
        result = VirtualProtect(
            function.import_address,
            size_pointer,
            old_permissions,
            byref(old_permissions),
        )


def load_relocations(pe_headers: PeHeaders, ImageBase: int) -> None:
    """
    This function overwrites the relocations with the difference between image
    base in memory and image base in PE headers.
    """

    delta = ImageBase - pe_headers.optional.ImageBase
    if (
        not pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].VirtualAddress
        or not delta
    ):
        return None

    type_ = IMAGE_THUNK_DATA64 if pe_headers.arch == 64 else IMAGE_THUNK_DATA32
    size_pointer = sizeof(type_)

    position = (
        ImageBase
        + pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].VirtualAddress
    )
    size = sizeof(IMAGE_BASE_RELOCATION)
    data = get_data_from_memory(position, size)

    while data != (b"\0" * size):
        base_relocation = load_struct_from_bytes(IMAGE_BASE_RELOCATION, data)
        block_size = (
            base_relocation.SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)
        ) // 2

        for reloc in (c_uint16 * block_size).from_address(position + size):
            type_ = reloc >> 12
            offset = reloc & 0x0FFF
            address = ImageBase + base_relocation.VirtualAddress + offset

            if (
                type_ == IMAGE_REL_BASED_HIGHLOW
                or type_ == IMAGE_REL_BASED_DIR64
            ):
                static_address = int.from_bytes(
                    get_data_from_memory(address, size_pointer), "little"
                )
                old_permissions = DWORD(0)
                result = VirtualProtect(
                    address,
                    size_pointer,
                    PAGE_READWRITE,
                    byref(old_permissions),
                )
                memmove(
                    address,
                    (static_address + delta).to_bytes(size_pointer, "little"),
                    size_pointer,
                )
                result = VirtualProtect(
                    address,
                    size_pointer,
                    old_permissions,
                    byref(old_permissions),
                )

        data = get_data_from_memory(
            position + base_relocation.SizeOfBlock, size
        )
        position += base_relocation.SizeOfBlock


def load(file: _BufferedIOBase) -> None:
    """
    This function does all steps to load and execute the PE program in memory.
    """

    pe_headers = load_headers(file)
    image_base = load_in_memory(file, pe_headers)
    file.close()

    load_imports(get_imports(pe_headers, image_base, "target"))
    load_relocations(pe_headers, image_base)

    function_type = CFUNCTYPE(c_int)
    function = function_type(
        image_base + pe_headers.optional.AddressOfEntryPoint
    )
    function()


def main() -> int:
    """
    This is the main function to start the program from command line.
    """

    print(copyright)

    if len(argv) != 3:
        print(
            'USAGES: "',
            executable,
            '" "',
            argv[0],
            '" [executables path] [command line]',
            file=stderr,
            sep="",
        )
        return 1

    path = argv[1]
    command_line = argv[2]

    if not isfile(path):
        print("Executable path doesn't exists.", file=stderr)
        return 2

    module_name = basename(path)
    full_path = abspath(path)
    peb = get_peb()

    modify_process_informations(peb, full_path, command_line)
    modify_executable_path_name(peb, module_name, full_path)
    set_command_lines(command_line)

    load(open(path, "rb"))
    return 0


if __name__ == "__main__":
    exit(main())
