#! /bin/bash

AHLT=.
export PYTHONPATH=$AHLT/util


$AHLT/util/corenlp-server.sh -quiet true -port 9000 -timeout 15000  &
sleep 1

echo "Extracting features..."
python3 extract-features.py $AHLT/data/devel/ > features/devel.feat &
python3 extract-features.py $AHLT/data/train/ > features/train.feat

kill `cat /tmp/corenlp-server.running`

# train MEM model
echo "Training MEM model..."
python3 train.py features/train.feat model.mem C=10
# run MEM model
echo "Running MEM model..."
python3 predict.py features/devel.feat model.mem > results/devel-MEM.out
# evaluate MEM results
echo "Evaluating MEM results..."
python3 $AHLT/util/evaluator.py DDI $AHLT/data/devel devel-MEM.out > results/devel-MEM.stats

# train SVM model
echo "Training SVM model..."
python3 train.py features/train.feat model.svm C=10
# run SVM model
echo "Running SVM model..."
python3 predict.py features/devel.feat model.svm > results/devel-SVM.out
# evaluate SVM results
echo "Evaluating SVM results..."
python3 $AHLT/util/evaluator.py DDI $AHLT/data/devel results/devel-SVM.out > results/devel-SVM.stats

