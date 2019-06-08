<?php

$img = $argv[1] ?? 'lsb_RGB.png';

/**
 * retourne le least signifiant bit d'un octet
 */
function LSB($integer) {
	return $integer & 1;
}

/**
 * conversion d'une chaine de caractère binaire, type "0110010011" en chaîne de caractère normale
 */
function fromBin($bin) {
        $octets = str_split($bin, 8);
        $out = '';
        foreach($octets as $byte) {
		$int = base_convert($byte,2,10);
                $out .= chr($int);
        }
        return $out;
}

// récupération de la taille de l'image
list($width, $height,) = getimagesize($img);
$BinMsg= '';

$im = imagecreatefrompng($img);

// on lit colonne par colone et non pas ligne par ligne :
// en s'arretant à la 1389e colone
for( $i = 0; $i < 1389; $i++) {
	for ($j = 0; $j < $height; $j++) {
		$rgb = imagecolorat($im, $i, $j);
		$colors = imagecolorsforindex($im, $rgb);
		$BinMsg .= LSB($colors['red']);	
		$BinMsg .= LSB($colors['green']);	
		$BinMsg .= LSB($colors['blue']);
	}
}

$chaine = fromBin($BinMsg);

echo $chaine."\n";


