FILES=./att_format/*.att

for f in $FILES
do
	echo "Processing att file $f ..."
	filename=$(basename "$f")
	filename_without_path="${filename%.*}"
	match64="*64*"
	match16="*16*"
	if [[ $filename_without_path == $match64 ]]
	then
	    symfile="alph64.txt"
	elif [[ $filename_without_path == $match16 ]]
	then
	    symfile="alph16.txt"
	else
	    symfile="alph4.txt"
	fi
	fstcompile --isymbols=att_format/${symfile} --osymbols=att_format/${symfile} --keep_isymbols --keep_osymbols $f fst_format/${filename_without_path}.fst
	echo "done."
done
