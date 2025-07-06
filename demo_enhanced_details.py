#!/usr/bin/env python3
"""
Demo script showing the enhanced opportunity detail dialog
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from src.gui.gui import OpportunityDetailDialog


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Opportunity Detail Dialog Demo")
        self.setGeometry(100, 100, 400, 200)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Demo opportunity data with comprehensive fields
        self.demo_opportunities = [
            {
                'id': 1,
                'name': 'NASA Space Technology Development Program',
                'org_name': 'NASA',
                'deadline': '2024-12-31',
                'status': 'Open',
                'description': 'Comprehensive space technology development program focused on advancing satellite technologies, space exploration capabilities, and next-generation propulsion systems. This program seeks to develop innovative solutions for deep space missions and lunar exploration.',
                'url': 'https://nasa.gov/solicitations/space-tech-2024',
                'requirements': 'PhD in Aerospace Engineering, Mechanical Engineering, or related field. Minimum 5 years of experience in space systems development. Security clearance may be required.',
                'category': 'Space Technology',
                'keywords': 'space, satellite, technology, aerospace, engineering, propulsion, lunar, mars',
                'relevance_score': 0.85,
                'estimated_funding': '$2.5 million over 3 years',
                'source_url': 'https://grants.gov/nasa-space-tech',
                'created_at': '2024-01-15 10:30:00'
            },
            {
                'id': 2,
                'name': 'NSF AI Research Initiative',
                'org_name': 'National Science Foundation',
                'deadline': '2024-11-15',
                'status': 'Open',
                'description': 'Multi-disciplinary research program to advance artificial intelligence and machine learning applications in scientific research. Focus on developing AI tools for data analysis, pattern recognition, and predictive modeling.',
                'url': 'https://nsf.gov/ai-research-2024',
                'requirements': 'PhD in Computer Science, Data Science, or related field. Demonstrated experience in AI/ML research and publications in peer-reviewed journals.',
                'category': 'Artificial Intelligence',
                'keywords': 'artificial intelligence, machine learning, data science, research, algorithms',
                'relevance_score': 0.75,
                'estimated_funding': '$1.8 million over 2 years',
                'source_url': 'https://nsf.gov/funding/ai-initiative',
                'created_at': '2024-01-20 14:45:00'
            },
            {
                'id': 3,
                'name': 'DOE Clean Energy Innovation Challenge',
                'org_name': 'Department of Energy',
                'deadline': '2024-10-30',
                'status': 'Open',
                'description': 'Innovation challenge focused on developing breakthrough clean energy technologies, including advanced solar systems, energy storage solutions, and grid modernization technologies.',
                'url': 'https://energy.gov/clean-energy-challenge',
                'requirements': 'Advanced degree in Engineering, Physics, or related field. Industry or academic experience in renewable energy systems.',
                'category': 'Clean Energy',
                'keywords': 'clean energy, solar, battery, grid, renewable energy, sustainability',
                'relevance_score': 0.68,
                'estimated_funding': '$3.2 million over 4 years',
                'source_url': 'https://energy.gov/funding/innovation-challenge',
                'created_at': '2024-01-25 09:15:00'
            }
        ]
        
        # Buttons to show different opportunities
        for i, opp in enumerate(self.demo_opportunities):
            btn = QPushButton(f"Show Details: {opp['name']}")
            btn.clicked.connect(lambda checked, opp=opp: self.show_opportunity(opp))
            layout.addWidget(btn)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def show_opportunity(self, opportunity_data):
        """Show the enhanced opportunity detail dialog"""
        detail_dialog = OpportunityDetailDialog(opportunity_data)
        detail_dialog.show()
        
        # Keep reference to prevent garbage collection
        self.current_dialog = detail_dialog

def main():
    app = QApplication(sys.argv)
    
    print("🚀 Starting Enhanced Opportunity Detail Dialog Demo")
    print("=" * 60)
    print("Features included in the enhanced dialog:")
    print("📋 Multi-tab interface (Overview, Details, Analysis, Actions)")
    print("🎯 Quick action buttons (Bookmark, Mark as Applied, Export)")
    print("📊 Relevance scoring and match analysis")
    print("📝 Personal notes and application tracking")
    print("💾 Export functionality")
    print("🔗 Clickable links and formatted display")
    print("=" * 60)
    
    demo_window = DemoWindow()
    demo_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
