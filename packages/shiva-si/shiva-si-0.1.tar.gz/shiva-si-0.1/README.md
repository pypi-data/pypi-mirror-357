# Shiva-SI

`shiva-si` is a Python utility package for saving and loading machine learning models using the `.si` format.

### 🔧 Features

- Save any PyTorch model with associated metadata
- Load models with metadata directly for evaluation or deployment
- Inspired by `.pt` and `.npy`, but optimized for AI/ML workflows

### 📦 Install

```bash
pip install shiva-si
```

### 💾 Usage

```python
from shiva.si_format import save_si, load_si
from my_model import MyModel  # your PyTorch model class

# Save
model = MyModel()
save_si(model, "model.si", metadata={"trained_on": "MNIST", "epoch": 5})

# Load
loaded_model, metadata = load_si(MyModel, "model.si")
```

---

### 📁 Contents

- `shiva/core.py` – model training logic
- `shiva/si_format.py` – custom `.si` model saving/loading functions
- `train_and_save.py` – example training script
- `load_and_evaluate.py` – example evaluation script