#!/usr/bin/env python3
"""Process cybersecurity raw data into training format"""

import json
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class CybersecurityDataProcessor:
    def __init__(self, raw_dir: str, output_dir: str):
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            'processed_files': 0,
            'total_examples': 0,
            'by_tier': {'basic': 0, 'professional': 0, 'enterprise': 0}
        }
    
    def process_nvd_cve(self, input_file: Path) -> List[Dict]:
        """Process NVD CVE data"""
        print(f"  📊 Processing {input_file.name}...")
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        examples = []
        
        # Handle different NVD formats
        vulns = data.get('vulnerabilities', [])
        if not vulns and 'CVE_Items' in data:
            vulns = data['CVE_Items']
        
        for item in vulns[:100]:  # Limit to 100 per file
            cve = item.get('cve', item)
            cve_id = cve.get('id', cve.get('CVE_data_meta', {}).get('ID', 'UNKNOWN'))
            
            descriptions = cve.get('descriptions', cve.get('description', {}).get('description_data', []))
            desc = next((d.get('value', d.get('value', '')) for d in descriptions if d.get('lang') == 'en'), '')
            
            if not desc or len(desc) < 50:
                continue
            
            # Determine severity
            metrics = cve.get('metrics', {})
            cvss = (metrics.get('cvssMetricV31', [{}])[0].get('cvssData', {}) or
                   metrics.get('cvssMetricV2', [{}])[0].get('cvssData', {}))
            
            score = cvss.get('baseScore', 5.0)
            severity = 'MEDIUM'
            if score >= 9.0: severity = 'CRITICAL'
            elif score >= 7.0: severity = 'HIGH'
            elif score < 4.0: severity = 'LOW'
            
            difficulty = {'LOW': 2, 'MEDIUM': 4, 'HIGH': 6, 'CRITICAL': 8}.get(severity, 4)
            tier = 'basic' if difficulty <= 3 else 'professional' if difficulty <= 6 else 'enterprise'
            
            example = {
                "id": f"cve_{cve_id.lower().replace('-', '_')}",
                "input": f"Explain {cve_id} and its security implications",
                "output": f"{desc}\n\nSeverity: {severity} (CVSS Score: {score})\n\n"
                         f"This vulnerability requires {'immediate' if severity == 'CRITICAL' else 'prompt'} "
                         f"attention and remediation based on its {severity.lower()} severity rating.",
                "context": f"CVE Analysis - {cve_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["cve", "vulnerability", severity.lower(), cve_id.split('-')[0]],
                "quality_score": 9.0,
                "metadata": {
                    "source": "nvd_cve",
                    "cve_id": cve_id,
                    "cvss_score": score,
                    "severity": severity,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "category": "vulnerabilities"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} CVE examples")
        return examples
    
    def process_mitre_attack(self, input_file: Path) -> List[Dict]:
        """Process MITRE ATT&CK data"""
        print(f"  🎯 Processing {input_file.name}...")
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        examples = []
        
        for obj in data.get('objects', [])[:100]:
            if obj.get('type') != 'attack-pattern':
                continue
            
            tech_id = next((ref.get('external_id') for ref in obj.get('external_references', []) 
                          if ref.get('source_name') == 'mitre-attack'), 'UNKNOWN')
            name = obj.get('name', 'Unknown')
            desc = obj.get('description', '')
            
            if len(desc) < 50:
                continue
            
            tactics = [phase['phase_name'] for phase in obj.get('kill_chain_phases', [])]
            
            example = {
                "id": f"mitre_{tech_id.lower().replace('.', '_')}",
                "input": f"Explain MITRE ATT&CK technique {tech_id}: {name}",
                "output": f"{desc}\n\nTactics: {', '.join(tactics)}\n\n"
                         f"This technique is part of the MITRE ATT&CK framework, representing "
                         f"documented adversary behavior used in real-world attacks.",
                "context": f"MITRE ATT&CK - {tech_id}",
                "difficulty_level": 6,
                "subscription_tier": "professional",
                "tags": ["mitre", "technique", tech_id] + tactics,
                "quality_score": 9.5,
                "metadata": {
                    "source": "mitre_attack",
                    "technique_id": tech_id,
                    "tactics": tactics,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "category": "threat_intelligence"
                }
            }
            
            examples.append(example)
            self.stats['by_tier']['professional'] += 1
        
        print(f"    ✓ Extracted {len(examples)} MITRE ATT&CK examples")
        return examples
    
    def process_security_advisory(self, input_file: Path) -> List[Dict]:
        """Process security advisory RSS/XML"""
        print(f"  📢 Processing {input_file.name}...")
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Find items/entries
        items = (root.findall('.//item') or 
                root.findall('.//{http://www.w3.org/2005/Atom}entry'))
        
        examples = []
        
        for item in items[:50]:
            title_elem = (item.find('title') or 
                         item.find('{http://www.w3.org/2005/Atom}title'))
            desc_elem = (item.find('description') or 
                        item.find('{http://www.w3.org/2005/Atom}summary'))
            
            if title_elem is None or desc_elem is None:
                continue
            
            title = title_elem.text or ''
            desc = desc_elem.text or ''
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()
            
            if len(desc) < 50:
                continue
            
            advisory_id = re.search(r'(USN-\d+-\d+|MSFT-\d+|CVE-\d{4}-\d+)', title)
            aid = advisory_id.group(1) if advisory_id else 'ADVISORY'
            
            difficulty = 5
            tier = 'professional'
            
            example = {
                "id": f"advisory_{aid.lower().replace('-', '_')}",
                "input": f"What does security advisory {aid} address?",
                "output": f"{title}\n\n{desc[:400]}...",
                "context": f"Security Advisory - {aid}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["advisory", "patch", "security_update"],
                "quality_score": 9.0,
                "metadata": {
                    "source": "security_advisory",
                    "advisory_id": aid,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "category": "patch_management"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} advisory examples")
        return examples
    
    def process_arxiv_paper(self, input_file: Path) -> List[Dict]:
        """Process ArXiv research papers"""
        print(f"  📄 Processing {input_file.name}...")
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        examples = []
        
        for entry in entries[:30]:
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
            id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
            
            if not all([title_elem, summary_elem, id_elem]):
                continue
            
            title = title_elem.text.strip()
            summary = re.sub(r'\s+', ' ', summary_elem.text.strip())
            paper_id = id_elem.text.split('/')[-1]
            
            if len(summary) < 100:
                continue
            
            example = {
                "id": f"arxiv_{paper_id.replace(':', '_').replace('.', '_')}",
                "input": f"Summarize the cybersecurity research: {title}",
                "output": f"{summary}\n\n"
                         f"This peer-reviewed research contributes to advancing "
                         f"cybersecurity knowledge through rigorous academic analysis.",
                "context": f"Academic Research - {paper_id}",
                "difficulty_level": 9,
                "subscription_tier": "enterprise",
                "tags": ["research", "arxiv", "cryptography", "academic"],
                "quality_score": 9.5,
                "metadata": {
                    "source": "arxiv",
                    "paper_id": paper_id,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "category": "security_research"
                }
            }
            
            examples.append(example)
            self.stats['by_tier']['enterprise'] += 1
        
        print(f"    ✓ Extracted {len(examples)} research paper examples")
        return examples
    
    def create_training_file(self, examples: List[Dict], filename: str):
        """Save processed examples"""
        output_data = {
            "domain": "cybersecurity",
            "description": f"Cybersecurity training data - {filename.replace('.json', '')}",
            "version": "1.0.0",
            "total_examples": len(examples),
            "subscription_tiers": {
                "basic": {
                    "system_prompt": "You are a cybersecurity assistant for beginners.",
                    "max_complexity": 3,
                    "target_audience": "beginners"
                },
                "professional": {
                    "system_prompt": "You are a cybersecurity expert for professionals.",
                    "max_complexity": 7,
                    "target_audience": "security_professionals"
                },
                "enterprise": {
                    "system_prompt": "You are a senior cybersecurity consultant.",
                    "max_complexity": 10,
                    "target_audience": "enterprise_leaders"
                }
            },
            "training_examples": examples
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.stats['processed_files'] += 1
        self.stats['total_examples'] += len(examples)
        print(f"    💾 Saved to {filename}")
    
    def process_all(self):
        """Process all available files"""
        print("\n🔄 Starting data processing...\n")
        
        # Process CVE data
        cve_files = list(self.raw_dir.glob('*cve*.json'))
        for f in cve_files:
            try:
                examples = self.process_nvd_cve(f)
                if examples:
                    self.create_training_file(examples, 'vulnerabilities_cve_1.json')
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Process MITRE ATT&CK
        mitre_files = list(self.raw_dir.glob('*mitre*.json'))
        for f in mitre_files:
            try:
                examples = self.process_mitre_attack(f)
                if examples:
                    self.create_training_file(examples, 'threat_intelligence_mitre_1.json')
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Process security advisories
        advisory_files = list(self.raw_dir.glob('*security*.xml'))
        advisory_files.extend(self.raw_dir.glob('*advisory*.xml'))
        for f in advisory_files:
            try:
                examples = self.process_security_advisory(f)
                if examples:
                    self.create_training_file(examples, 'patch_management_advisories_1.json')
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Process ArXiv papers
        arxiv_files = list(self.raw_dir.glob('*arxiv*.xml'))
        for f in arxiv_files:
            try:
                examples = self.process_arxiv_paper(f)
                if examples:
                    self.create_training_file(examples, 'security_research_arxiv_1.json')
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Print summary
        print(f"\n📊 PROCESSING SUMMARY")
        print(f"==================")
        print(f"Files processed: {self.stats['processed_files']}")
        print(f"Total examples: {self.stats['total_examples']}")
        print(f"By subscription tier:")
        print(f"  Basic: {self.stats['by_tier']['basic']}")
        print(f"  Professional: {self.stats['by_tier']['professional']}")
        print(f"  Enterprise: {self.stats['by_tier']['enterprise']}")


if __name__ == '__main__':
    processor = CybersecurityDataProcessor(
        raw_dir='data/raw_sources/cybersecurity',
        output_dir='data/training_sets/cybersecurity'
    )
    processor.process_all()
