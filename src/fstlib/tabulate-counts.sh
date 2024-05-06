#!/bin/sh

set -e

printf 'Alph\tTier\tClass\tk\tj\ti\tSize\tMonoid\tD-Classes\n' \
> state-counts/counts.tsv~

for file in state-counts/*.*.*.*.*; do
	base="$(basename "${file}")"
	printf '%s.' "${base}" | cat - "${file}" | tr '.,' $'\t'
	if (printf '%s\n' "${base}" | grep -q 'S[PL][.]'); then
		printf '%s.' "${base}" \
		| cat - "${file}" \
		| sed 's/S/coS/' \
		| awk -F'[.,]' -v"OFS=\t" '{$7 = $7 + 1; print}'
	fi
done | sort >> state-counts/counts.tsv~

mv state-counts/counts.tsv{~,}
