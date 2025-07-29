import argparse
import torch
from shiva.si_format import save_si, load_si, export_to_onnx

def main():
    parser = argparse.ArgumentParser(description="Shiva CLI for .si model format")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Save command
    save_parser = subparsers.add_parser("save", help="Save a PyTorch model to .si format")
    save_parser.add_argument("--model-class", required=True, help="Python module path to the model class (e.g., mymodule.MyModel)")
    save_parser.add_argument("--output", required=True, help="Path to save the .si file")
    save_parser.add_argument("--compression", choices=["gzip", "bz2", "lzma"], help="Optional compression")
    save_parser.add_argument("--metadata", help="Optional metadata as key=value pairs", nargs='*')

    # Load command
    load_parser = subparsers.add_parser("load", help="Load a .si file")
    load_parser.add_argument("--model-class", required=True, help="Python module path to the model class (e.g., mymodule.MyModel)")
    load_parser.add_argument("--input", required=True, help="Path to the .si file")
    load_parser.add_argument("--compression", choices=["gzip", "bz2", "lzma"], help="Optional compression")

    # ONNX export command
    onnx_parser = subparsers.add_parser("export-onnx", help="Export a model to ONNX")
    onnx_parser.add_argument("--model-class", required=True, help="Python module path to the model class")
    onnx_parser.add_argument("--output", required=True, help="Path to save the .onnx file")

    args = parser.parse_args()

    # Dynamic import for model class
    module_path, class_name = args.model_class.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    model_class = getattr(module, class_name)

    if args.command == "save":
        model = model_class()
        metadata_dict = {}
        if args.metadata:
            for item in args.metadata:
                if "=" in item:
                    k, v = item.split("=", 1)
                    metadata_dict[k] = v
        save_si(model, args.output, metadata=metadata_dict, compression=args.compression)

    elif args.command == "load":
        model, metadata = load_si(model_class, args.input, compression=args.compression)
        print("✅ Metadata:", metadata)

    elif args.command == "export-onnx":
        model = model_class()
        dummy_input = torch.randn(1, 10)
        export_to_onnx(model, dummy_input, args.output)

if __name__ == "__main__":
    main()