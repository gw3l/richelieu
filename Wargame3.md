# Challenge Richelieu DGSE - Wargame #3

Suite au [Wargame #2](./Wargame2.md), on obtient un accès ssh vers le 3ème wargame.
Là encore il s'agit d'un programme avec des droits [suid](https://fr.wikipedia.org/wiki/Setuid#Setuid_et_Setgid_pour_les_ex%C3%A9cutables).

Lançons-le :
```bash
./prog.bin
***************************************************
***    Bienvenue dans la gestion d'éléments     ***
***                                             ***
***   NB : Taille de l'ID : 50 octets           ***
***        Vous pouvez mettre la taille         ***
***        en paramètre pour la changer         ***
***************************************************
Que voulez-vous faire ?
  -> 1) nouvel élément
  -> 2) affichage
  -> 3) détruire un élément
  -> 4) changer de nom
  -> 5) changer d'id
  -> 6) sortie
choix $
```

On est face à un challenge typique de ceux traitant des problèmes d'allocation mémoire dynamique [ptmalloc2](https://blog.k3170makan.com/2018/11/glibc-heap-exploitation-basics.html?m=1). Comme c'est indiqué lorsqu'on lance le programme, nous avons la possibilité de changer la taille de l'ID en passant un entier en paramètre.
Voici ce que fait chaque élément du menu :
1. `malloc(0x10)` pour stocker un élément qui contient juste deux pointeurs. On nous demande alors le nom de l'élément. Le `malloc` effectué ensuite dépends alors de la taille de la chaîne rentrée par l'utilisateur. On nous demande ensuite l'id de l'élément. Le `malloc` effectué est alors fixe (en fonction du paramètre passé ou 0x32 par défaut)
2. Affichage du contenu de chaque élément.
3. Appel à `free()` soit sur le nom, soit sur l'id.
4. Réécriture du nom. le nouveau nom ne peut pas excéder 8 octets. Pas d'appel à `malloc()`.
5. Nouvel id. le nouvel id ne peut pas dépasser la taille de l'id. Pas d'appel à `malloc()`.
6. Fin du programme

Le problème est qu'aucune vérification n'est faite lorsque l'on fait un `free()` pour savoir si la mémoire allouée à cet endroit n'a pas déjà été libérée et qu'aucune vérification n'est faite lors de l'affichage pour savoir si ce qu'on affiche n'est pas de la mémoire libérée.

On peut donc exploiter ce binaire en réalisant une attaque du type [double free](https://github.com/shellphish/how2heap/blob/master/fastbin_dup.c).

Là encore j'ai réalisé [un script python qui se charge d'exploiter cette vulnérabilité](./scripts/defi3-exploit.py). Voilà ce qu'il fait :
- Lancement du programme avec 15 en paramètre afin que tous les malloc() aient la même taille.
- Création d'un élément (3 `malloc()`)
- Création d'un second élément (3 `malloc()`)
- Destruction du nom du premier élément => `free()` sur la mémoire correspondant au 2eme `malloc()`
- Destruction de l'id du premier élément => `free()` sur la mémoire correspondant au 3eme `malloc()`
- Destruction à nouveau du nom du premier élément => `free()` à nouveau sur la mémoire correspondant au 2eme `malloc()`
- Création d'un 3ème élément : 3 `malloc()`. Le 1er et le 3eme `malloc()` renvoient les mêmes adresses à cause du double `free()`. Pour cet élément on va passer l'adresse de la [GOT](https://en.wikipedia.org/wiki/Global_Offset_Table) de `free()` en nom et id.
  Après le troisième `malloc()`, l'adresse de la got de `free()` est écrite à la place de l'id (normal). Le truc c'est que l'endroit où le programme écrit est aussi celui où sont stockés les pointeurs vers les chaînes nom et id. Ces pointeurs sont alors écrasés par l’adresse de la got.
- Affichage des éléments. Lors de l'affichage de l'id du 3ème élément, c'est l'adresse réelle de la fonction `free()` dans la libc qui est affiché. Mon script calcule l'adresse de `system()` à partir de l'adresse leakée de `free()`.
- Renommage du nom du second élément en "/bin/sh"
- Renommage du nom du troisième élément par l’adresse de `system()`. En fait à cet endroit on réécrit l’adresse de `free()` dans la GOT
- Destruction du nom du second élément. Le programme va appeler `free()` sur le nom. Or l’adresse de `free()` a été réécrite par celle de `system()` et le nom contient "/bin/sh". C'est donc `system("/bin/sh")` qui est exécuté. On obtient un shell et on peut afficher le contenu du dernier drapeau :)

Voilà c'est terminé, il n'y a plus d'autre épreuve. C'était un ensemble de challenge bien sympathique et au final pas très compliqué. J'espère que mes explications auront été claires.
