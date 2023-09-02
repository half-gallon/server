## Reference

https://github.com/zkonduit/cryptoidol

## Requirement

- docker
- [model](https://github.com/half-gallon/model) (in the same directory of `server`)

## Install

```bash
python3.10 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# import ezkl artifacts from '../model'
make copy-model

# start api serve
docker compose up
```

Then run server from server repository. (link TBD)
