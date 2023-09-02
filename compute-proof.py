import json
import os
import tempfile

import ezkl
from mclbn256 import Fr
import numpy as np

from model_lib import extract_mfcc

ARTIFACTS_PATH = "artifacts"


MODEL_PATH = os.path.join(ARTIFACTS_PATH, "network.ezkl")
SETTINGS_PATH = os.path.join(ARTIFACTS_PATH, "settings.json")
PK_PATH = os.path.join(ARTIFACTS_PATH, "pk.key")
SRS_PATH = os.path.join(ARTIFACTS_PATH, "kzg.srs")


def u64_to_fr(array):
    reconstructed_bytes = (
        array[0].to_bytes(8, byteorder="little")
        + array[1].to_bytes(8, byteorder="little")
        + array[2].to_bytes(8, byteorder="little")
        + array[3].to_bytes(8, byteorder="little")
    )
    return Fr(reconstructed_bytes)


def compute_proof(audio_file_name):  # witness is a json string
    print("processing ", audio_file_name)
    val = extract_mfcc(audio_file_name)
    val = np.array(val)
    print("val.shape (init)", val.shape)

    val = np.transpose(val)
    print("val.shape (after transpose)", val.shape)

    val = val.flatten()
    print("val.shape (after flatten)", val.shape)

    with tempfile.NamedTemporaryFile() as pffo:
        inp = {
            "input_shapes": [[1, 190, 13], [1, 2]],
            "input_data": [
                val.tolist(),
                [1, 0],
            ],
        }
        json.dump(inp, open(f"{audio_file_name}.input.json", "w"), indent=2)

        witness = tempfile.NamedTemporaryFile()
        audio_input = tempfile.NamedTemporaryFile(mode="w+")

        # now save to json
        json.dump(inp, audio_input)
        audio_input.flush()

        print("audio_input.name", audio_input.name)
        print("MODEL_PATH", MODEL_PATH)
        print("witness.name", witness.name)
        print("SETTINGS_PATH", SETTINGS_PATH)

        wit = ezkl.gen_witness(
            audio_input.name, MODEL_PATH, witness.name, settings_path=SETTINGS_PATH
        )
        json.dump(wit, open(f"{audio_file_name}.witness.json", "w"), indent=2)

        res = ezkl.prove(
            witness.name,
            MODEL_PATH,
            PK_PATH,
            pffo.name,
            SRS_PATH,
            "evm",
            "single",
            settings_path=SETTINGS_PATH,
        )
        json.dump(res, open(f"{audio_file_name}.proof.json", "w"), indent=2)

        v0_arr = res["instances"][0][0]
        v1_arr = res["instances"][0][1]

        v0 = u64_to_fr(v0_arr)  # 이게 float number여야 하는데...
        v1 = u64_to_fr(v1_arr)

        print("v0", v0)
        print("v1", v1)

        res = {
            "instances": [str(v0), str(v1)],
            "proof": "0x" + res["proof"],
        }
        json.dump(res, open(f"{audio_file_name}.api.response.json", "w"), indent=2)

    return res


if __name__ == "__main__":
    compute_proof("owner.wav")
    compute_proof("other.wav")
