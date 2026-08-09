#!/usr/bin/env python3
"""Build the semantic search vectors for the glossary.

Embeds every command (cmd + desc + category + tooltip) with the
Xenova/multilingual-e5-small ONNX model (asymmetric: passages use the
'passage: ' prefix; the query side uses 'query: ' in the browser).

Output: search_vectors.json
  {
    "model": "Xenova/multilingual-e5-small",
    "format": "fp16",           # half-precision little-endian, row-major
    "dim": 384,
    "ids": [id per row, in row order],
    "vectors_b64": "<base64 of count*dim float16 values>"
  }

The browser decodes vectors_b64 with atob() + DataView.getFloat16 and dot-
products the query embedding against every row.

Requires a venv with onnxruntime + tokenizers + numpy:
    python3 -m venv /tmp/ltg-emb && /tmp/ltg-emb/bin/pip install onnxruntime tokenizers numpy
    MODEL_DIR=/tmp/ltg-emb/models ./venv/bin/python scripts/build_embeddings.py

Model files (download once):
    https://huggingface.co/Xenova/multilingual-e5-small/resolve/main/onnx/model_quantized.onnx
    https://huggingface.co/Xenova/multilingual-e5-small/resolve/main/tokenizer.json
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_PATH = ROOT / "commands.json"
OUT_PATH = ROOT / "search_vectors.json"

MODEL_ID = "Xenova/multilingual-e5-small"
MODEL_DIR = Path(os.environ.get("MODEL_DIR", "/tmp/ltg-emb/models"))
PASSAGE_PREFIX = "passage: "
DIM = 384


def load_corpus() -> list[dict]:
    return json.loads(COMMANDS_PATH.read_text())["commands"]


def text_for(c: dict) -> str:
    return f"{c['cmd']} {c['desc']} {c['category']} {c['tooltip']}"


def load_model():
    tok = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
    sess = ort.InferenceSession(
        str(MODEL_DIR / "model.onnx"), providers=["CPUExecutionProvider"]
    )
    inp_names = [i.name for i in sess.get_inputs()]
    return tok, sess, inp_names


def embed(texts: list[str], tok, sess, inp_names, prefix: str = "") -> np.ndarray:
    vecs = []
    for t in texts:
        enc = tok.encode((prefix + t) if prefix else t)
        ids = np.array([enc.ids], dtype=np.int64)
        mask = np.array([enc.attention_mask], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in inp_names:
            feed["token_type_ids"] = np.zeros_like(ids)
        h = sess.run(None, feed)[0][0]  # [seq, hidden]
        m = mask[0].astype(np.float32)[:, None]
        pooled = (h * m).sum(axis=0) / np.maximum(m.sum(axis=0), 1e-9)
        norm = np.linalg.norm(pooled)
        vecs.append(pooled / max(norm, 1e-9))
    return np.stack(vecs)


def main() -> int:
    if not (MODEL_DIR / "model.onnx").exists():
        print(f"Model files missing in {MODEL_DIR} — download first (see docstring).")
        return 1

    cmds = load_corpus()
    texts = [text_for(c) for c in cmds]
    print(f"corpus: {len(cmds)} commands | model: {MODEL_ID}")

    tok, sess, inp_names = load_model()
    t0 = time.time()
    vecs = embed(texts, tok, sess, inp_names, prefix=PASSAGE_PREFIX)
    print(f"embedded {len(vecs)} docs in {time.time()-t0:.1f}s")

    ids = [int(c["id"]) for c in cmds]
    if vecs.shape[1] != DIM:
        print(f"WARNING: model dim is {vecs.shape[1]}, expected {DIM}")
    f16 = vecs.astype(np.float16)
    payload = {
        "model": MODEL_ID,
        "format": "fp16",
        "dim": int(vecs.shape[1]),
        "ids": ids,
        "vectors_b64": base64.b64encode(f16.tobytes()).decode("ascii"),
    }
    OUT_PATH.write_text(json.dumps(payload))
    print(f"wrote {OUT_PATH.name}: {OUT_PATH.stat().st_size/1e6:.2f} MB "
          f"({len(ids)} vectors x {vecs.shape[1]} fp16)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
