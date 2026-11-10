#include <sys/event.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <signal.h>
int main(void) {
 int q=kqueue();pid_t child=fork();
 if(child==0){usleep(500000);_exit(0);}
 if(child<0||q<0)return 2;
 struct kevent change,result;struct timespec zero={0,0};
 EV_SET(&change,child,EVFILT_PROC,EV_ADD|EV_RECEIPT,NOTE_FORK|NOTE_TRACK|NOTE_EXIT,0,0);
 int n=kevent(q,&change,1,&result,1,&zero);
 printf("{\"return\":%d,\"errno\":%d,\"receiptError\":%ld,\"flags\":%d}\n",n,n<0?errno:0,n>0?(long)result.data:0,n>0?result.flags:0);
 kill(child,SIGKILL);waitpid(child,0,0);close(q);return 0;
}
