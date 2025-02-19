# From Words to Returns: Sentiment Analysis of Japanese 10-K Reports Using Advanced Large Language Models

This repository contains the code used in the study **"From Words to Returns: Sentiment Analysis of Japanese 10-K Reports Using Advanced Large Language Models"**. All scripts and notebooks have been tested in Google Colaboratory (Colab) with Python.

## Table of Contents
1. [Overview](#overview)  
2. [Data](#data)  
3. [Repository Structure](#repository-structure)  
4. [Environment Setup](#environment-setup)  
5. [Usage](#usage)  
6. [Note](#note)  
7. [Author](#author)

---

## Overview

This repository aims to:

- Collect Japanese companies’ securities reports (equivalent to 10-K reports).
- Use text-based sentiment analysis to explore potential relationships with stock returns.

The main steps include:

1. **Retrieval and Processing of Securities Reports**  
   Automatically retrieve filings from EDINET and extract key sections such as specific keywords and Management Discussion & Analysis (MD&A).

2. **Calculation of Sentiment Scores Using Financial Dictionaries and Large Language Models**  
   Employ a domain-specific financial sentiment dictionary and advanced Large Language Models (DeBERTa, ChatGPT, Claude, Gemini) to compute positive/negative sentiment scores.

3. **Model Training and Fine-Tuning**  
   Fine-tune the DeBERTa model for enhanced accuracy using labeled financial documents.

> **Note:**  
> EDINET (Electronic Disclosure for Investors’ NETwork) is an electronic disclosure system provided by Japan’s Financial Services Agency.  
> URL: [https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx](https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx)

---

## Data

We use data extracted from Japanese securities reports obtained from EDINET. The main data items include:

- **Company Information**  
  \- Security Code  
  \- Company Name  
  \- Filer Name  
  \- Submission Date  
  \- Fiscal Year

- **Document Information**  
  \- Document Type (e.g., securities report, quarterly report)  
  \- Document ID  
  \- Source URL

- **Text Data**  
  \- **Extracted MD&A Text**: Management Discussion & Analysis sections, including corporate policies, strategies, and performance  
  \- **Keyword-Extracted Text**: Passages containing predefined financial keywords (e.g., “risk,” “growth,” “profit”)  
  \- **Full Text (optional)**: The entire text of the reports, if needed for further analysis

- **Metadata / Tag Information (optional)**  
  \- XBRL tags and section labels  
  \- Additional date-related information (accounting period, announcement date, etc.)  
  \- Other relevant supplemental metadata

### Data Collection Method

- **EDINET Download Page**  
  [https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx](https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx)  
  Use the EDINET website to search and download filings by keywords, filer name, or EDINET code.  
  The script `Get_securities_report.py` automates the download and text-extraction process.

> **Important:**  
> Please refer to the Financial Services Agency/EDINET terms of use for information regarding any restrictions on data redistribution or publication.

---

## Repository Structure

This repository consists of the following main files and notebooks:

- **`Get_securities_report.py`**  
  Retrieves Japanese securities reports and extracts specific keywords and MD&A sections.

- **`sentiment_dic.ipynb`**  
  Calculates and outputs positive/negative sentiment values using a financial polarity dictionary.

- **`DeBERTa_tune.ipynb`**  
  Fine-tunes the DeBERTa model on financial documents.

- **`sentiment_DeBERTa.ipynb`**  
  Uses the fine-tuned DeBERTa model to calculate and output positive/negative sentiment values.

- **`sentiment_chatgpt.py`**  
  Utilizes the ChatGPT API to calculate and output positive/negative sentiment values.

- **`sentiment_Claude.ipynb`**  
  Utilizes Claude (Anthropic API) to calculate and output positive/negative sentiment values.

- **`sentiment_Gemini.ipynb`**  
  Utilizes Gemini to calculate and output positive/negative sentiment values.

---

## Environment Setup

Below is an example of how to set up the environment using Google Colab. For local environments, ensure that you have a compatible Python version and install the required dependencies.

- **Python Version**  
  Python 3.8 or later is recommended.

- **Required Libraries**  
  In Colab, you can install the necessary libraries at the beginning of each notebook, for example:
  ```bash
  !pip install transformers sentencepiece
  !pip install openai anthropic  # For ChatGPT or Claude usage
  # Add other libraries as needed

---

## Usage

### 1. Retrieve Securities Reports
1. Run `Get_securities_report.py` to fetch securities reports.  
2. Extracted keywords and MD&A sections will be saved as CSV or text files.  

   ```bash
   python Get_securities_report.py --output_dir ./data/reports

### 2. Sentiment Analysis Using a Financial Dictionary
1. Open `sentiment_dic.ipynb` in Colab.  
2. Run the cells in order to match words in the reports against a financial polarity dictionary and compute positive/negative sentiment scores.

### 3. Fine-Tune the DeBERTa Model
1. In `DeBERTa_tune.ipynb`, train the model using your labeled financial data.  
2. Save the fine-tuned model for subsequent use.

### 4. Sentiment Analysis with DeBERTa
1. Run `sentiment_DeBERTa.ipynb` to calculate sentiment scores using the fine-tuned DeBERTa model.  
2. Provide the text data to obtain positive/negative scores.

### 5. Sentiment Analysis with Other LLMs

- **`sentiment_chatgpt.py`**
  Uses the ChatGPT API to analyze sentiment.  
     ```bash
     python sentiment_chatgpt.py --input_file ./data/reports/example.txt --output_file ./results/chatgpt_sentiment.csv

- **`sentiment_Claude.ipynb`**
  Demonstrates how to use Claude (Anthropic API) for sentiment analysis in a notebook format.

- **`sentiment_Gemini.ipynb`**
  Demonstrates how to use Gemini for sentiment analysis in a notebook format.

## Note
Intermediate files produced by this code have been excluded from this documentation due to size constraints.

## Author
* Moe Nakasuji (Kwansei Gakuin University)
* Katsuhiko Okada (Kwansei Gakuin University)
* Yasutomo Tsukioka (Kwansei Gakuin University)
* Takahiro Yamasaki (Osaka Sangyo University)
