# From Words to Returns: Sentiment Analysis of Japanese 10-K Reports Using Advanced Large Language Models

This repository contains the code used in the study **"From words to returns: Sentiment Analysis of Japanese 10-K reports using advanced Large Language Models"**. All scripts and notebooks have been tested in Google Colaboratory (Colab) with Python.

---

## Table of Contents
1. [Overview](#overview)
2. [Data](#data)
3. [Repository Structure](#repository-structure)
4. [Environment Setup](#environment-setup)
5. [Usage](#usage)
6. [License](#license)
7. [References](#references)

---

## Overview

This repository aims to collect Japanese companies’ securities reports (equivalent to the 10-K reports) and perform text-based sentiment analysis to examine potential relationships with stock returns. The main steps include:

1. **Retrieval and Processing of Securities Reports**: Automatically retrieve filings from EDINET (see note below) and extract key sections such as specific keywords and Management Discussion & Analysis (MD&A) parts.

2. **Calculation of Sentiment Scores Using Financial Dictionaries and Large Language Models**: Employ a domain-specific financial sentiment dictionary and advanced Large Language Models (DeBERTa, ChatGPT, Claude, Gemini) to compute positive/negative sentiment scores from the retrieved text.

3. **Model Training and Fine-Tuning**: Fine-tune the DeBERTa model for enhanced accuracy using labeled financial documents.

> **Note:** EDINET (Electronic Disclosure for Investors’ NETwork) is an electronic disclosure system provided by Japan’s Financial Services Agency.  
> **URL**: [https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx](https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx)

---

## Data

We use data extracted from Japanese securities reports obtained from EDINET. The main data items include:

- **Company Information**  
  - Security Code  
  - Company Name  
  - Filer Name  
  - Submission Date  
  - Fiscal Year

- **Document Information**  
  - Document Type (e.g., securities report, quarterly report)  
  - Document ID  
  - Source URL

- **Text Data**  
  - **Extracted MD&A Text**: Management discussion & analysis sections, including corporate policies, strategies, and performance  
  - **Keyword-Extracted Text**: Passages containing predefined financial keywords (e.g., “risk,” “growth,” “profit”)  
  - **Full Text (optional)**: The entire text of the reports, if needed for further analysis

- **Metadata / Tag Information (optional)**  
  - XBRL tags and section labels  
  - Additional date-related information (accounting period, announcement date, etc.)  
  - Any other relevant supplemental metadata

### Data Collection Method

- **EDINET Download Page**  
  - [https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx](https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx)  
  - Use the EDINET website to search and download filings by keywords, filer name, or EDINET code.  
  - The script `Get_securities_report.py` automates the download and text extraction processes.

> **Important**: Please refer to the Financial Services Agency/EDINET terms of use for information regarding any restrictions on data redistribution or publication.

---

## Repository Structure

This repository consists of the following main files:

1. **Get_securities_report.py**  
   - Retrieves Japanese securities reports and extracts specific keywords and MD&A sections.

2. **sentiment_dic.ipynb**  
   - Calculates and outputs positive/negative sentiment values using a financial polarity dictionary.

3. **DeBERTa_tune.ipynb**  
   - Fine-tunes the DeBERTa model on financial documents.

4. **sentiment_DeBERTa.ipynb**  
   - Uses the fine-tuned DeBERTa model to calculate and output positive/negative sentiment values.

5. **sentiment_chatgpt.py**  
   - Utilizes the ChatGPT API to calculate and output positive/negative sentiment values.

6. **sentiment_Claude.ipynb**  
   - Utilizes Claude (Anthropic API) to calculate and output positive/negative sentiment values.

7. **sentiment_Gemini.ipynb**  
   - Utilizes Gemini to calculate and output positive/negative sentiment values.

---

## Environment Setup

Below is an example of how to set up the environment using Google Colab. For local environments, install an equivalent Python version and dependencies.

1. **Python Version**  
   - Python 3.8 or later is recommended.

2. **Required Libraries**  
   - In Colab, you can install the necessary libraries at the beginning of each Notebook (e.g., `!pip install ...`).  
   - For example:
     ```bash
     !pip install transformers sentencepiece
     !pip install openai anthropic  # For ChatGPT or Claude usage
     ...
     ```

3. **Setting Up API Keys (if needed)**  
   - Using ChatGPT or Claude requires setting environment variables for the respective API keys.  
   - For instance:
     ```python
     import os
     os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY'
     os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY'
     ```

---

## Usage

1. **Retrieve Securities Reports**  
   - Run `Get_securities_report.py` to fetch securities reports.  
   - Extracted keywords and MD&A sections will be saved as CSV or text files.  
   - Example:
     ```bash
     python Get_securities_report.py --output_dir ./data/reports
     ```

2. **Sentiment Analysis Using a Financial Dictionary**  
   - Open `sentiment_dic.ipynb` in Colab and run the cells in order.  
   - The script matches words in the reports against a financial polarity dictionary to compute positive/negative sentiment scores.

3. **Fine-Tune the DeBERTa Model**  
   - In `DeBERTa_tune.ipynb`, use your labeled financial data to train and improve the DeBERTa model’s performance.  
   - The fine-tuned model can be saved from the notebook.

4. **Sentiment Analysis with DeBERTa**  
   - Run `sentiment_DeBERTa.ipynb` to calculate sentiment scores using the fine-tuned DeBERTa model.  
   - Input the text data and obtain positive/negative scores.

5. **Sentiment Analysis with Other LLMs**  
   - **sentiment_chatgpt.py**  
     - Uses the ChatGPT API to analyze sentiment.  
     - Make sure to set your API key and run:
       ```bash
       python sentiment_chatgpt.py --input_file ./data/reports/example.txt --output_file ./results/chatgpt_sentiment.csv
       ```
   - **sentiment_Claude.ipynb**  
     - Demonstrates how to use Claude (Anthropic API) for sentiment analysis in a notebook format.
   - **sentiment_Gemini.ipynb**  
     - Demonstrates how to use Gemini for sentiment analysis in a notebook format.

---

## License

All code in this repository is released under the [MIT License](LICENSE), unless otherwise noted.  
Please note that the original text data from EDINET may be subject to the Financial Services Agency/EDINET terms of use regarding redistribution or publication.

---

## References

- **EDINET**: [https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx](https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx)  
- **Hugging Face Transformers**: [https://github.com/huggingface/transformers](https://github.com/huggingface/transformers)  
- **OpenAI**: [https://openai.com/](https://openai.com/)  
- **Anthropic**: [https://www.anthropic.com/](https://www.anthropic.com/)

---
