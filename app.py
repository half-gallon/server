import json
from celery import Celery
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
app.config["CELERY_BROKER_URL"] = os.getenv("APP_BROKER_URI")
app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app)

celery = Celery(
    "worker", backend=os.getenv("APP_BACKEND"), broker=app.config["CELERY_BROKER_URL"]
)

celery.conf.update(app.config)


# mfcc extraction from augmented data


def u64_to_fr(array):
    reconstructed_bytes = (
        array[0].to_bytes(8, byteorder="little")
        + array[1].to_bytes(8, byteorder="little")
        + array[2].to_bytes(8, byteorder="little")
        + array[3].to_bytes(8, byteorder="little")
    )
    return Fr(reconstructed_bytes)


@celery.task
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

            val = extract_mfcc(wfo.name)

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

            wit = ezkl.gen_witness(
                audio_input.name, MODEL_PATH, witness.name, settings_path=SETTINGS_PATH
            )

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
    return jsonify({"status": "ok"})


@app.route("/prove", methods=["POST"])
def prove_task():
    print("updated???")
    try:
        f = request.files["audio"].read()
        result = compute_proof.delay(f)
        result.ready()  # returns true when ready
        res = result.get()  # bytes of proof

        return jsonify({"status": "ok", "res": res})

    except Exception as e:
        return repr(e), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "res": "Welcome to ezkl proving server"})


if __name__ == "__main__":
    addr = "0xb794f5ea0ba39494ce839613fffba74279579268"
    addr_int = int(addr, 0)
    rep = Fr(addr_int)
    print(rep)

    ser = rep.serialize()

    first_byte = int.from_bytes(ser[0:8], "little")
    second_byte = int.from_bytes(ser[8:16], "little")
    third_byte = int.from_bytes(ser[16:24], "little")
    fourth_byte = int.from_bytes(ser[24:32], "little")

    print(first_byte)
    print(second_byte)
    print(third_byte)
    print(fourth_byte)

    reconstructed_bytes = (
        first_byte.to_bytes(8, byteorder="little")
        + second_byte.to_bytes(8, byteorder="little")
        + third_byte.to_bytes(8, byteorder="little")
        + fourth_byte.to_bytes(8, byteorder="little")
    )

    recon = Fr.deserialize(reconstructed_bytes)

    assert rep == recon
