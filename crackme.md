# Challenge Richelieu DGSE - CrackMe

Suite à l'étape [Stéganographie](./steganographie.md), on a obtenu un [exécutable](./binaries/crackme).
On essaie d'abord de le lancer pour voir de quoi il s'agit :
```bash
chmod +x crackme
./crackme
usage : ./crackme <mot de passe>
./crackme password
Mauvais mot de passe
```

Il s'agit d'un crackme, un programme pour lequel il faut trouver un mot de passe.

On essaie de récupérer des infos sur le binaire :
```bash
objdump -d crackme

crackme:     format de fichier elf64-x86-64

nm crackme
nm: crackme: aucun symbole
```
Ces commandes sont censées nous donner les adresses des fonctions et le code assembleur du programme. Mais ici, elles ne renvoient rien.

Allons un peu plus loin :
```bash
objdump -x crackme

crackme:     format de fichier elf64-x86-64
crackme
architecture: i386:x86-64, fanions 0x00000102:
EXEC_P, D_PAGED
adresse de départ 0x0000000000447f10

En-tête de programme:
    LOAD off    0x0000000000000000 vaddr 0x0000000000400000 paddr 0x0000000000400000 align 2**21
         filesz 0x0000000000048724 memsz 0x0000000000048724 flags r-x
    LOAD off    0x00000000000b5428 vaddr 0x00000000006b5428 paddr 0x00000000006b5428 align 2**21
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-

Sections :
Idx Name          Taille    VMA               LMA               Off fich  Algn
SYMBOL TABLE:
aucun symbole
```
On a au moins un point d'entrée sur le quel mettre un point d'arrêt dans gdb.

```bash
strings crackme
[...]
$Info: This file is packed with the ALD executable packer http://upx.sf.net $
$Id: ALD 3.91 Copyright (C) 1996-2013 the ALD Team. All Rights Reserved. $
[...]
```
Le programme semble avoir été packé avec UPX, essayons de le dépacker :
```bash
upx -d crackme
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2018
UPX 3.95        Markus Oberhumer, Laszlo Molnar & John Reiser   Aug 26th 2018

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
upx: crackme: NotPackedException: not packed by UPX

Unpacked 0 files.
```

Il s'agit probablement d'une version modifiée d'**UPX**. Il est probablement possible de passer outre en créant une version adaptée d'upx. Comme je ne connais pas trop upx, je ne me suis pas orienté dans cette voie.

En déboguant le binaire avec gdb on se rend compte qu'il y a plusieurs protections:
- le binaire est compilé en **statique**, c'est à dire qu'il ne fait aucun appel à une librairie extérieure, toutes les fonctions nécessaires sont inclues dans le binaire.
- diverses fonctions **anti reverse engineering** comme l'utilisation de **[rtdsc](https://fr.wikipedia.org/wiki/RDTSC)** (qui compte le temps écoulé entre un certain nombre d'instructions). Il vérifie si la variable d'environnement **MALLOC_TRACE** est renseignée, signe que les allocations mémoire sont tracées. Je le soupçonne aussi de faire appel à la fonction **ptrace** pour vérifier que le programme n'est pas en cours de débogage.

