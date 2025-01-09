

export PYTHONPATH="../EmbeddedFuzzer:../EmbeddedFuzzer/src"
/root/anaconda3/bin/python -m lithium ../EmbeddedFuzzer/src/experiment/interesting.py "$1"
rm -rf tmp1
