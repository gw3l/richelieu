#!/usr/bin/env python3
# coding: utf-8

# entier n extrait de la clé publique
n = 837849563862443268467145186974119695264713699736869090645354954749227901572347301978135797019317859500555501198030540582269024532041297110543579716921121054608494680063992435808708593796476251796064060074170458193997424535149535571009862661106986816844991748325991752241516736019840401840150280563780565210071876568736454876944081872530701199426927496904961840225828224638335830986649773182889291953429581550269688392460126500500241969200245489815778699333733762961281550873031692933566002822719129034336264975002130651771127313980758562909726233111335221426610990708111420561543408517386750898610535272480495075060087676747037430993946235792405851007090987857400336566798760095401096997696558611588264303087788673650321049503980655866936279251406742641888332665054505305697841899685165810087938256696223326430000379461379116517951965921710056451210314300437093481577578273495492184643002539393573651797054497188546381723478952017972346925020598375000908655964982541016719356586602781209943943317644547996232516630476025321795055805235006790200867328602560320883328523659710885314500874028671969578391146701739515500370268679301080577468316159102141953941314919039404470348112690214065442074200255579004452618002777227561755664967507

# entier e extrait de la clé publique
e = 65537

# le contenu du fichier motDePasseGPG.txt.enc sous forme hexadécimale. pour l'obtenir : cat motDePasseGPG.txt.enc | xxd -ps
c = 0x14a290b886069beadc539cbebb28f47b768ce968cba889fe7b810eaa8eba933cea3472261722984cf14832eb3b82343ffbc4f63d6d1ad10cae7f911434e1ae5fdc1996b79aac36993ff7ab0ba20835286921a678db025108923590c3713f4b1bee483fe6ed4900478b8fd5d2c2c3aa7c69fc9c5b782d916fde411a29fc969ff02fcd9a6c427830ae0b6084bb3e2bd2ade7bb656a644acd6c4f479788ec8c15c566b293fdfe4fa6479a067b17fdc86753f41b3ec34e97f907638d0492d3dc944080c3bbe1fdcea7cdb81cf72b5ee327ba7d4063eaa68c8afe31bcb0f0f2095aa7080c294eb24c63518aa22975b3c0680b61b2f5643b9163c2dbd83cd91f8330f3ac243de2aa254a647684be90025a5ca2fa52bc87c41b67dbbecf0937ac3f9a54f92bcd08e37347b58ac5932f547be1b49c4803a41d1b77a1009328a5bc8df12243f3f6646a30de51d37dd9d9a6cf4cff77a9ac40da3df50d6e71ec0706e0c2eef3f088d2c8f5ee076d3b802cb0e512b60824fbfa7b4d19dbe3d669b550af8a0e628ba3f759de5e79db4d9a23a4ec651a7b2bef2a7fc74e690cefd912074f8fbb25e97777816929cfb77781cce9d9c1bc74e8be5ed7b7f3d45f318b53430ffedaeca8162016fa25828adc517e59509b30d5c43941ada7a5325e1caad52b4347ef695426a6bdca69ea0b9d39d358756e8a7c375b56c0de26b2613a5dcc34a97feb

# l'entier p tel qu'il est dans le fichier originalement obtenu de l'archive
prime ="00:fb:40:dc:44:ba:03:d1:53:42:f7:59:08:e0:f9:30:05:96:64:4a:de:94:68:5e:08:e2:8c:9a:b1:64:0c:2f:62:c2:9a:b9:a2:39:82:4b:9e:be:eb:76:ae:6d:87:21:a3:5e:9e:d9:8d:7e:57:38:3e:59:09:34:a5:78:cd:f7:2e:89:5d:5c:37:52:ea:fd:f6:31:cc:ba:d2:d9:60:e4:45:1d:67:76:d2:1f:12:9c:9d:c9:b1:90:45:51:ed:d2:fb:dd:b6:74:b4:99:fb:b1:0a:d9:b7:c2:be:8b:57:07:22:0a:8e:3a:36:ff:6d:c1:1d:63:93:af:cb:4e:c0:47:9f:65:bf:df:e3:f0:5f:1e:98:61:45:74:ec:36:a7:a5:b1:f1:8d:3d:97:6b:5a:82:49:09:00:08:0d:9d:c2:74:57:4e:30:a1:39:68:2f:22:34:71:13:aa:3b:f2:20:4f:8e:10:eb:d4:d0:9b:cd:8c:c2:53:5f:9d:71:13:0c:0f:21:b6:6e:13:39:40:d3:a6:b1:eb:74:ad:dd:0a:29:14:81:b1:90:ad:e0:53:f0:89:c8:00:fe:dc:ad:56:59:fc:28:1d:c0:cf:5e:08:c0:54:33:24:a3:52:bb:f3:25:10:43:c3:73:b8:40:4f:fc:6b:6b:77:bd:5f:22:24:eb:fb:15".split(':')

# renvoie True ou False selon si le bit à la position pos dans la variable var est égale à 0 ou 1
def check(var, pos):
	return ((var) & (1<<(pos-1)) == 0)

# Renvoie value1 ou value2 selon la valeur du bit à la position pos dans l'entier integer
def BVal(integer, pos, value1, value2):
	if check(integer, pos):
		return value1
	return value2

# les bits modifiés sont présent à 11 positions dans le prime p, on doit donc tester 2^11 possibilitées
for i in range(pow(2,11)):
	prime[1]   = BVal(i, 1,  'fb', '7f')
	prime[54]  = BVal(i, 2,  '57', 'a4')
	prime[62]  = BVal(i, 3,  'cd', 'b5')
	prime[86]  = BVal(i, 4,  '12', 'f4')
	prime[96]  = BVal(i, 5,  'fb', '7f')
	prime[102] = BVal(i, 6,  'fb', '7f')
	prime[110] = BVal(i, 7,  '57', 'a4')
	prime[160] = BVal(i, 8,  '57', 'a4')
	prime[182] = BVal(i, 9,  'cd', 'b5')
	prime[231] = BVal(i, 10, '54', '16')
	prime[-2]  = BVal(i, 11, 'fb', '7f')
	p = int( "".join(prime), 16)
	# on teste ensuite si l'entiert généré est bien un diviseur de n :
	q = n // p
	if p * q == n:
		# si c'est le cas on s'arrète
		break

print ("n = %d" % n)
print ("e = %d" % e)
print ("p = %d" % p)
print ("q = %d" % q)

# on calcule ensuite la valeur de d (voir la page wikipedia de RSA)
phi = ( p - 1 ) * ( q - 1 )
def egcd(a, b):
        if a == 0 :
            return(b, 0, 1)
        else:
            g, y, x = egcd( b % a, a)
            return (g, x - ( b // a ) * y, y)
def modinv(a,m):
        g, x, y = egcd(a, m)
        if g != 1:
            raise Expection("RSA Hello")
        else :
            return x%m
d = modinv(e,phi)
print ("d = %d" % d)
decode = pow(c,d,n)
output = (hex(decode)[2:].replace('L',''))

print ("décrypté : "+str(bytes.fromhex("0"+output)))
