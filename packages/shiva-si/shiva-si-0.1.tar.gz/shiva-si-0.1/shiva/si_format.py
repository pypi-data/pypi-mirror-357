import os
import torch
import gzip
import bz2
import lzma

# Optional ChromaDB support
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

def _compress_data(data_bytes, compression):
    if compression == "gzip":
        return gzip.compress(data_bytes)
    elif compression == "bz2":
        return bz2.compress(data_bytes)
    elif compression == "lzma":
        return lzma.compress(data_bytes)
    return data_bytes

def _decompress_data(data_bytes, compression):
    if compression == "gzip":
        return gzip.decompress(data_bytes)
    elif compression == "bz2":
        return bz2.decompress(data_bytes)
    elif compression == "lzma":
        return lzma.decompress(data_bytes)
    return data_bytes

def save_si(model, path, metadata=None, optimizer=None, scheduler=None, compression=None, docker_labels=None):
    """
    Save a PyTorch model to .si format with optional compression, metadata, optimizer, and Docker/OCI labels.

    Args:
        model: torch.nn.Module
        path: str
        metadata: dict
        optimizer: torch.optim.Optimizer
        scheduler: torch.optim.lr_scheduler
        compression: str ('gzip', 'bz2', 'lzma')
        docker_labels: dict, OCI-style labels to include
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "model_state": model.state_dict(),
        "metadata": metadata or {},
        "docker_labels": docker_labels or {}
    }
    if optimizer:
        data["optimizer_state"] = optimizer.state_dict()
    if scheduler:
        data["scheduler_state"] = scheduler.state_dict()

    buffer = torch.save(data, _use_new_zipfile_serialization=True, pickle_protocol=4, _return_bytes=True)
    compressed = _compress_data(buffer, compression)
    with open(path, "wb") as f:
        f.write(compressed)
    print(f"✅ Model saved to '{path}' with compression={compression}")

def load_si(model_class, path, device='cpu', optimizer=None, scheduler=None, compression=None):
    """
    Load a .si model file, restoring model, optimizer, scheduler, and returning metadata.

    Args:
        model_class: callable
        path: str
        device: str
        optimizer: optional
        scheduler: optional
        compression: str

    Returns:
        model, metadata
    """
    with open(path, "rb") as f:
        compressed_data = f.read()
    buffer = _decompress_data(compressed_data, compression)
    data = torch.load(buffer, map_location=device)

    model = model_class()
    model.load_state_dict(data["model_state"])

    if optimizer and "optimizer_state" in data:
        optimizer.load_state_dict(data["optimizer_state"])
    if scheduler and "scheduler_state" in data:
        scheduler.load_state_dict(data["scheduler_state"])

    metadata = data.get("metadata", {})
    docker_labels = data.get("docker_labels", {})
    print(f"✅ Loaded model with metadata: {metadata}")
    if docker_labels:
        print(f"📦 Docker/OCI labels: {docker_labels}")
    return model, metadata

def export_to_chroma(embedding_vector, model_name="model", collection_name="models"):
    """
    Store a model embedding in ChromaDB (if installed).
    """
    if not CHROMA_AVAILABLE:
        raise ImportError("ChromaDB is not installed. Run `pip install chromadb` to use this feature.")

    client = chromadb.Client()
    collection = client.get_or_create_collection(collection_name)
    collection.add(
        documents=[f"Model: {model_name}"],
        embeddings=[embedding_vector],
        ids=[model_name]
    )
    print(f"✅ Stored embedding to ChromaDB under collection '{collection_name}'.")

def export_to_onnx(model, dummy_input, output_path, opset_version=11):
    """
    Export a PyTorch model to ONNX format.

    Args:
        model: torch.nn.Module
        dummy_input: torch.Tensor
        output_path: str
        opset_version: int
    """
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )
    print(f"✅ Model exported to ONNX at '{output_path}'")