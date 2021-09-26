from os import system, _exit, path, urandom

system("mode 80,18 & title Unique & powershell $H=get-host;$W=$H.ui.rawui;$B=$W.buffersize;$B.width=80;$B.height=9999;$W.buffersize=$B;")


def exit_():
    system("echo Press any key to exit . . . & pause >nul")
    _exit(0)


ERROR = "\x1b[38;5;255m[\x1b[31m-\x1b[38;5;255m]"
SUCCESS = "\x1b[38;5;255m[\x1b[32m+\x1b[38;5;255m]"


def randint(a, b, seed=[0]):
    seed[0] = (1664525 * seed[0] + 1013904223) % 2 ** 32
    return int(a + (1 + b - a) * seed[0] / 2 ** 32)


if not path.exists("prefire.py"):
    print(f"{ERROR} File does not exist.\n")
    exit_()
with open("prefire.py", "a") as f:
    for _ in range(1, randint(4, 10)):
        f.write(f"\n#{urandom(16).hex()}")
print(f"{SUCCESS} File was made unique.\n")
exit_()
