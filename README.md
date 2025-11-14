
# 🏥 Clinical Trial Data Management System

### **AI-Powered Natural Language → SQL Engine + Dynamic Table Generator (v3.0)**

This project is a fully integrated **Clinical Trial Data Management System**, built with:

* **Google Gemini 2.0 Flash** for Natural Language → SQL conversion
* **SQLite** as the Clinical Trial database
* **Gradio** interactive application (multi-tab UI)
* **Automatic Fake Data Generator** using **Faker**
* **Dynamic Table Creator** (schema-based flexible table creation)
* **Interactive Clinical Dashboard** using Plotly
* **Google Drive support** for persistence (Colab-based workflow)

This application allows users to **ask clinical questions in plain English**, generate SQL queries automatically, run them safely on the database, create custom tables, and visualize metrics.

---

# 📌 Features Overview

### ✔️ **1. Natural Language → SQL (NL-to-SQL) Engine**

Powered by **Google Gemini API**, allowing queries like:

* “Show patients older than 60”
* “List severe adverse events”
* “Find lab values outside normal range”
* “Count patients by treatment arm”

System response flow:

1. Interpret NL query
2. Generate SQL using Gemini
3. Validate SQL (block DELETE, UPDATE, DROP, etc.)
4. Ask for user confirmation
5. Execute safely
6. Display results as a table

---

### ✔️ **2. Clinical Trial Database (Auto-Generated)**

Database includes 50 patients and supporting tables:

| Table              | Description                  |
| ------------------ | ---------------------------- |
| **patients**       | Demographics + treatment arm |
| **adverse_events** | Patient AEs with severity    |
| **lab_results**    | Lab values + normal ranges   |
| **visits**         | Scheduled vs actual visits   |
| **query_log**      | Query history                |

Each table is generated with **realistic distributions**:

* Age groups
* Visit timelines
* Lab out-of-range logic
* AE generation with random severities

---

### ✔️ **3. Dynamic Table Generator**

Create any custom table with your own schema:

```
employee_name:TEXT
salary:REAL
date_of_joining:DATE
department:TEXT
```

Features:

* Smart data detection (names, emails, salaries, dates, etc.)
* Generates **fake but realistic** values
* Supports TEXT, INTEGER, REAL, DATE, BOOLEAN
* Generate up to **1000 rows automatically**
* Save permanently into the SQLite database

---

### ✔️ **4. Clinical Dashboard**

Visualizes key metrics:

* Total patients
* Active vs completed
* Adverse event distribution
* Patients per site (bar chart)
* Treatment arm distribution (pie chart)

Built using **Plotly** for interactive charts.

---

### ✔️ **5. Google Drive Integration (Colab)**

All data saved in:

```
/content/drive/MyDrive/ClinicalTrialApp/
```

Ensures:

* Database persistence
* Modules saved as .py files
* App reloads even after runtime reset

---

# 📂 Project Structure

```
ClinicalTrialApp/
│
├── clinical_trial.db               # SQLite database
├── nl_to_sql.py                    # Gemini AI NL → SQL engine
├── table_generator.py              # Dynamic table creation + fake data
├── app_gradio.py                   # Full multi-tab Gradio application
├── data_quality_checker.py         # (Optional) Data QC module
├── query_generator.py              # (Optional) SQL template generator
└── final_nlp_with_db_generator.py  # Main notebook (converted)
```

---

# 🧠 Technology Stack

| Component     | Technology                 |
| ------------- | -------------------------- |
| Language      | Python                     |
| Database      | SQLite                     |
| AI Model      | Google Gemini 2.0 Flash    |
| UI Framework  | Gradio                     |
| Fake Data     | Faker library              |
| Visualization | Plotly                     |
| Storage       | Google Drive               |
| Platform      | Google Colab (recommended) |

---

# 🚀 How to Run the Application

### **Step 1: Install Dependencies**

```
pip install pandas numpy plotly sqlalchemy openpyxl gradio google-generativeai faker
```

### **Step 2: Mount Google Drive**

(When running in Colab)

```python
from google.colab import drive
drive.mount('/content/drive')
```

### **Step 3: Run the main script**

```
python final_nlp_with_db_generator.py
```

### **Step 4: Launch the Gradio App**

After execution, you will get:

```
Running on public URL: https://xxxx.gradio.live
```

Open the link in your browser.

---

# 🔑 Gemini API Setup

1. Go to: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key
3. Copy it
4. Go to **API Configuration** tab in the Gradio UI
5. Enter your key & click **Configure API**

After that you're ready to run NL → SQL queries.

---

# 🧪 Example Natural Language Queries

| User Query                  | Auto-Generated SQL                                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------------------- |
| Show all patients           | SELECT * FROM patients LIMIT 100                                                                          |
| Show patients older than 60 | SELECT * FROM patients WHERE age > 60 LIMIT 100                                                           |
| Find severe adverse events  | SELECT * FROM adverse_events WHERE severity='Severe' LIMIT 100                                            |
| Out-of-range lab results    | SELECT * FROM lab_results WHERE test_value < normal_range_low OR test_value > normal_range_high LIMIT 100 |

---

# 🔥 New Features in Version 3.0

* ✔ Dynamic fake data generator with smart column detection
* ✔ Automatic schema-based table creation
* ✔ Enhanced dashboard analytics
* ✔ Query confirmation to avoid accidental execution
* ✔ Modular codebase
* ✔ More realistic clinical data generation
* ✔ Improved NL → SQL reliability with schema guidance

---

# ⚠ Security Note (Important)

Your notebook uses:

```python
import google.generativeai as genai
genai.configure(api_key=YOUR_KEY)
```

👉 **Do NOT upload your API key to GitHub.**
Use environment variables or `.env` file.

---

# 👨‍💻 Author

**Ravi Sankkaran I**

