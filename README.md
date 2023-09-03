## Reference

https://github.com/zkonduit/cryptoidol

## Requirement

- [model](https://github.com/half-gallon/model) (in the same directory of `server`)

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
gunicorn app_alone:app -w3 -b 0.0.0.0:6000 --timeout 120
```
