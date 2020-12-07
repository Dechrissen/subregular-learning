#!/usr/bin/awk -E

BEGIN {
	OFS=","
}

{
	path = substr($1, 1, (index($1, ":") - 1))

	f1 = $2

	split(path, components, "/")
	model = components[2]

	test = substr(components[3], 1, (index(components[3], "_") - 1))

	split(model, model_desc, "_")

	model_type = model_desc[1]
	model_drop = model_desc[2]
	lang = model_desc[3]
	size = model_desc[4]

	lang_class = substr(lang, 1, (index(lang, ".") - 1))

	if (test == "Test1") {
		test1[model_type OFS lang_class OFS lang OFS size] = f1
	}
	else {
		if (test == "Test2") {
			test2[model_type OFS lang_class OFS lang OFS size] = f1
		}
		else {
			test3[model_type OFS lang_class OFS lang OFS size] = f1
		}
	}
}

END {
	print "Model Type", "Language Class", "Language", "Training Size", "Test 1", "Test 2", "Test 3"
	for (item in test1) {
		print item, test1[item], test2[item], test3[item]
	}
}
