import tensorflow as tf
import os
from data import pad_data, parse_dataset


def predict(model, model_dir, data_file, test_name, vocabulary):
    index_to_char = {}
    for item in vocabulary:
        index_to_char[vocabulary[item]] = item

    _, x_data, y_data = parse_dataset(data_file, vocabulary)
    x_padded = tf.constant(pad_data(x_data, vocabulary))
    true_labels = tf.math.argmax(y_data, axis=1)

    if "bert" in model_dir:
        predictions = tf.nn.sigmoid(model.predict(x_padded).logits)
    else:
        predictions = model.predict(x_padded)
    category_predictions = tf.math.argmax(predictions, axis=1)

    pred_file = os.path.join(model_dir, f"{test_name}_pred.txt")
    with open(pred_file, "w") as f:
        for i in range(len(x_data)):
            string = "".join(index_to_char[idx] for idx in x_data[i])
            true_label = "TRUE" if true_labels[i] == 0 else "FALSE"
            predicted_label = "TRUE" if category_predictions[i] == 0 else "FALSE"
            f.write(f"{string}\t{true_label}\t{predicted_label}\n")

    probs_file = os.path.join(model_dir, f"{test_name}_probs.txt")
    with open(probs_file, "w") as f:
        for i in range(len(predictions)):
            f.write(f"{predictions[i, 0]} {predictions[i, 1]}\n")
