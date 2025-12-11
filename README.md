# Online Shopping Platform Product Consumption Comparison
Key word: Python crawler; Newegg.com website; GPU, SSD analysis and visualization
# DSCI 510 Final Project Online Shopping Platform Product Consumption Comparison
## Web Scraping & Product Analytics for RTX 5090 GPUs and 2TB SSDs

---
## enviroment 
```bash
pip install -r requirements.txt
```
beautifulsoup4>=4.12.0
matplotlib>=3.7.0
numpy>=1.24.0
pandas>=2.0.0
requests>=2.31.0
scipy>=1.10.0
seaborn>=0.12.0

## How to run

This project includes an automated pipeline inside `main.py`.  
By running this file, the entire workflow will execute sequentially:

- Web scraping from Newegg — currently commented out  
- Data cleaning and preprocessing  
- Exploratory data analysis  
- Visualization generation

```bash
python main.py
```


## 📌 Project Overview

This project collects, cleans, and analyzes product data from **Newegg.com**, focusing on two hardware categories:

- **NVIDIA RTX 5090 Graphics Cards**
- **2TB Solid State Drives (SSDs)**

The goal is to perform brand-level comparisons, examine pricing and rating patterns, and visualize market trends using Python-based scraping and analytics.

---

## 📂 Data Sources

All product data was collected through **custom web scraping** using Python’s `requests` and `BeautifulSoup`.  
Newegg does **not** provide a public API, so HTML parsing was required.

### CSV Data includes:
- title
- product_url
- Brand
- Price
- rating
- Number of reviews
- Shipping information

### Pages Scraped:
| Product Category | Pages | Method |
|------------------|--------|--------|
| RTX 5090 GPUs     | 8 pages | HTML scraping |
| 2TB SSDs          | 2 pages | HTML scraping |

Raw HTML is saved locally, and cleaned CSV files are generated for analysis.

---

## 🧭 Repository Structure

```md
project_root/
├── data/
│   ├── raw/                     # Raw scraped CSV files and original HTML
│   ├── processed/               # Cleaned, normalized CSVs and analysis logs
│   └── images/                  # Generated visualization charts (GPU & SSD)
│
├── result/
│   ├── final_report.pdf
│
├── src/
│   ├── Analysis.py              # Statistical analysis & aggregation functions
│   ├── Classify_gpu.py          # GPU categorization logic
│   ├── Clean.py                 # Data cleaning pipeline
│   ├── Fetch.py                 # Web scraping module (HTML scraping)
│   ├── Visualization_5090.py    # Visualization functions for GPU dataset
│   ├── Visualization_ssd.py     # Visualization functions for SSD dataset
│   └── main.py                  # Main entry point — runs scraping, cleaning, analysis & plotting
│
├── requirements.txt             # Python dependencies
├── function_doc.md		           # All function description
├── project_proposal
└── README.md                    # Project documentation
```

## 👨‍💻 Author
**Yiming Xiong**
📧 Email: xiongyim@usc.edu
**Haosen Guo**
📧 Email: haosengu@usc.edu
