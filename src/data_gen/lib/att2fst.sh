FILES=./*.att
for f in $FILES
do
	echo "Processing $f file..."
	f2=${f%????}
	fstcompile --isymbols=ins.txt --osymbols=outs.txt $f  $f2.fst
done
