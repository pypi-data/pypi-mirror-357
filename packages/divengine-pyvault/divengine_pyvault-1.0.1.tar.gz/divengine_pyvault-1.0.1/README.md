# Divengine Python Vault

**PyVault** is a Python-powered documentation generator that transforms any Python project into a structured [Obsidian](https://obsidian.md) vault. It extracts all classes, functions, and modules, maps their relationships, and builds a fully browsable knowledge graph of the codebase.
![image](https://github.com/user-attachments/assets/38d9f3dd-e001-42e2-b69f-d33bfdae7343)

---

## 🧠 What it does

- Parses your Python project using the `ast` module
- Extracts:
  - 📦 Modules (each `.py` file)
  - 🧩 Functions and methods
  - 🏷️ Classes (including inheritance, methods, and properties)
  - 🔗 Function calls between elements (`uses`)
- Organizes everything into Markdown files inside an Obsidian-ready vault
- Preserves the original folder structure
- Uses Obsidian `[[wiki-style links]]` for graph connections

![image](https://github.com/user-attachments/assets/3577390b-f482-4854-9304-6e6aec358ef4)

---

## 🔧 How to use

1. Clone the repository:

```bash
git clone https://github.com/divengine/pyvault.git
```

2. Install Python ≥ 3.8
  
3. Run the generator:

```bash
git clone https://github.com/psf/black.git
cd pyvault
python pyvault.py ../black/ ../vault-black/
```

The result will appear inside the obsidian_vault/ folder.
