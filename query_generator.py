from typing import Dict, List
from datetime import datetime, timedelta

class QueryTemplateGenerator:
    """Generate standardized query templates"""

    def __init__(self):
        self.templates = {
            'missing_severity': {
                'title': 'Missing AE Severity',
                'priority': 'High',
                'template': """
DATA CLARIFICATION REQUEST

To: Site {site_id} Study Team
Date: {current_date}
Query ID: DCR-{query_id}
Priority: HIGH

ISSUE:
The following adverse event is missing severity:

  Patient ID: {patient_id}
  Event ID: {event_id}
  Event Term: {event_term}
  Event Date: {event_date}

ACTION REQUIRED:
Please provide severity classification (Mild/Moderate/Severe)

RESPONSE DUE: Within 48 hours
"""
            },
            'lab_outlier': {
                'title': 'Lab Value Out of Range',
                'priority': 'High',
                'template': """
DATA CLARIFICATION REQUEST

To: Site {site_id} Study Team
Date: {current_date}
Query ID: DCR-{query_id}
Priority: HIGH

ISSUE:
Out-of-range lab value identified:

  Patient ID: {patient_id}
  Test Name: {test_name}
  Test Value: {test_value} {unit}
  Normal Range: {normal_range_low} - {normal_range_high} {unit}
  Test Date: {test_date}
  Deviation: {outlier_type}

ACTION REQUIRED:
Please verify and provide clinical assessment

RESPONSE DUE: Within 72 hours
"""
            },
            'protocol_deviation': {
                'title': 'Visit Protocol Deviation',
                'priority': 'Medium',
                'template': """
DATA CLARIFICATION REQUEST

To: Site {site_id} Study Team
Date: {current_date}
Query ID: DCR-{query_id}
Priority: MEDIUM

ISSUE:
Protocol deviation identified:

  Patient ID: {patient_id}
  Visit: {visit_type}
  Scheduled: {scheduled_date}
  Actual: {visit_date}
  Days Late: {days_late}

ACTION REQUIRED:
Please provide reason for deviation

RESPONSE DUE: Within 5 business days
"""
            }
        }

    def generate_query(self, issue_type: str, data: Dict, query_id: str = None) -> Dict:
        """Generate query"""
        if query_id is None:
            query_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

        data['current_date'] = datetime.now().strftime('%Y-%m-%d')
        data['query_id'] = query_id

        if 'site_id' not in data:
            data['site_id'] = 'SITEXXXX'

        template_mapping = {
            'Missing Data': 'missing_severity',
            'Lab Outlier': 'lab_outlier',
            'Protocol Deviation': 'protocol_deviation',
        }

        template_key = template_mapping.get(issue_type)

        if template_key and template_key in self.templates:
            template_info = self.templates[template_key]

            try:
                query_text = template_info['template'].format(**data)

                return {
                    'query_id': query_id,
                    'patient_id': data.get('patient_id', 'N/A'),
                    'issue_type': issue_type,
                    'title': template_info['title'],
                    'priority': template_info['priority'],
                    'query_text': query_text,
                    'status': 'Open',
                    'created_date': data['current_date'],
                    'due_date': self._calculate_due_date(template_info['priority'])
                }
            except KeyError as e:
                return {'error': f"Missing field: {e}"}

        return {'error': f"No template for: {issue_type}"}

    def _calculate_due_date(self, priority: str) -> str:
        days_map = {'High': 2, 'Medium': 5, 'Low': 10}
        days = days_map.get(priority, 5)
        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime('%Y-%m-%d')

    def generate_batch_queries(self, issues: List[Dict]) -> List[Dict]:
        queries = []
        for i, issue in enumerate(issues, 1):
            query_id = f"{datetime.now().strftime('%Y%m%d')}-{i:04d}"
            query = self.generate_query(issue['type'], issue, query_id)
            if 'error' not in query:
                queries.append(query)
        return queries

    def export_queries_to_text(self, queries: List[Dict], output_dir: str):
        import os
        os.makedirs(output_dir, exist_ok=True)

        for query in queries:
            if 'error' not in query:
                filename = f"{query['query_id']}_{query['patient_id']}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(query['query_text'])

        return len(queries)

print("✅ Query Template Generator created!")
