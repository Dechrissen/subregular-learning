import shutil

alph = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
nums = [0,1,2,3,4,5,6,7,8,9]

# write ins.txt
with open('ins.txt', 'w') as f:
	f.write('<EPS>\t0\n')
	# start UTF-8 encoding number for lowercase alphabet
	x = 97
	for i in alph:
		f.write(i+'\t'+str(x)+'\n')
		x+=1
	# start UTF-8 encoding number for capital alphabet
	x = 65
	for i in alph:
		f.write(i.upper()+'\t'+str(x)+'\n')
		x+=1
	# start UTF-8 encoding number for digits
	x = 48
	for i in nums:
		f.write(str(i)+'\t'+str(x)+'\n')
		x+=1
	# hard code final two UTF-8 encodings
	f.write('#\t35\n')
	f.write('$\t36')

# copy ins.txt to outs.txt
shutil.copy('ins.txt', 'outs.txt')

print('wrote 64 symbols to ins.txt and outs.txt (a-z, A-Z, 0-9, #, $)')
