import sqlite3
import pandas as pd
from typing import Dict, List
from datetime import datetime

class DataQualityChecker:
    """Automated data quality checks for clinical trial data"""

    def __init__(self, db_path):
        self.db_path = db_path

    def run_all_checks(self) -> Dict:
        """Run all data quality checks"""
        conn = sqlite3.connect(self.db_path)

        results = {
            'missing_data': self.check_missing_data(conn),
            'outliers': self.check_lab_outliers(conn),
            'protocol_deviations': self.check_protocol_deviations(conn),
            'duplicates': self.check_duplicates(conn),
            'date_anomalies': self.check_date_anomalies(conn),
            'unresolved_events': self.check_unresolved_events(conn)
        }

        conn.close()
        return results

    def check_missing_data(self, conn) -> List[Dict]:
        """Check for missing critical data"""
        issues = []

        # Missing severity
        query = "SELECT event_id, patient_id, event_term, event_date FROM adverse_events WHERE severity IS NULL"
        missing_severity_df = pd.read_sql_query(query, conn)
        for _, row in missing_severity_df.iterrows():
            issues.append({
                'type': 'Missing Data',
                'table': 'adverse_events',
                'field': 'severity',
                'patient_id': row['patient_id'],
                'event_id': row['event_id'],
                'event_term': row['event_term'],
                'event_date': row['event_date'],
                'severity': 'High',
                'description': f"Adverse event '{row['event_term']}' for patient {row['patient_id']} missing severity"
            })

        # Missing resolved status
        query = "SELECT event_id, patient_id, event_term, event_date FROM adverse_events WHERE resolved IS NULL"
        missing_resolved_df = pd.read_sql_query(query, conn)
        for _, row in missing_resolved_df.iterrows():
            issues.append({
                'type': 'Missing Data',
                'table': 'adverse_events',
                'field': 'resolved',
                'patient_id': row['patient_id'],
                'event_id': row['event_id'],
                'event_term': row['event_term'],
                'event_date': row['event_date'],
                'severity': 'Medium',
                'description': f"Adverse event '{row['event_term']}' for patient {row['patient_id']} missing resolution"
            })

        return issues

    def check_lab_outliers(self, conn) -> List[Dict]:
        """Detect lab values outside normal ranges"""
        query = """
        SELECT patient_id, test_name, test_value, unit, test_date, normal_range_low, normal_range_high,
               CASE
                   WHEN test_value < normal_range_low THEN 'Low'
                   WHEN test_value > normal_range_high THEN 'High'
               END as outlier_type
        FROM lab_results
        WHERE test_value < normal_range_low OR test_value > normal_range_high
        """

        outliers_df = pd.read_sql_query(query, conn)

        issues = []
        for _, row in outliers_df.iterrows():
            if row['outlier_type'] == 'High':
                deviation = (row['test_value'] - row['normal_range_high']) / row['normal_range_high']
            else:
                deviation = (row['normal_range_low'] - row['test_value']) / row['normal_range_low']

            if deviation > 0.5:
                severity = 'Critical'
            elif deviation > 0.2:
                severity = 'High'
            else:
                severity = 'Medium'

            issues.append({
                'type': 'Lab Outlier',
                'patient_id': row['patient_id'],
                'test_name': row['test_name'],
                'test_value': row['test_value'],
                'unit': row['unit'],
                'test_date': row['test_date'],
                'normal_range_low': row['normal_range_low'],
                'normal_range_high': row['normal_range_high'],
                'outlier_type': row['outlier_type'],
                'severity': severity,
                'description': f"{row['test_name']}: {row['test_value']} {row['unit']} ({row['outlier_type']})"
            })

        return issues

    def check_protocol_deviations(self, conn) -> List[Dict]:
        """Check for visit protocol deviations"""
        query = """
        SELECT patient_id, visit_number, visit_date, scheduled_date, visit_type,
               CAST((julianday(visit_date) - julianday(scheduled_date)) AS INTEGER) as days_difference
        FROM visits
        WHERE julianday(visit_date) - julianday(scheduled_date) > 7
        """

        deviations_df = pd.read_sql_query(query, conn)

        issues = []
        for _, row in deviations_df.iterrows():
            days_late = row['days_difference']

            if days_late > 21:
                severity = 'Critical'
            elif days_late > 14:
                severity = 'High'
            else:
                severity = 'Medium'

            issues.append({
                'type': 'Protocol Deviation',
                'patient_id': row['patient_id'],
                'visit_number': row['visit_number'],
                'visit_type': row['visit_type'],
                'visit_date': row['visit_date'],
                'scheduled_date': row['scheduled_date'],
                'days_late': days_late,
                'severity': severity,
                'description': f"{row['visit_type']} for patient {row['patient_id']} {days_late} days late"
            })

        return issues

    def check_duplicates(self, conn) -> List[Dict]:
        """Check for duplicate records"""
        issues = []

        query = """
        SELECT patient_id, COUNT(*) as duplicate_count
        FROM patients
        GROUP BY patient_id
        HAVING COUNT(*) > 1
        """

        duplicates_df = pd.read_sql_query(query, conn)

        for _, row in duplicates_df.iterrows():
            issues.append({
                'type': 'Duplicate Record',
                'table': 'patients',
                'patient_id': row['patient_id'],
                'count': row['duplicate_count'],
                'severity': 'Critical',
                'description': f"Patient {row['patient_id']} has {row['duplicate_count']} duplicates"
            })

        return issues

    def check_date_anomalies(self, conn) -> List[Dict]:
        """Check for date-related anomalies"""
        issues = []

        query = """
        SELECT ae.patient_id, ae.event_term, ae.event_date, p.enrollment_date
        FROM adverse_events ae
        JOIN patients p ON ae.patient_id = p.patient_id
        WHERE ae.event_date < p.enrollment_date
        """

        anomalies_df = pd.read_sql_query(query, conn)

        for _, row in anomalies_df.iterrows():
            issues.append({
                'type': 'Date Anomaly',
                'patient_id': row['patient_id'],
                'event_term': row['event_term'],
                'event_date': row['event_date'],
                'enrollment_date': row['enrollment_date'],
                'severity': 'High',
                'description': f"Event '{row['event_term']}' date before enrollment for patient {row['patient_id']}"
            })

        return issues

    def check_unresolved_events(self, conn) -> List[Dict]:
        """Check for long-standing unresolved adverse events"""
        issues = []

        query = """
        SELECT patient_id, event_id, event_term, event_date, severity,
               CAST((julianday('now') - julianday(event_date)) AS INTEGER) as days_open
        FROM adverse_events
        WHERE resolved = 'No' OR resolved IS NULL
        """

        unresolved_df = pd.read_sql_query(query, conn)

        for _, row in unresolved_df.iterrows():
            days_open = row['days_open']

            if days_open > 90:
                severity = 'High'
            elif days_open > 30:
                severity = 'Medium'
            else:
                severity = 'Low'

            issues.append({
                'type': 'Unresolved Event',
                'patient_id': row['patient_id'],
                'event_id': row['event_id'],
                'event_term': row['event_term'],
                'event_date': row['event_date'],
                'event_severity': row['severity'] or 'Unknown',
                'days_open': days_open,
                'severity': severity,
                'description': f"Event '{row['event_term']}' for patient {row['patient_id']} unresolved for {days_open} days"
            })

        return issues

    def export_issues_to_excel(self, results: Dict, output_path: str):
        """Export all issues to Excel file"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                for check_type, issues in results.items():
                    if isinstance(issues, list):
                        summary_data.append({
                            'Check Type': check_type.replace('_', ' ').title(),
                            'Total Issues': len(issues),
                            'Critical': sum(1 for i in issues if i.get('severity') == 'Critical'),
                            'High': sum(1 for i in issues if i.get('severity') == 'High'),
                            'Medium': sum(1 for i in issues if i.get('severity') == 'Medium'),
                            'Low': sum(1 for i in issues if i.get('severity') == 'Low')
                        })

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Individual sheets
                for check_type, issues in results.items():
                    if isinstance(issues, list) and len(issues) > 0:
                        df = pd.DataFrame(issues)
                        sheet_name = check_type.replace('_', ' ').title()[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            return True, f"Report exported to {output_path}"
        except Exception as e:
            return False, f"Error: {str(e)}"

print("✅ Data Quality Checker module created!")
