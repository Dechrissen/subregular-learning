import csv

lines = open("all_evals.txt", "r").readlines()
tests = {}
for line in lines:
    test = line.strip().split(":")[0].replace("models/", "")
    if test not in tests:
        tests[test] = {}
    metric = line.strip().split(":")[1]
    value = line.strip().split()[1]
    tests[test][metric] = value

csv_fname = "all_evals.csv"
with open(csv_fname, "w", newline="\n") as f:
    writer = csv.writer(f)
    writer.writerows([[
        "alph",
        "tier",
        "class",
        "k",
        "j",
        "i",
        "direction",
        "network_type",
        "drop",
        "train_set_size",
        "test_type",
        "tp",
        "fp",
        "tn",
        "fn",
        "tpr",
        "fpr",
        "precision",
        "fscore",
        "accuracy",
        "auc",
        "brier"
    ]])

for test in tests:
    model = test.split("/")[0]
    direction = model.split("_")[0]
    network_type = model.split("_")[1]
    drop = model.split("_")[2]
    lang = model.split("_")[3]
    train_set_size = model.split("_")[4]

    alph = lang.split(".")[0]
    tier = lang.split(".")[1]
    lang_class = lang.split(".")[2]
    k = lang.split(".")[3]
    j = lang.split(".")[4]
    lang_i = lang.split(".")[5]

    test_type = test.split("/")[1].split("_")[0].replace("Test", "")

    with open(csv_fname, "a", newline="\n") as f:
        writer = csv.writer(f)
        try:
            writer.writerows([[
                alph,
                tier,
                lang_class,
                k,
                j,
                lang_i,
                direction,
                network_type,
                drop,
                train_set_size,
                test_type,
                tests[test]["TP"],
                tests[test]["FP"],
                tests[test]["TN"],
                tests[test]["FN"],
                tests[test]["TPR"],
                tests[test]["FPR"],
                tests[test]["Precision"],
                tests[test]["F-score"],
                tests[test]["Accuracy"],
                tests[test]["AUC"],
                tests[test]["Brier"]
            ]])
        except KeyError:
            pass
