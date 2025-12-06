from jira import JIRA
from typing import List, Dict, Any
import os
from .base_loader import BaseLoader

class JiraLoader(BaseLoader):
    """Load Jira tickets"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.jira_config = config.get('jira', {})
        self.max_issues = self.jira_config.get('max_issues', 100)
    
    def load(self) -> List[Dict[str, Any]]:
        if not self.is_enabled():
            return []
        
        jira_email = os.getenv('JIRA_EMAIL')
        jira_token = os.getenv('JIRA_API_TOKEN')
        jira_server = self.jira_config.get('server')
        
        if not jira_email or not jira_token or not jira_server:
            print("⚠️  Jira credentials not found in .env file")
            return []
        
        try:
            # Connect to Jira
            jira = JIRA(
                server=jira_server,
                basic_auth=(jira_email, jira_token)
            )
            
            # Fetch issues
            jql = self.jira_config.get('jql', 'ORDER BY updated DESC')
            issues = jira.search_issues(jql, maxResults=self.max_issues)
            
            documents = []
            
            for issue in issues:
                # Get issue details
                issue_obj = jira.issue(issue.key, expand='changelog')
                
                # Build content
                content_parts = [
                    f"Key: {issue.key}",
                    f"Summary: {issue.fields.summary}",
                    f"Description: {issue.fields.description or 'No description'}",
                    f"Status: {issue.fields.status.name}",
                    f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}",
                ]
                
                # Add comments
                if hasattr(issue.fields, 'comment') and issue.fields.comment.comments:
                    content_parts.append("\nComments:")
                    for comment in issue.fields.comment.comments:
                        content_parts.append(f"- {comment.author.displayName}: {comment.body}")
                
                content = "\n".join(content_parts)
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'source': 'jira',
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'status': issue.fields.status.name,
                        'created': str(issue.fields.created),
                        'updated': str(issue.fields.updated)
                    }
                })
            
            print(f"✅ Loaded {len(documents)} Jira tickets")
            return documents
            
        except Exception as e:
            print(f"❌ Error loading Jira tickets: {str(e)}")
            return []

