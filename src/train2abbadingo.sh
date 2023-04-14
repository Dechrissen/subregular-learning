#!/bin/sh
# usage: train2ffdata.sh input.txt > output.txt
# input.txt should consist of a series of lines,
# each of which composed of a word, a tab character,
# then a BOOL value indicating whether the word is accepted.
#
# The output data is in the Abbadingo format:
# the first line is two fields:
# * the number of words in the file, then
# * the number of alphabetic symbols
# subsequent lines each describe a word and consist of
# * a tag (here 0 for rejected or 1 for accepted)
# * the length in characters of the word
# * the word as a space-separated sequence of characters

name="$(basename "$1")"
wc -l < "$1" | tr -d '[[:space:]]'; printf ' %s\n' "${name%%.*}"
awk '# TODO rewrite this in python
BEGIN {
	for(i=0; i<256; i++) {
		_ord_[sprintf("%c",i)] = i
	}
}
function ord(n)
{
	return _ord_[n]
}

{
	n=split($1,a,"")
	m=0
	x=""
	for(i=1; i<=n;m++) {
		x = x a[i++]
		# "properly" decode UTF-8 values
		while (int(ord(a[i]) / 64) == 2) {
			x = x a[i++]
		}
		x=x " "
	}
	sub("[[:space:]]*$","",x)
	print ($2=="TRUE"),m,x
}
' "$1"
