# Sentiment Analysis: From Words to Returns

This repository contains the code used in the paper:  
**"From words to returns: Sentiment analysis of Japanese 10-K reports using advanced Large Language Models."**

---

## Overview

The main objectives of this project are:

1. **Retrieving Japanese companies' Securities Reports** and extracting specific keywords along with the Management Discussion and Analysis (MD&A) sections.
2. **Performing sentiment analysis** using a variety of methods:
   - **Financial polarity dictionary**
   - **Fine-tuned DeBERTa model**
   - **ChatGPT**, **Claude**, and **Gemini** models

All scripts and notebooks have been tested on **Google Colaboratory** (Colab) using **Python**.

---

## Repository Structure

```plaintext
sentiment-analysis-words-to-return/
├── Get_securities_report.py
├── sentiment_dic.ipynb
├── DeBERTa_tune.ipynb
├── sentiment_DeBERTa.ipynb
├── sentiment_chatgpt.py
├── sentiment_Claude.ipynb
└── sentiment_Gemini.ipynb
