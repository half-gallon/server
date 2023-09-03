import json
import ezkl
import tempfile
from model_lib import extract_mfcc
import numpy as np
from flask import request, jsonify, Flask
import os
from flask_cors import CORS
from pydub import AudioSegment
from mclbn256 import Fr

from constant import input_shape

ARTIFACTS_PATH = "artifacts"


MODEL_PATH = os.path.join(ARTIFACTS_PATH, "network.ezkl")
SETTINGS_PATH = os.path.join(ARTIFACTS_PATH, "settings.json")
PK_PATH = os.path.join(ARTIFACTS_PATH, "pk.key")
SRS_PATH = os.path.join(ARTIFACTS_PATH, "kzg.srs")

app = Flask(__name__)
CORS(app)


def u64_to_fr(array):
    reconstructed_bytes = (
        array[0].to_bytes(8, byteorder="little")
        + array[1].to_bytes(8, byteorder="little")
        + array[2].to_bytes(8, byteorder="little")
        + array[3].to_bytes(8, byteorder="little")
    )
    return Fr(reconstructed_bytes)


def compute_proof(audio):  # witness is a json string
    with tempfile.NamedTemporaryFile() as pffo:
        with tempfile.NamedTemporaryFile() as wfo:
            # write audio to temp file
            wfo.write(audio)
            wfo.flush()

            audio_file_name = wfo.name

            val = extract_mfcc(audio_file_name)
            val = np.array(val)

            val = np.transpose(val)
            val = val.flatten()

            inp = {
                "input_shapes": [input_shape, [1, 2]],
                "input_data": [
                    val.tolist(),
                    [1, 0],
                ],
            }

            witness = tempfile.NamedTemporaryFile()
            audio_input = tempfile.NamedTemporaryFile(mode="w+")
            # now save to json
            json.dump(inp, audio_input)
            audio_input.flush()

            print("HEY4")
            print("audio_input.name", audio_input.name)
            print("MODEL_PATH", MODEL_PATH)
            print("witness.name", witness.name)
            print("SETTINGS_PATH", SETTINGS_PATH)
            wit = ezkl.gen_witness(
                audio_input.name, MODEL_PATH, witness.name, settings_path=SETTINGS_PATH
            )
            print("HEY5")

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

            res = {
                "proof": "0x" + res["proof"],
            }

        return res


@app.route("/health", methods=["GET"])
def health_check():
    print("health check")
    return jsonify({"status": "ok"})


@app.route("/prove", methods=["POST"])
def prove_task():
    print("prove")
    try:
        f = request.files["audio"].read()
        print("file read. try to compute proof")
        res = compute_proof(f)
        print("computed")
        return jsonify(res)

    except Exception as e:
        print(e)

        return repr(e), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "res": "Welcome to ezkl proving server"})


if __name__ == "__main__":
    audio_file = "owner.wav"
    audio = AudioSegment.from_wav(audio_file)

    res = compute_proof(audio)
