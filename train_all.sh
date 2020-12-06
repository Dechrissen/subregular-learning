#!/bin/bash

abort() {
	exit 1
}

trap abort SIGINT

UNIVERSAL_ARGS=( --batch-size 64 --epochs 50 --embed-dim 100 --rnn-type gru )

LANGS=( SL.4.2.1 SL.4.2.2 SL.4.2.4 SP.4.2.1 SP.4.2.2 SP.4.2.4 TSL.0 TSL.1 TSL.2 )
DATA_SIZES=( 10k 100k )
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
				model_dir="models/${direction}GRU_${drop}_${lang}_${size}/"
				data_prefix="src/data_gen/data_3langs/${size}/${lang}"
				if [ ${drop} == "NoDrop" ]; then
					if [ ${direction} == "Uni" ]; then
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --dropout 0 --bidi False\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					else
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --dropout 0 --bidi True\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					fi
				else
					if [ ${direction} == "Uni" ]; then
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --dropout 0.2 --bidi False\
							--train-data "${data_prefix}_Training.txt" --val-data "${data_prefix}_Dev.txt" --output-dir "${model_dir}"
					else
						python src/neural_net/tensorflow/main.py "${UNIVERSAL_ARGS[@]}" --dropout 0.2 --bidi True\
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
