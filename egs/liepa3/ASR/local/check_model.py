import logging
import os
import sherpa_onnx
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="""Path to the model file.
        """,
    )
    parser.add_argument(
        "--tokens",
        type=str,
        help="""Path to the tokens file.
        """,
    )
    args = parser.parse_args()
    model_f, tokens = args.model, args.tokens
    logging.info(f"Model file: {args.model}")
    logging.info(f"Tokens file: {args.tokens}")
    recognizer = sherpa_onnx.OfflineRecognizer.from_zipformer_ctc(
        model=model_f,
        tokens=tokens,
        debug=True,
    )

    import onnx

    model = onnx.load(model_f)

    for inp in model.graph.input:
        dims = []
        for d in inp.type.tensor_type.shape.dim:
            if d.dim_param:
                dims.append(d.dim_param)
            else:
                dims.append(d.dim_value)

        logging.info(f"{inp.name}: {dims}")

    # Load ONNX model metadata
    logging.info("MODEL LOADED: READY to transcribe")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
