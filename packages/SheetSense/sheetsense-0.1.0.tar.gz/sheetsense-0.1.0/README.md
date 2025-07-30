#   Structured Data Extractor

This tool converts messy Excel Sheets into structured JSON using OpenAI

##  Installation

```bash
pip install .
```

# Usage
```python
from .Excel_Json_Converter import StructuredDataExtractor

extractor = StructuredDataExtractor
extractor.extract("ExcelFile.xlsx")

```

---

#   Requirements

```txt
pandas
openai
python-dotenv
```