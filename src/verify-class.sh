#!/bin/sh

for file in "$@"; do
	tests=""
	case "$file" in
		*.SP.*)
			tests="TLTT"
			;;
		*.PT.*)
			tests="TLTT SP"
			;;
		*.SL.*)
			tests="PT"
			;;
		*.TSL.*)
			tests="LPT"
			;;
		*.LT.*)
			tests="PT TSL"
			;;
		*.TLT.*)
			tests="LPT TSL"
			;;
		*.LTT.*)
			tests="PT TLT"
			;;
		*.TLTT.*)
			tests="LPT TLT"
			;;
		*.LP.*)
			tests="TLTT PT"
			;;
		*.TLP.*)
			tests="TLTT LPT"
			;;
		*.SF.*)
			tests="TLPT"
			;;
	esac
	if [ -z "${tests}" ]; then
		continue
	fi
	for test in ${tests}; do
		printf ':is%s it\n' "${test}"
	done \
	| awk -v file="\"${file}\"" \
	  'BEGIN {print ":readATT",file,"_ _"} {print}' \
	| plebby \
	| grep -q True \
	&& printf '%s\n' "${file}" \
	|| :
done
