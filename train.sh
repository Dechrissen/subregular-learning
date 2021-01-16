#!/bin/bash

abort() {
	exit 1
}

trap abort SIGINT


# ------------------ PARAMETERS TO EDIT -----------------------
# -------------------------------------------------------------
UNIVERSAL_ARGS=( --batch-size 64 --epochs 30 --embed-dim 100 )
rnn_type= "simple" # simple / gru / lstm
# -------------------------------------------------------------


# get list of languages from `tags.txt`
LANGS=()
filename="./tags.txt"
while read line
do
  LANGS+=($line)
done < $filename

DATA_SIZES=( 1k 10k 100k )
DROPOUTS=( NoDrop )
DIRECTIONS=( Uni Bi )
TESTS=( Test1 Test2 Test3 )

if [ ! -e models ]; then
	mkdir -v models
fi

for lang in ${LANGS[@]}; do
	for size in ${DATA_SIZES[@]}; do
		for direction in ${DIRECTIONS[@]}; do
			for drop in ${DROPOUTS[@]}; do
				model_dir="models/${direction}_${rnn_type}_${drop}_${lang}_${size}/"
				data_prefix="src/data_gen/data/${size}/${lang}"
				if [ ${drop} == "NoDrop" ]; then
					if [ ${direction} == "Uni" ]; then
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --rnn-type "${rnn_type}" --dropout 0 --bidi False\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					else
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --rnn-type "${rnn_type}" --dropout 0 --bidi True\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					fi
				else
					if [ ${direction} == "Uni" ]; then
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --rnn-type "${rnn_type}" --dropout 0.2 --bidi False\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					else
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --rnn-type "${rnn_type}" --dropout 0.2 --bidi True\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					fi
				fi
				for test in ${TESTS[@]}; do
					python src/neural_net/tensorflow/predict.py --model-dir "${model_dir}" --data-file "${data_prefix}_${test}.txt"
					python src/neural_net/tensorflow/eval.py --predict-file "${model_dir}${test}_pred.txt"
				done
			done
		done
	done
done
