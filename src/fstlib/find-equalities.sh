#!/bin/sh
cd att_format
for a in *.att; do
	for b in "${a%%.*}".*PLT.*.att; do
		if [ "$a" '!=' "$b" ]; then
			printf '%s\n' \
			":readatt ${a} _ _" \
			'=a it' \
			":readatt ${b} _ _" \
			'=b it' \
			':equal a b' \
			| plebby \
			| grep -q True \
			&& printf '%s == %s\n' "$a" "$b"
		fi
	done
done
