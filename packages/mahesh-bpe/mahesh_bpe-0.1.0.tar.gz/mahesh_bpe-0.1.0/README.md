# Mahesh-BPE

**Mahesh-BPE** is a simple and educational implementation of the Byte Pair Encoding (BPE) algorithm, designed for NLP tokenization and vocabulary compression. It is useful for developers, students, and AI/ML enthusiasts who want to understand and experiment with BPE-based tokenization.

---

## 🚀 Features

- ✅ Pure Python implementation of BPE
- ✂️ Tokenizes text into characters and merges frequent pairs
- ⚙️ Customizable number of merge operations (`epochs`)
- 📚 Returns vocabulary and encoded text
- 🧼 Handles multiple spaces and unknown tokens

---

## 📦 Installation

```bash
pip install mahesh-bpe
````

Or, if you're installing it locally:

```bash
pip install .
```

## 🔧 Usage
```
from mahesh_bpe import BPE

bpe = BPE(epoch=1000)
text = "This is the sample text. This text is a    sample. sa"
bpe.train(text)

print("Vocabulary:", bpe.vocab)
print("Encoded:", bpe.encode("the"))
```

---

## 🧠 How It Works

1. **Tokenization**: Splits input into characters and space-preserved tokens.
2. **Pair Counting**: Finds most frequent adjacent token pairs.
3. **Merging**: Merges those pairs iteratively.
4. **Vocabulary Building**: Updates internal vocabulary.
5. **Encoding**: Applies learned merges to new text.

---

## ⚙️ Parameters

| Parameter | Description                | Default |
| --------- | -------------------------- | ------- |
| `epoch`   | Number of merge iterations | 50      |

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Authors

* **Durja LLC**
* **Manoj Nayak**

```

