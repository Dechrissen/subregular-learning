if __name__ == "__main__":
	print("Opening files....")
	output_file = open("model_list.txt", "w+", encoding="utf8")
	
	f = open("../traintags.txt", "r", encoding="utf8")
	f = f.readlines()
	
	print("Generating list....")
	for tag in f:
		for length in ['1k', '10k', '100k']:
			for model in ['simple', 'lstm', 'gru']:
				output_file.write(tag[:-1] + " " + length + " " + model + "\n")
				
	output_file.close()
	print("Done!")
