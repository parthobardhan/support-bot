import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

class MockDataGenerator:
    
    def __init__(self):
        self.adobe_products = [
            "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe Premiere Pro",
            "Adobe After Effects", "Adobe Lightroom", "Adobe XD", "Adobe Acrobat",
            "Adobe Creative Cloud", "Adobe Experience Manager", "Adobe Analytics",
            "Adobe Target", "Adobe Campaign", "Adobe Audience Manager"
        ]
        
        self.jira_priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
        self.jira_statuses = ["Open", "In Progress", "Resolved", "Closed", "Reopened"]
        
        self.documentation_categories = [
            "API Reference", "User Guide", "Installation Guide", "Troubleshooting",
            "Best Practices", "Release Notes", "Migration Guide", "Security Guide"
        ]
        
        self.knowledge_categories = [
            "How-to", "FAQ", "Troubleshooting", "Best Practices", "Known Issues",
            "Feature Overview", "Integration Guide", "Performance Tips"
        ]
    
    def generate_jira_tickets(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock Jira tickets"""
        tickets = []
        
        for i in range(count):
            product = random.choice(self.adobe_products)
            priority = random.choice(self.jira_priorities)
            status = random.choice(self.jira_statuses)
            
            # Generate realistic issue types and summaries
            issue_types = ["Bug", "Feature Request", "Task", "Story", "Epic"]
            issue_type = random.choice(issue_types)
            
            ticket = {
                "_id": f"JIRA-{i+1:05d}",
                "type": "jira",
                "issue_type": issue_type,
                "title": self._generate_jira_title(product, issue_type),
                "summary": self._generate_jira_summary(product, issue_type),
                "content": self._generate_jira_description(product, issue_type, priority),
                "priority": priority,
                "status": status,
                "product": product,
                "assignee": self._generate_random_name(),
                "reporter": self._generate_random_name(),
                "created_date": self._random_date(),
                "updated_date": self._random_date(),
                "labels": self._generate_labels(),
                "tags": [product.lower().replace(" ", "_"), issue_type.lower(), priority.lower()],
                "resolution_time_hours": random.randint(1, 168) if status in ["Resolved", "Closed"] else None,
                "customer_impact": random.choice(["Critical", "High", "Medium", "Low"]),
                "environment": random.choice(["Production", "Staging", "Development"]),
                "chunk_id": f"jira_chunk_{i+1}"
            }
            
            tickets.append(ticket)
        
        return tickets
    
    def generate_documentation(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock documentation articles"""
        docs = []
        
        for i in range(count):
            product = random.choice(self.adobe_products)
            category = random.choice(self.documentation_categories)
            
            doc = {
                "_id": f"DOC-{i+1:05d}",
                "type": "documentation",
                "category": category,
                "title": self._generate_doc_title(product, category),
                "summary": self._generate_doc_summary(product, category),
                "content": self._generate_doc_content(product, category),
                "product": product,
                "version": f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "author": self._generate_random_name(),
                "created_date": self._random_date(),
                "updated_date": self._random_date(),
                "tags": [product.lower().replace(" ", "_"), category.lower().replace(" ", "_")],
                "difficulty_level": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "estimated_read_time": f"{random.randint(5, 60)} minutes",
                "url": f"https://helpx.adobe.com/{product.lower().replace(' ', '-')}/{random.randint(1000, 9999)}",
                "chunk_id": f"doc_chunk_{i+1}"
            }
            
            docs.append(doc)
        
        return docs
    
    def generate_knowledge_articles(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock knowledge base articles"""
        articles = []
        
        for i in range(count):
            product = random.choice(self.adobe_products)
            category = random.choice(self.knowledge_categories)
            
            article = {
                "_id": f"KB-{i+1:05d}",
                "type": "knowledge",
                "category": category,
                "title": self._generate_kb_title(product, category),
                "summary": self._generate_kb_summary(product, category),
                "content": self._generate_kb_content(product, category),
                "product": product,
                "author": self._generate_random_name(),
                "created_date": self._random_date(),
                "updated_date": self._random_date(),
                "tags": [product.lower().replace(" ", "_"), category.lower().replace(" ", "_")],
                "helpful_votes": random.randint(0, 500),
                "view_count": random.randint(100, 10000),
                "difficulty_level": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "solution_verified": random.choice([True, False]),
                "related_articles": [f"KB-{random.randint(1, count):05d}" for _ in range(random.randint(1, 3))],
                "chunk_id": f"kb_chunk_{i+1}"
            }
            
            articles.append(article)
        
        return articles
    
    def _generate_jira_title(self, product: str, issue_type: str) -> str:
        """Generate realistic Jira ticket titles"""
        bug_titles = [
            f"{product} crashes when opening large files",
            f"Memory leak in {product} after extended use",
            f"Performance degradation in {product} on macOS",
            f"{product} not responding to keyboard shortcuts",
            f"Export functionality broken in {product}",
            f"UI elements overlapping in {product}",
            f"Font rendering issues in {product}"
        ]
        
        feature_titles = [
            f"Add batch processing to {product}",
            f"Implement dark mode for {product}",
            f"Enhanced export options for {product}",
            f"Cloud integration for {product}",
            f"AI-powered features for {product}",
            f"Mobile companion app for {product}",
            f"Advanced collaboration tools for {product}"
        ]
        
        if issue_type == "Bug":
            return random.choice(bug_titles)
        elif issue_type == "Feature Request":
            return random.choice(feature_titles)
        else:
            return f"{issue_type}: {product} enhancement request"
    
    def _generate_jira_summary(self, product: str, issue_type: str) -> str:
        """Generate Jira ticket summaries"""
        return f"Issue reported for {product} - {issue_type.lower()} requiring immediate attention from the development team."
    
    def _generate_jira_description(self, product: str, issue_type: str, priority: str) -> str:
        """Generate detailed Jira descriptions"""
        return f"""
        Product: {product}
        Issue Type: {issue_type}
        Priority: {priority}
        
        Description:
        This {issue_type.lower()} has been reported by multiple users and requires immediate attention.
        The issue affects the core functionality of {product} and impacts user productivity.
        
        Steps to Reproduce:
        1. Open {product}
        2. Perform the specific action that triggers the issue
        3. Observe the unexpected behavior
        
        Expected Behavior:
        The application should function normally without any interruptions.
        
        Actual Behavior:
        The application exhibits unexpected behavior that disrupts the user workflow.
        
        Environment:
        - Operating System: Windows 10/11, macOS Monterey/Ventura
        - Product Version: Latest
        - Browser: Chrome/Safari (if applicable)
        
        Additional Notes:
        This issue has been verified across multiple environments and user accounts.
        """
    
    def _generate_doc_title(self, product: str, category: str) -> str:
        """Generate documentation titles"""
        titles = {
            "API Reference": f"{product} API Reference Guide",
            "User Guide": f"Getting Started with {product}",
            "Installation Guide": f"How to Install and Configure {product}",
            "Troubleshooting": f"Common Issues and Solutions for {product}",
            "Best Practices": f"{product} Best Practices and Tips",
            "Release Notes": f"{product} Latest Release Notes",
            "Migration Guide": f"Migrating to the Latest Version of {product}",
            "Security Guide": f"Security Guidelines for {product}"
        }
        return titles.get(category, f"{product} {category} Documentation")
    
    def _generate_doc_summary(self, product: str, category: str) -> str:
        """Generate documentation summaries"""
        return f"Comprehensive {category.lower()} for {product} covering all essential features and functionality."
    
    def _generate_doc_content(self, product: str, category: str) -> str:
        """Generate detailed documentation content"""
        return f"""
        {category} for {product}
        
        Overview:
        This document provides comprehensive information about {product} {category.lower()}.
        
        Key Features:
        - Advanced functionality for professional users
        - Intuitive user interface design
        - Cross-platform compatibility
        - Cloud integration capabilities
        - Collaborative workflow tools
        
        Getting Started:
        1. Download and install {product} from the official Adobe website
        2. Launch the application and complete the initial setup
        3. Explore the main interface and familiarize yourself with key tools
        4. Begin creating your first project
        
        Advanced Features:
        {product} offers numerous advanced features designed for professional workflows:
        - Professional-grade tools and filters
        - Extensive file format support
        - Integration with other Adobe Creative Cloud applications
        - Advanced color management
        - Automation and scripting capabilities
        
        Tips and Best Practices:
        - Regularly save your work to prevent data loss
        - Use keyboard shortcuts to improve efficiency
        - Organize your assets using proper naming conventions
        - Take advantage of cloud synchronization features
        
        Troubleshooting:
        If you encounter issues with {product}, try these common solutions:
        - Restart the application
        - Clear the application cache
        - Update to the latest version
        - Check system requirements
        - Contact Adobe Support if issues persist
        
        Additional Resources:
        - Online tutorials and learning materials
        - Community forums and user groups
        - Official Adobe support documentation
        - Video tutorials and webinars
        """
    
    def _generate_kb_title(self, product: str, category: str) -> str:
        """Generate knowledge base article titles"""
        titles = {
            "How-to": f"How to Use Advanced Features in {product}",
            "FAQ": f"Frequently Asked Questions about {product}",
            "Troubleshooting": f"Troubleshooting Common {product} Issues",
            "Best Practices": f"Best Practices for {product} Workflows",
            "Known Issues": f"Known Issues and Workarounds for {product}",
            "Feature Overview": f"Complete Feature Overview of {product}",
            "Integration Guide": f"Integrating {product} with Other Applications",
            "Performance Tips": f"Performance Optimization Tips for {product}"
        }
        return titles.get(category, f"{product} {category}")
    
    def _generate_kb_summary(self, product: str, category: str) -> str:
        """Generate knowledge base summaries"""
        return f"Expert guidance and solutions for {product} users, focusing on {category.lower()} and practical applications."
    
    def _generate_kb_content(self, product: str, category: str) -> str:
        """Generate knowledge base content"""
        return f"""
        {category} Guide for {product}
        
        Introduction:
        This knowledge base article provides expert guidance for {product} users.
        
        Common Questions and Solutions:
        
        Q: How do I optimize performance in {product}?
        A: To optimize performance, consider the following recommendations:
        - Close unnecessary applications
        - Increase RAM allocation in preferences
        - Use proxy files for large media
        - Clear cache regularly
        - Update graphics drivers
        
        Q: What are the system requirements for {product}?
        A: {product} requires:
        - Operating System: Windows 10 (64-bit) or macOS 10.15 or later
        - RAM: 16 GB minimum, 32 GB recommended
        - Graphics: GPU with DirectX 12 support
        - Storage: 4 GB of available disk space
        - Internet: Required for activation and updates
        
        Q: How do I resolve compatibility issues?
        A: Common compatibility solutions include:
        - Updating to the latest version
        - Checking plugin compatibility
        - Verifying system requirements
        - Running compatibility troubleshooter
        - Contacting technical support
        
        Advanced Tips:
        - Customize workspace layouts for efficiency
        - Use templates to speed up project creation
        - Master keyboard shortcuts for common tasks
        - Set up proper color management profiles
        - Utilize cloud storage for project backup
        
        Related Topics:
        - Performance optimization
        - Workflow enhancement
        - Integration with other Adobe products
        - Troubleshooting common errors
        - Best practices for project management
        
        Last Updated: {datetime.now().strftime('%Y-%m-%d')}
        """
    
    def _generate_random_name(self) -> str:
        """Generate random names for assignees/authors"""
        first_names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Avery", "Quinn"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _random_date(self) -> datetime:
        """Generate random dates within the last 2 years"""
        start_date = datetime.now() - timedelta(days=730)
        end_date = datetime.now()
        random_days = random.randint(0, (end_date - start_date).days)
        return start_date + timedelta(days=random_days)
    
    def _generate_labels(self) -> List[str]:
        """Generate random labels for tickets"""
        labels = ["urgent", "customer-facing", "enhancement", "bug", "security", "performance", "ui", "api"]
        return random.sample(labels, random.randint(1, 3))
    
    def generate_all_data(self, total_count: int = 1000) -> List[Dict[str, Any]]:
        """Generate all types of mock data"""
        jira_count = total_count // 3
        doc_count = total_count // 3
        kb_count = total_count - jira_count - doc_count
        
        all_data = []
        all_data.extend(self.generate_jira_tickets(jira_count))
        all_data.extend(self.generate_documentation(doc_count))
        all_data.extend(self.generate_knowledge_articles(kb_count))
        
        return all_data
