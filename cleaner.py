# python
import ctypes
import msvcrt
import subprocess
import sys
import subprocess

# SHEmptyRecycleBin flags
_SHERB_NOCONFIRMATION = 0x00000001
_SHERB_NOPROGRESSUI    = 0x00000002
_SHERB_NOSOUND         = 0x00000004

_shell32 = ctypes.windll.shell32
_shell32.SHEmptyRecycleBinW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint)
_shell32.SHEmptyRecycleBinW.restype  = ctypes.c_long

def empty_recycle_bin(confirm=False, show_progress=False, sound=True):
    flags = 0
    if not confirm:
        flags |= _SHERB_NOCONFIRMATION
    if not show_progress:
        flags |= _SHERB_NOPROGRESSUI
    if not sound:
        flags |= _SHERB_NOSOUND

    res = _shell32.SHEmptyRecycleBinW(None, None, flags)
    if res != 0:
        raise OSError(f"SHEmptyRecycleBinW failed with HRESULT {hex(res)}")

def _spawn_detached_cleaner():
    # Run the same executable/script with --run-clean in a detached, hidden process
    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000
    flags = DETACHED_PROCESS | CREATE_NO_WINDOW

    args = [sys.executable, sys.argv[0], "--run-clean"]
    subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=flags,
    )

if __name__ == "__main__":
    # If invoked with the special arg, perform the cleanup (runs in child process)
    if "--run-clean" in sys.argv:
        try:
            empty_recycle_bin()
        except Exception:
            # silent exit to keep the detached child unobtrusive
            pass
        sys.exit(0)

    # Normal interactive flow: wait for any key, spawn detached cleaner, then exit immediately
    print("Press any button to empty the recycle bin")
    msvcrt.getch()  # wait for a single keypress

    _spawn_detached_cleaner()
    # parent exits immediately so the console window closes right away
    sys.exit(0)
