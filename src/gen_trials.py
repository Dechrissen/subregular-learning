if __name__ == "__main__":
	print("Opening files....")
	output_file = open("model_list.txt", "w+", encoding="utf8")
	
	f = open("../tags.txt", "r", encoding="utf8")
	f = f.readlines()
	
	print("Generating list....")
	for tag in f:
		for length in ['1', '10', '100']:
			for model in ['RNN', 'LSTM', 'GRU']:
				output_file.write(tag[:-1] + " " + length + " " + model + "\n")
				
	output_file.close()
	print("Done!")