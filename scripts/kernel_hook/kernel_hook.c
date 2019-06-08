#include <linux/module.h>
#include <linux/kallsyms.h>
#include <linux/kernel.h>
#include <linux/unistd.h>
#include <linux/delay.h>

#define overWritedSyscall __NR_readlink

MODULE_LICENSE("GPL");

static unsigned long **sys_call_table;
#if overWritedSyscall == __NR_readlink
asmlinkage int (*original_call) (const char __user *, char __user *, int);
#elif overWritedSyscall == __NR_write
asmlinkage int (*original_call) (unsigned int fd, const char __user * buf, size_t count);
#endif

static short altern = 0;

static void disable_page_protection(void) {
    unsigned long value;
    asm volatile("mov %%cr0,%0" : "=r" (value));
    if (value & 0x00010000) {
            value &= ~0x00010000;
            asm volatile("mov %0,%%cr0": : "r" (value));
    }
}

static void enable_page_protection(void) {
    unsigned long value;
    asm volatile("mov %%cr0,%0" : "=r" (value));
    if (!(value & 0x00010000)) {
            value |= 0x00010000;
            asm volatile("mov %0,%%cr0": : "r" (value));
    }
}
#if overWritedSyscall == __NR_readlink
asmlinkage int our_syscall(const char __user * path, char __user * buf, int bufsiz) {
#elif overWritedSyscall == __NR_write
asmlinkage int our_syscall(unsigned int fd, const char __user * buf, size_t count) {
#endif
   char name[TASK_COMM_LEN];
   get_task_comm(name, current);
   if (strcmp("executable", name) == 0) {
	   if(altern % 2 != 0) {
   		printk("kernhook: Syscall hooked for '%s'\n", name);
   		ssleep(8);
   		printk("kernhook: wake up!");
	   }
	   altern++;
 //  } else {
//	   printk("kernhook: '%s' bypass the hook", name);
   }
#if overWritedSyscall == __NR_readlink
   return original_call(path, buf, bufsiz);
#elif overWritedSyscall == __NR_write
   return original_call(fd, buf, count);
#endif

}


static int hook_init(void) {
    printk("kernhook: initialize module");
    sys_call_table = (void *) kallsyms_lookup_name("sys_call_table");
    original_call = (void *) sys_call_table[overWritedSyscall];

    disable_page_protection();
    sys_call_table[overWritedSyscall] =(void *) our_syscall;
    enable_page_protection();
    return 0;
}

static void hook_exit(void) {
	printk("kernhook: clean module");
	disable_page_protection();
	sys_call_table[overWritedSyscall] =(void *) original_call;
	enable_page_protection();
}

module_init(hook_init);
module_exit(hook_exit);
