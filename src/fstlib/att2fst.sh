FILES=./*.att
for f in $FILES
do
	echo "Processing $f file..."
	f2=${f%????}
	fstcompile --isymbols=ins.txt --osymbols=outs.txt $f  /lib_fst/$f2.fst
done
