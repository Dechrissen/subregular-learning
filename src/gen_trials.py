if __name__ == "__main__":
    output_file = open("model_list.txt", "w+", encoding="utf8")

    tags = open("tags.txt", "r", encoding="utf8").readlines()
    for tag in tags:
        for length in ['Small', 'Mid', 'Large']:
            for model in ["gru", "lstm", "simple", "stackedrnn", "transformer"]:
                output_file.write(f"{tag[:-1]} {length} {model}\n")
				
    output_file.close()
    print("Done!")

