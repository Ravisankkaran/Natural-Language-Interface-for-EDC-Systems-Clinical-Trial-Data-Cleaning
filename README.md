🧬 Natural Language Interface for EDC Systems – Clinical Trial Data Cleaning

A Machine Learning + NLP powered system designed to enable natural language-based data cleaning instructions for Electronic Data Capture (EDC) platforms used in clinical trials.
The system interprets user queries written in plain English and automatically performs cleaning operations on clinical datasets.

📌 Overview

Clinical trial datasets often contain inconsistencies, missing values, outliers, or formatting errors. Data managers usually perform manual cleaning using SQL or spreadsheet operations.

This project introduces an AI-driven Natural Language Interface (NLI) where the user simply types cleaning instructions like:

“Remove records where age is missing”

“Replace negative height values with the median”

“Filter patients treated with Drug A between visit 1 and 3”

The system interprets the command using NLP and applies the correct transformation on the dataset.

🌟 Key Features

Converts natural language instructions → structured data cleaning actions

Handles missing values, outliers, filtering, transformations

Uses NLP: tokenization, intent classification, entity recognition

Applies cleaning tasks automatically to clinical datasets

Includes complete data preprocessing

Model evaluation and performance metrics

Easily extensible to real-world EDC systems

📊 Dataset

The dataset includes typical clinical trial fields such as:

Subject ID

Age, Sex

Visit information

Lab values

Treatment details

Medical history

Biomarker readings

The dataset is used to simulate real-world clinical data inconsistencies.

🧹 System Architecture
1️⃣ Natural Language Input

User gives instruction in plain English.

2️⃣ NLP Processing

Tokenization

Lemmatization

Intent detection

Parameter extraction

Entity recognition (columns, values, conditions)

3️⃣ Cleaning Logic Mapping

Maps intent to specific data-cleaning actions:

Intent	Example Command	Action
Drop Missing	“Remove rows where age is missing”	df.dropna on column
Replace Values	“Replace negative values in weight”	df[column].apply()
Filter Rows	“Show patients with glucose > 200”	df[df[column] > value]
Standardization	“Convert dates to YYYY-MM-DD”	pd.to_datetime
4️⃣ Execution Engine

Executes pandas operations dynamically based on parsed command.

5️⃣ Cleaned Output Dataset

Returns cleaned data as DataFrame.

🔧 Algorithms & NLP Techniques Used

Spacy / NLTK for tokenization & POS tagging

TF-IDF + Logistic Regression for intent classification

Rule-based entity extraction

Mapping layer for converting intent → pandas code

Pandas for data cleaning execution

📈 Evaluation Metrics

For NLP components:

Intent accuracy

Precision & recall

Confusion matrix

Entity extraction accuracy

For data transformations:

Before–after comparison

Missing value reduction

Outlier correction

Validity checks

🧪 Cleaning Operations Supported

✔ Remove rows based on missing values
✔ Replace invalid/negative measurements
✔ Standardize date formats
✔ Filter rows using conditions
✔ Rename columns
✔ Drop duplicates
✔ Aggregate values (mean, median)
✔ Normalize numeric fields

📂 Project Structure
.
├── data/
│   ├── clinical_raw.csv
│   └── clinical_cleaned.csv
├── models/
│   └── intent_classifier.pkl
├── nlp/
│   ├── intent_mapping.json
│   └── entity_extractor.py
├── notebook/
│   └── clinical_data_cleaning_NLI.ipynb
├── app/
│   └── nli_api.py
├── README.md
└── requirements.txt

🛠 Tech Stack

Python

Pandas

NumPy

SpaCy / NLTK

Scikit-learn

TF-IDF Vectorizer

Logistic Regression

Regex-based entity extraction

Matplotlib / Seaborn

▶️ How to Use
Step 1 — Install dependencies
pip install -r requirements.txt

Step 2 — Open the Notebook
Natural Language Interface for EDC Systems – Clinical Trial Data Cleaning.ipynb

Step 3 — Train the NLP Model

Train intent classifier

Build entity extractor rules

Step 4 — Enter natural language queries

Example:

"Remove rows where cholesterol is missing"


The system will automatically clean the dataset.

✨ Future Enhancements

Integration with RedCap / Medidata Rave / OpenClinica EDC systems

LLM-powered command parsing

Web-based chatbot UI

Exporting cleaning logs for audit trail

Deep learning–based entity extraction (BERT, BioBERT)

Voice-command support

👤 Author

Ravi Sankkaran I
