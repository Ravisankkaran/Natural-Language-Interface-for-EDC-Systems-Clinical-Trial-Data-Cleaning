import gradio as gr
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append('/content/drive/MyDrive/ClinicalTrialApp')

from nl_to_sql import SimpleNLtoSQL
from table_generator import DynamicTableGenerator

DB_PATH = '/content/drive/MyDrive/ClinicalTrialApp/clinical_trial.db'

nl_sql = None
table_gen = DynamicTableGenerator(DB_PATH)

def configure_api(api_key):
    global nl_sql
    if not api_key or api_key.strip() == "":
        return "⚠️ Please enter your Gemini API key", False

    try:
        nl_sql = SimpleNLtoSQL(DB_PATH, api_key=api_key.strip())
        return "✅ Gemini API configured! You can now use the query interface.", True
    except Exception as e:
        return f"❌ Error: {str(e)}", False

def execute_nl_query(user_query, confirmation):
    global nl_sql

    if not nl_sql:
        return "⚠️ Please configure Gemini API first!", None, "", gr.update(visible=False)

    if not user_query or user_query.strip() == "":
        return "Please enter a query.", None, "", gr.update(visible=False)

    try:
        sql_query, status, explanation = nl_sql.parse_query(user_query)

        if status == "success" and sql_query:
            if not confirmation:
                return (
                    f"🔍 Generated SQL Query:\n\n{sql_query}\n\n" +
                    f"💡 Explanation:\n{explanation}\n\n" +
                    "⚠️ Please review and check the confirmation box to execute.",
                    None,
                    sql_query,
                    gr.update(visible=True)
                )

            df_result, exec_status = nl_sql.execute_query(sql_query)

            if exec_status == "success":
                result_text = f"✅ Query executed!\n\n📊 Found {len(df_result)} results"
                return result_text, df_result, sql_query, gr.update(visible=False)
            else:
                return f"❌ Error: {exec_status}", None, sql_query, gr.update(visible=False)
        else:
            return f"⚠️ {explanation}", None, sql_query or "", gr.update(visible=False)

    except Exception as e:
        return f"❌ Error: {str(e)}", None, "", gr.update(visible=False)

def create_custom_table(table_name, columns_text, num_rows):
    """Create a new custom table"""
    if not table_name or not columns_text:
        return "⚠️ Please provide table name and columns!", None

    # Parse columns (format: col1:TEXT, col2:INTEGER, col3:DATE)
    try:
        schema = {}
        for line in columns_text.strip().split('\n'):
            if ':' in line:
                col, dtype = line.split(':')
                schema[col.strip()] = dtype.strip()

        if not schema:
            return "⚠️ Invalid column format! Use: column_name:DATA_TYPE (one per line)", None

        # Create table
        success, msg = table_gen.create_table_from_schema(table_name, schema)
        if not success:
            return msg, None

        # Insert data
        success, data_msg = table_gen.insert_data(table_name, schema, int(num_rows))

        # Show preview
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}" LIMIT 10', conn)
        conn.close()

        return f"{msg}\n{data_msg}\n\n✅ Table created with {num_rows} rows!", df

    except Exception as e:
        return f"❌ Error: {str(e)}", None

def list_all_tables():
    """List all tables in database"""
    tables = table_gen.get_all_tables()
    return "\n".join([f"• {t}" for t in tables])

