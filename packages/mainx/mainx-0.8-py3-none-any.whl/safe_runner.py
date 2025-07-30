import sys
import platform
import socket

# Attempt to import Windows-only APIs
try:
    import win32api
    WINDOWS = True
except ImportError:
    WINDOWS = False
    win32api = None

def get_user_info():
    if WINDOWS and win32api:
        try:
            return win32api.GetUserName()
        except Exception as e:
            return f"win32api failed: {e}"
    else:
        try:
            import getpass
            return getpass.getuser()
        except:
            return "Unknown User"

def get_system_info():
    return {
        "OS": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.machine(),
        "Hostname": socket.gethostname(),
        "User": get_user_info()
    }

def main():
    info = get_system_info()
    print("[+] System Info Collected:")
    for key, val in info.items():
        print(f"    {key}: {val}")

if __name__ == "__main__":
    main()
