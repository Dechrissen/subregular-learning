FILES=./att_format/*.att
for f in $FILES
do
	echo "Processing att file $f ..."
	filename=$(basename "$f")
	filename_without_path="${filename%.*}"
	fstcompile --isymbols=att_format/ins.txt --osymbols=att_format/outs.txt $f fst_format/${filename_without_path}.fst
	echo "done."
done