Si le binaire aurait été compilé dynamiquement on aurait pu [hooker](https://www.0x0ff.info/2014/hook-lib-linux-ld_preload/) une fonction juste avant la fin du programme avec **LD_PRELOAD**, mais là on ne peut pas... Par contre il fait appel à des appels système (forcement):

```bash
strace ./crackme password
execve("./crackme", ["./crackme", "password"], 0x7ffe02558fa8 /* 23 vars */) = 0
mmap(0x800000, 2896043, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, 0, 0) = 0x800000
readlink("/proc/self/exe", "<...>/richelieu/bin"..., 4096) = 45
mmap(0x400000, 2842624, PROT_NONE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x400000
mmap(0x400000, 726035, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x400000
mprotect(0x400000, 726035, PROT_READ|PROT_EXEC) = 0
mmap(0x6b1000, 11088, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0xb1000) = 0x6b1000
mprotect(0x6b1000, 11088, PROT_READ|PROT_WRITE) = 0
mmap(0x6b4000, 5160, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x6b4000
munmap(0x801000, 2891947)               = 0
uname({sysname="Linux", nodename="<...>", ...}) = 0
brk(NULL)                               = 0x11a9000
brk(0x11aa1c0)                          = 0x11aa1c0
arch_prctl(ARCH_SET_FS, 0x11a9880)      = 0
readlink("/proc/self/exe", "<...>richelieu/bin"..., 4096) = 45
brk(0x11cb1c0)                          = 0x11cb1c0
brk(0x11cc000)                          = 0x11cc000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0
write(1, "Mauvais mot de passe\n", 21Mauvais mot de passe
)  = 21
exit_group(0)                           = ?
+++ exited with 0 +++
```

Peut-on hooker les appels systèmes ? La réponse est oui. C'est un peu plus complexe qu'avec LD_PRELOAD mais ça se fait. Il "suffit" de **créer un module kernel Linux qui modifie la syscall table du noyau**.

C'est ce que j'ai fait [ici](./scripts/kernel_hook/). Ce module fonctionne sur Ubuntu 18.04 (et probablement ailleurs). Il est prévu pour **hooker le syscall** readlink. J'ai laissé la possibilité de hooker write à titre d'exemple, mais en l'état ça fait planter le kernel. Il est conçu pour attendre 8 secondes lors du second appel au syscall readlink par ce crackme exclusivement (pour le pas bloquer le reste du système), ce qui nous laisse une fenêtre de temps suffisante pour attacher le programme dans gdb. Toutes les instructions précédent ce deuxième syscall auront été effectuées sans débogage. On croise les doigts pour qu'il n'y ait pas d'autres fonction antidebugging jusqu'à la vérification du mot de passe.

Compilons et lançons le module :
```bash
make
[...]
sudo insmod kernel_hook.ko
```

Puis lançons le programme avec un paramètre quelconque et dans une autre fenêtre `sudo gdb crackme` (sudo est nécessaire pour pouvoir attacher le programme au moment du syscall, qui tourne en [ring 0](https://en.wikipedia.org/wiki/Protection_ring) à ce moment là):
```gdb
gdb-peda$ ps -ef | grep executable
root      4773  4668  0 13:14 pts/2    00:00:00 sudo gdb executable
root      4774  4773  1 13:14 pts/2    00:00:00 gdb executable
gwel      4776  3909  1 13:14 pts/1    00:00:00 ./executable woot
root      4777  4774  0 13:14 pts/2    00:00:00 bash -c ps -ef | grep executable
root      4779  4777  0 13:14 pts/2    00:00:00 grep executable
gdb-peda$ attach 4776
```
On continue l’exécution au pas à pas jusqu’à arriver à l'instruction située à l'adresse 0x400b20 qui semble être le véritable point d'entrée une fois le programme dépacké. On voit que le programme vérifie le nombre de paramètres, puis effectue les instructions suivantes :

```
=> 0x400abd:	repnz scas al,BYTE PTR es:[rdi]
   0x400abf:	mov    eax,0x0
   0x400ac4:	cmp    rcx,0xffffffffffffffe0
   0x400ac8:	je     0x400acc
```
À cet endroit, la longueur du premier paramètre est vérifié. Elle doit être égale à 30, sinon le programme envoie "Mauvais mot de passe".

Dans gdb on fait : `set $rcx = 0xffffffffffffffe0` avant l'instruction à l’adresse 0x400ac4 ci dessous. On fait comme si la chaîne avait la bonne longueur, plutôt que de recommencer tout le programme.

On arrive au bout d'un moment à ces instructions :

```
0x400af0:	movzx  eax,r8b
 0x400af4:	movzx  esi,BYTE PTR [rdx]
 0x400af7:	movzx  ecx,BYTE PTR [rdi]
 0x400afa:	add    rdx,0x1
=> 0x400afe:	add    rdi,0x1
 0x400b02:	test   cl,cl
 0x400b04:	je     0x400b17
 0x400b06:	mov    r8d,r9d
 0x400b09:	test   eax,eax
 0x400b0b:	je     0x400af0
 0x400b0d:	xor    ecx,esi
 0x400b0f:	cmp    cl,BYTE PTR [rdx]
 0x400b11:	sete   r8b
 0x400b15:	jmp    0x400af0
```
*rdx* contient un pointeur vers une chaîne qui vaut 773063265d3a0e3b0d4d2a1f2e1f2d4f2851377a147620780f214d216c11 (en hexadécimal). appelons cette chaîne *clé*.
*rdi* pointe vers la chaîne de caractère qu'on a passé en paramètre.
On voit que l'opération suivante est réalisée, pour chaque lettre de la chaîne passée en paramètre (en pseudo-code pour simplifier) :
```
if(xor(paramètre[i], clé[i]) == clé[i+1]) {
  continue
} else {
  print("Mauvais mot de passe")
}
```
La clé est donc xorée et le résultat est comparé. Le xor est facilement réversible, si on fait pour chaque lettre de la clé `xor(clé[i], clé[i+1])` on va obtenir le mot de passe. C'est ce que fait ce petit [script python](./scripts/xor.py). Lançons le :

```bash
python xor.py
GSE{g456@g5112bgyfMnbVXw.llM}
```
La première lettre est tronquée (car le test pour la première lettre est effectué en amont), mais on peut facilement la deviner. Le mot de passe est donc **DGSE{g456@g5112bgyfMnbVXw.llM}**

Il permet de décompresser le fichier suite.zip, obtenu dans la partie [Cryptanalyse](./cryptanalyse.md). Une fois décompressé, le fichier nous donne un simple fichier texte, indiquant une commande ssh ainsi qu'un mot de passe pour se connecter à un serveur.

Voilà. J'espère que mes explications ont été claires. La suite sera expliquée dans la partie [Wargame #1](./Wargame1.md).