with gr.Blocks(title="Clinical Trial Data Management", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 🏥 Clinical Trial Data Management System
    ### AI-Powered with Google Gemini + Dynamic Table Generator
    **Version 3.0**
    """)

    with gr.Tab("🔑 API Configuration"):
        gr.Markdown("### Configure Gemini API")

        api_key_input = gr.Textbox(
            label="🔑 Enter Gemini API Key",
            type="password",
            placeholder="Get from https://aistudio.google.com/apikey"
        )
        api_config_btn = gr.Button("⚙️ Configure API", variant="primary")
        api_status = gr.Textbox(label="API Status", lines=2)
        api_configured = gr.State(False)

        api_config_btn.click(
            fn=configure_api,
            inputs=[api_key_input],
            outputs=[api_status, api_configured]
        )

    with gr.Tab("🔍 Query Interface"):
        gr.Markdown("### Ask questions in plain English - Powered by Gemini 2.0")

        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="Your question:",
                    placeholder="e.g., Show patients with severe adverse events",
                    lines=2
                )

                confirmation_checkbox = gr.Checkbox(
                    label="✅ I reviewed the SQL and want to execute it",
                    value=False,
                    visible=False
                )

                with gr.Row():
                    query_btn = gr.Button("🚀 Generate SQL", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear")

        query_output = gr.Textbox(label="Results", lines=8)
        sql_output = gr.Code(label="Generated SQL", language="sql")
        results_df = gr.Dataframe(label="Data", wrap=True)

        query_btn.click(
            fn=execute_nl_query,
            inputs=[query_input, confirmation_checkbox],
            outputs=[query_output, results_df, sql_output, confirmation_checkbox]
        )

        clear_btn.click(
            fn=lambda: ("", None, "", False, gr.update(visible=False)),
            outputs=[query_output, results_df, sql_output, confirmation_checkbox, confirmation_checkbox]
        )

    with gr.Tab("🆕 Create Custom Tables"):
        gr.Markdown("""
        ### 🎨 Dynamic Table Generator
        Create your own custom tables with automatic fake data generation!
        """)

        with gr.Row():
            with gr.Column():
                new_table_name = gr.Textbox(
                    label="📋 Table Name",
                    placeholder="e.g., custom_data"
                )

                columns_input = gr.Textbox(
                    label="📝 Columns (one per line)",
                    placeholder="column1:TEXT\ncolumn2:INTEGER\ncolumn3:DATE\ncolumn4:REAL",
                    lines=8
                )

                gr.Markdown("""
                **Supported Data Types:**
                - TEXT (for names, emails, addresses, etc.)
                - INTEGER (for numbers)
                - REAL (for decimals)
                - DATE (for dates)
                - BOOLEAN (for yes/no)

                **Smart Detection:** Column names like "name", "email", "phone", "address" will auto-generate appropriate data!
                """)

                num_rows_input = gr.Slider(
                    minimum=1,
                    maximum=1000,
                    value=100,
                    step=1,
                    label="📊 Number of Rows to Generate"
                )

                create_table_btn = gr.Button("🎯 Create Table & Generate Data", variant="primary")

            with gr.Column():
                gr.Markdown("### 📚 Existing Tables")
                tables_list = gr.Textbox(
                    label="Current Tables in Database",
                    lines=15,
                    interactive=False
                )
                refresh_tables_btn = gr.Button("🔄 Refresh List")

        create_output = gr.Textbox(label="Status", lines=5)
        preview_df = gr.Dataframe(label="Preview (First 10 Rows)", wrap=True)

        create_table_btn.click(
            fn=create_custom_table,
            inputs=[new_table_name, columns_input, num_rows_input],
            outputs=[create_output, preview_df]
        )

        refresh_tables_btn.click(
            fn=list_all_tables,
            outputs=[tables_list]
        )

        # Auto-load tables on tab load
        app.load(fn=list_all_tables, outputs=[tables_list])

    with gr.Tab("📊 Dashboard"):
        gr.Markdown("### Analytics & Metrics")

        def create_dashboard():
            try:
                conn = sqlite3.connect(DB_PATH)

                # Get stats
                stats = {
                    'total_patients': pd.read_sql_query("SELECT COUNT(*) as count FROM patients", conn).iloc[0]['count'],
                    'active_patients': pd.read_sql_query("SELECT COUNT(*) as count FROM patients WHERE status = 'Active'", conn).iloc[0]['count'],
                    'total_aes': pd.read_sql_query("SELECT COUNT(*) as count FROM adverse_events", conn).iloc[0]['count'],
                    'severe_aes': pd.read_sql_query("SELECT COUNT(*) as count FROM adverse_events WHERE severity = 'Severe'", conn).iloc[0]['count'],
                }

                summary = f"""
CLINICAL TRIAL DASHBOARD
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

KEY METRICS:

👥 Patients:
   • Total: {stats['total_patients']}
   • Active: {stats['active_patients']} ({stats['active_patients']/stats['total_patients']*100:.1f}%)

⚠️ Safety:
   • Total AEs: {stats['total_aes']}
   • Severe AEs: {stats['severe_aes']}
"""

                site_dist = pd.read_sql_query("SELECT site_id, COUNT(*) as count FROM patients GROUP BY site_id", conn)
                fig1 = px.bar(site_dist, x='site_id', y='count', title="Patients by Site")

                treatment_dist = pd.read_sql_query("SELECT treatment_arm, COUNT(*) as count FROM patients GROUP BY treatment_arm", conn)
                fig2 = px.pie(treatment_dist, values='count', names='treatment_arm', title="Treatment Arms")

                conn.close()

                return summary, fig1, fig2

            except Exception as e:
                return f"❌ Error: {str(e)}", None, None

        refresh_btn = gr.Button("🔄 Refresh", variant="primary")

        dashboard_summary = gr.Textbox(label="Metrics", lines=20)

        with gr.Row():
            chart1 = gr.Plot(label="Patients by Site")
            chart2 = gr.Plot(label="Treatment Arms")

        refresh_btn.click(
            fn=create_dashboard,
            outputs=[dashboard_summary, chart1, chart2]
        )

        app.load(
            fn=create_dashboard,
            outputs=[dashboard_summary, chart1, chart2]
        )

    gr.Markdown("""
    ---
    **v3.0** | Powered by Google Gemini | Data in Google Drive | Dynamic Table Generator

    💾 Location: `/content/drive/MyDrive/ClinicalTrialApp/`

    🎯 **New Feature**: Create custom tables with automatic fake data generation!
    """)

print("✅ Enhanced Gradio app created!")
