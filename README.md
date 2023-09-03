# half-gallon: proving server

This flask app requires `.onnx` and ezkl artifacts generated from [model](https://github.com/half-gallon/model). It receives `.wav` audio of user and return the proof tell that the input voice matches trained voices to the model.

## Reference

https://github.com/zkonduit/cryptoidol

## Requirement

- [model](https://github.com/half-gallon/model) (in the same directory of `server`)
- python@3.10.13

## Install

```bash
python3.10 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# import ezkl artifacts from '../model'. See more https://github.com/half-gallon/model
make copy-model

# (optional) test proof generation with `owner.wav`, `other.wav`
python compute-proof.py

# start api server
# note that api server with complex model cannot generate proof within timeout
gunicorn app_alone:app -w3 -b 0.0.0.0:6000 --timeout 120
```
