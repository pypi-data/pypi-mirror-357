**dikshantdata** is a Python package for generating synthetic tabular data using predefined schemas.

### ✅ Features
- Static schema definitions (20+ domain examples)
- Always includes required columns like `id`, `name`
- Smart sampling of optional fields
- DataFrame-only output for easy usage
- dataframe with following name supported : players, animals, students, employees, movies

### 🧪 Example Usage
```python
from dikshantdata import generator

# Generate a student dataset
df = generator.generate("students", rows=5, columns=6)
print(df.head())
```

### 📦 Installation
```bash
pip install dikshantdata
```

### 🛠 Requirements
- Python 3.7+
- pandas

### 🔖 License
MIT

---
Contributions and schema suggestions welcome!
 
