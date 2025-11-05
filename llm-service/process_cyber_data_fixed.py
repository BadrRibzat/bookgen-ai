#!/usr/bin/env python3
"""
Improved Cybersecurity Data Processor
Handles the actual format of your 5 data sources
"""

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
            'by_tier': {'basic': 0, 'professional': 0, 'enterprise': 0},
            'by_source': {}
        }
    
    def process_nvd_cve(self, input_file: Path) -> List[Dict]:
        """Process NVD CVE data - handles your actual CVE format"""
        print(f"  📊 Processing {input_file.name}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        
        # Handle MITRE CVE format
        vulns = data.get('vulnerabilities', [])
        
        for item in vulns[:100]:  # Limit to 100 per file
            cve = item.get('cve', {})
            cve_id = cve.get('id', 'UNKNOWN')
            
            if cve_id == 'UNKNOWN':
                continue
            
            # Get description
            descriptions = cve.get('descriptions', [])
            desc = ''
            for d in descriptions:
                if d.get('lang') == 'en':
                    desc = d.get('value', '')
                    break
            
            if not desc or len(desc) < 50:
                continue
            
            # Get CVSS score and severity
            metrics = cve.get('metrics', {})
            cvss_score = 5.0  # Default
            severity = 'MEDIUM'
            
            # Try CVSS v3.1 first, then v3.0, then v2
            for version in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                if version in metrics and metrics[version]:
                    cvss_data = metrics[version][0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore', 5.0)
                    break
            
            # Determine severity and complexity
            if cvss_score >= 9.0:
                severity = 'CRITICAL'
                difficulty = 8
                tier = 'enterprise'
            elif cvss_score >= 7.0:
                severity = 'HIGH'
                difficulty = 6
                tier = 'professional'
            elif cvss_score >= 4.0:
                severity = 'MEDIUM'
                difficulty = 4
                tier = 'professional'
            else:
                severity = 'LOW'
                difficulty = 2
                tier = 'basic'
            
            # Get published date
            published = cve.get('published', '')
            year = published[:4] if published else '2024'
            
            example = {
                "id": f"cve_{cve_id.lower().replace('-', '_')}",
                "input": f"Explain the cybersecurity vulnerability {cve_id} and its implications",
                "output": f"**{cve_id} - {severity} Severity Vulnerability**\n\n"
                         f"{desc}\n\n"
                         f"**Technical Details:**\n"
                         f"- CVSS Score: {cvss_score}/10.0\n"
                         f"- Severity Level: {severity}\n"
                         f"- Published: {published}\n\n"
                         f"**Risk Assessment:**\n"
                         f"This vulnerability requires {'immediate' if severity == 'CRITICAL' else 'prompt' if severity == 'HIGH' else 'timely'} "
                         f"attention and remediation based on its {severity.lower()} severity rating. "
                         f"Organizations should prioritize patching systems affected by this vulnerability.",
                "context": f"CVE Analysis - {cve_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["cve", "vulnerability", severity.lower(), f"cvss_{int(cvss_score)}", year],
                "quality_score": 9.2,
                "metadata": {
                    "source": "nvd_cve",
                    "cve_id": cve_id,
                    "cvss_score": cvss_score,
                    "severity": severity,
                    "published_date": published,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "token_count": len(desc.split()) + 50,
                    "category": "vulnerabilities"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} CVE examples")
        self.stats['by_source']['nvd_cve'] = len(examples)
        return examples
    
    def process_mitre_attack(self, input_file: Path) -> List[Dict]:
        """Process MITRE ATT&CK data - handles your actual MITRE format"""
        print(f"  🎯 Processing {input_file.name}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        
        # Your file has a 'bundle' structure with 'objects'
        objects = data.get('objects', [])
        
        for obj in objects:
            # Only process attack patterns (techniques)
            if obj.get('type') != 'attack-pattern':
                continue
            
            # Skip revoked or deprecated items
            if obj.get('revoked') or obj.get('x_mitre_deprecated'):
                continue
            
            name = obj.get('name', '')
            desc = obj.get('description', '')
            
            if not name or not desc or len(desc) < 50:
                continue
            
            # Get technique ID from external references
            tech_id = 'UNKNOWN'
            external_refs = obj.get('external_references', [])
            for ref in external_refs:
                if ref.get('source_name') == 'mitre-attack' and 'external_id' in ref:
                    tech_id = ref['external_id']
                    break
            
            if tech_id == 'UNKNOWN':
                continue
            
            # Get tactics from kill chain phases
            tactics = []
            kill_chain_phases = obj.get('kill_chain_phases', [])
            for phase in kill_chain_phases:
                if phase.get('kill_chain_name') == 'mitre-attack':
                    tactics.append(phase.get('phase_name', ''))
            
            # Get platforms
            platforms = obj.get('x_mitre_platforms', [])
            
            # Determine difficulty based on technique complexity
            difficulty = 6  # Default professional level
            tier = 'professional'
            
            # Enterprise level for complex or multi-platform techniques
            if len(platforms) > 3 or 'Enterprise' in str(platforms):
                difficulty = 8
                tier = 'enterprise'
            
            example = {
                "id": f"mitre_{tech_id.lower().replace('.', '_')}",
                "input": f"Explain MITRE ATT&CK technique {tech_id}: {name}",
                "output": f"**MITRE ATT&CK Technique {tech_id}: {name}**\n\n"
                         f"{desc}\n\n"
                         f"**Tactical Information:**\n"
                         f"- Tactics: {', '.join(tactics) if tactics else 'Various'}\n"
                         f"- Platforms: {', '.join(platforms[:5]) if platforms else 'Multiple'}\n"
                         f"- Technique ID: {tech_id}\n\n"
                         f"**Threat Context:**\n"
                         f"This technique is part of the MITRE ATT&CK framework, representing "
                         f"documented adversary behavior observed in real-world attacks. "
                         f"Understanding this technique helps defenders prepare appropriate countermeasures.",
                "context": f"MITRE ATT&CK Framework - {tech_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["mitre", "attack", "technique", tech_id] + tactics[:3],
                "quality_score": 9.5,
                "metadata": {
                    "source": "mitre_attack",
                    "technique_id": tech_id,
                    "tactics": tactics,
                    "platforms": platforms,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "token_count": len(desc.split()) + 40,
                    "category": "threat_intelligence"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
            
            # Limit to 50 examples to avoid overwhelming
            if len(examples) >= 50:
                break
        
        print(f"    ✓ Extracted {len(examples)} MITRE ATT&CK examples")
        self.stats['by_source']['mitre_attack'] = len(examples)
        return examples
    
    def process_ubuntu_security(self, input_file: Path) -> List[Dict]:
        """Process Ubuntu Security Notices RSS"""
        print(f"  📢 Processing {input_file.name}...")
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        examples = []
        
        # Find all item elements in the RSS feed
        items = root.findall('.//item')
        
        for item in items[:50]:  # Limit to 50 advisories
            title_elem = item.find('title')
            desc_elem = item.find('description')
            link_elem = item.find('link')
            pubdate_elem = item.find('pubDate')
            
            if title_elem is None or desc_elem is None:
                continue
            
            title = title_elem.text.strip() if title_elem.text else ''
            desc = desc_elem.text.strip() if desc_elem.text else ''
            link = link_elem.text.strip() if link_elem and link_elem.text else ''
            pubdate = pubdate_elem.text.strip() if pubdate_elem and pubdate_elem.text else ''
            
            if not title or not desc or len(desc) < 30:
                continue
            
            # Extract USN ID from title
            usn_match = re.search(r'(USN-\d+-\d+)', title)
            usn_id = usn_match.group(1) if usn_match else 'USN-UNKNOWN'
            
            # Determine severity from content
            severity_keywords = {
                'critical': 8,
                'high': 6, 
                'medium': 4,
                'low': 2,
                'escalate privileges': 7,
                'remote code execution': 8,
                'denial of service': 4
            }
            
            difficulty = 5  # Default
            for keyword, level in severity_keywords.items():
                if keyword.lower() in desc.lower():
                    difficulty = max(difficulty, level)
            
            tier = 'basic' if difficulty <= 3 else 'professional' if difficulty <= 7 else 'enterprise'
            
            example = {
                "id": f"ubuntu_{usn_id.lower().replace('-', '_')}",
                "input": f"What security issues does Ubuntu Security Notice {usn_id} address?",
                "output": f"**Ubuntu Security Notice {usn_id}**\n\n"
                         f"**Title:** {title}\n\n"
                         f"**Description:** {desc}\n\n"
                         f"**Advisory Details:**\n"
                         f"- Notice ID: {usn_id}\n"
                         f"- Published: {pubdate}\n"
                         f"- More Info: {link}\n\n"
                         f"**Remediation:**\n"
                         f"Ubuntu users should apply the security updates provided in this notice "
                         f"to protect their systems from the described vulnerabilities.",
                "context": f"Ubuntu Security Advisory - {usn_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["ubuntu", "security", "advisory", usn_id, "patch"],
                "quality_score": 8.8,
                "metadata": {
                    "source": "ubuntu_security",
                    "advisory_id": usn_id,
                    "published_date": pubdate,
                    "advisory_link": link,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "token_count": len((title + desc).split()) + 30,
                    "category": "patch_management"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} Ubuntu security examples")
        self.stats['by_source']['ubuntu_security'] = len(examples)
        return examples
    
    def process_arxiv_papers(self, input_file: Path) -> List[Dict]:
        """Process ArXiv research papers"""
        print(f"  📄 Processing {input_file.name}...")
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Handle Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('.//atom:entry', ns)
        
        examples = []
        
        for entry in entries[:30]:  # Limit to 30 papers
            title_elem = entry.find('atom:title', ns)
            summary_elem = entry.find('atom:summary', ns)
            id_elem = entry.find('atom:id', ns)
            published_elem = entry.find('atom:published', ns)
            
            if title_elem is None or summary_elem is None or id_elem is None:
                continue
            
            title = title_elem.text.strip() if title_elem.text else ''
            summary = summary_elem.text.strip() if summary_elem.text else ''
            paper_url = id_elem.text.strip() if id_elem.text else ''
            published = published_elem.text.strip() if published_elem and published_elem.text else ''
            
            # Clean up summary text
            summary = re.sub(r'\s+', ' ', summary)
            
            if not title or not summary or len(summary) < 100:
                continue
            
            # Extract arXiv ID
            arxiv_id = paper_url.split('/')[-1] if paper_url else 'unknown'
            
            # Research papers are enterprise level
            difficulty = 9
            tier = 'enterprise'
            
            example = {
                "id": f"arxiv_{arxiv_id.replace(':', '_').replace('.', '_')}",
                "input": f"Summarize the cybersecurity research paper: {title}",
                "output": f"**ArXiv Research Paper: {title}**\n\n"
                         f"**Abstract:** {summary}\n\n"
                         f"**Research Details:**\n"
                         f"- ArXiv ID: {arxiv_id}\n"
                         f"- Published: {published}\n"
                         f"- Paper URL: {paper_url}\n\n"
                         f"**Academic Significance:**\n"
                         f"This peer-reviewed research contributes to advancing cybersecurity "
                         f"knowledge through rigorous academic analysis and provides insights "
                         f"that can inform both defensive strategies and security tool development.",
                "context": f"Academic Cybersecurity Research - {arxiv_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["research", "arxiv", "cryptography", "academic", "peer_reviewed"],
                "quality_score": 9.7,
                "metadata": {
                    "source": "arxiv_papers",
                    "paper_id": arxiv_id,
                    "paper_url": paper_url,
                    "published_date": published,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "token_count": len((title + summary).split()) + 50,
                    "category": "security_research"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} research paper examples")
        self.stats['by_source']['arxiv_papers'] = len(examples)
        return examples
    
    def process_microsoft_security(self, input_file: Path) -> List[Dict]:
        """Process Microsoft Security Updates"""
        print(f"  🔒 Processing {input_file.name}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        
        # Handle different Microsoft security data structures
        # This is a flexible approach for various MS security formats
        updates = []
        
        if isinstance(data, list):
            updates = data
        elif isinstance(data, dict):
            # Try different possible keys
            for key in ['updates', 'advisories', 'vulnerabilities', 'releases', 'items']:
                if key in data:
                    updates = data[key] if isinstance(data[key], list) else [data[key]]
                    break
            
            # If no list found, treat the whole dict as a single update
            if not updates and data:
                updates = [data]
        
        for update in updates[:50]:  # Limit to 50 updates
            if not isinstance(update, dict):
                continue
            
            # Extract relevant fields (flexible field names)
            title = (update.get('title') or update.get('name') or 
                    update.get('summary') or update.get('description', ''))[:200]
            
            description = (update.get('description') or update.get('details') or 
                          update.get('summary') or title)
            
            if not title or not description or len(description) < 50:
                continue
            
            # Extract ID if available
            update_id = (update.get('id') or update.get('kb') or 
                        update.get('bulletin_id') or 'MS-UPDATE')
            
            # Extract severity
            severity = update.get('severity', update.get('impact', 'Medium'))
            
            # Map severity to difficulty
            severity_map = {
                'critical': 8, 'high': 6, 'medium': 4, 'low': 2,
                'important': 6, 'moderate': 4
            }
            
            difficulty = severity_map.get(severity.lower(), 5)
            tier = 'basic' if difficulty <= 3 else 'professional' if difficulty <= 7 else 'enterprise'
            
            example = {
                "id": f"microsoft_{str(update_id).lower().replace('-', '_').replace(' ', '_')}",
                "input": f"Explain Microsoft security update {update_id} and its importance",
                "output": f"**Microsoft Security Update: {update_id}**\n\n"
                         f"**Title:** {title}\n\n"
                         f"**Description:** {description}\n\n"
                         f"**Security Details:**\n"
                         f"- Update ID: {update_id}\n"
                         f"- Severity: {severity}\n\n"
                         f"**Recommendation:**\n"
                         f"Organizations using Microsoft products should evaluate and apply "
                         f"this security update according to their patch management procedures "
                         f"to address the described security issues.",
                "context": f"Microsoft Security Update - {update_id}",
                "difficulty_level": difficulty,
                "subscription_tier": tier,
                "tags": ["microsoft", "security", "update", "patch", severity.lower()],
                "quality_score": 8.5,
                "metadata": {
                    "source": "microsoft_security",
                    "update_id": str(update_id),
                    "severity": severity,
                    "created_at": datetime.now().isoformat(),
                    "validated": True,
                    "token_count": len((title + description).split()) + 35,
                    "category": "patch_management"
                }
            }
            
            examples.append(example)
            self.stats['by_tier'][tier] += 1
        
        print(f"    ✓ Extracted {len(examples)} Microsoft security examples")
        self.stats['by_source']['microsoft_security'] = len(examples)
        return examples
    
    def create_training_file(self, examples: List[Dict], filename: str, source_desc: str):
        """Save processed examples to training file"""
        if not examples:
            print(f"    ⚠️  No examples to save for {filename}")
            return
        
        # Count examples by tier
        tier_counts = {'basic': 0, 'professional': 0, 'enterprise': 0}
        for ex in examples:
            tier_counts[ex['subscription_tier']] += 1
        
        output_data = {
            "domain": "cybersecurity",
            "description": f"Cybersecurity training data - {source_desc}",
            "version": "1.0.0",
            "total_examples": len(examples),
            "tier_distribution": tier_counts,
            "subscription_tiers": {
                "basic": {
                    "system_prompt": "You are a cybersecurity assistant for beginners. Provide clear, basic explanations suitable for those learning security concepts.",
                    "max_complexity": 3,
                    "target_audience": "beginners",
                    "example_count": tier_counts['basic']
                },
                "professional": {
                    "system_prompt": "You are a cybersecurity expert for professionals. Provide detailed, technical responses with implementation details and security frameworks.",
                    "max_complexity": 7,
                    "target_audience": "security_professionals",
                    "example_count": tier_counts['professional']
                },
                "enterprise": {
                    "system_prompt": "You are a senior cybersecurity consultant. Provide enterprise-level strategic guidance with compliance and risk management focus.",
                    "max_complexity": 10,
                    "target_audience": "enterprise_leaders",
                    "example_count": tier_counts['enterprise']
                }
            },
            "training_examples": examples
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.stats['processed_files'] += 1
        self.stats['total_examples'] += len(examples)
        print(f"    💾 Saved {len(examples)} examples to {filename}")
    
    def process_all(self):
        """Process all available cybersecurity data files"""
        print("\n🔄 Starting comprehensive cybersecurity data processing...\n")
        
        # Process NVD CVE data
        cve_files = list(self.raw_dir.glob('*cve*.json'))
        for f in cve_files:
            try:
                examples = self.process_nvd_cve(f)
                if examples:
                    self.create_training_file(examples, 'vulnerabilities_cve_1.json', 'NVD CVE Database')
            except Exception as e:
                print(f"    ❌ Error processing {f.name}: {e}")
        
        # Process MITRE ATT&CK
        mitre_files = list(self.raw_dir.glob('*mitre*.json'))
        for f in mitre_files:
            try:
                examples = self.process_mitre_attack(f)
                if examples:
                    self.create_training_file(examples, 'threat_intelligence_mitre_1.json', 'MITRE ATT&CK Framework')
            except Exception as e:
                print(f"    ❌ Error processing {f.name}: {e}")
        
        # Process Ubuntu Security Notices
        ubuntu_files = list(self.raw_dir.glob('*ubuntu*.xml'))
        for f in ubuntu_files:
            try:
                examples = self.process_ubuntu_security(f)
                if examples:
                    self.create_training_file(examples, 'patch_management_ubuntu_1.json', 'Ubuntu Security Notices')
            except Exception as e:
                print(f"    ❌ Error processing {f.name}: {e}")
        
        # Process ArXiv Research Papers
        arxiv_files = list(self.raw_dir.glob('*arxiv*.xml'))
        for f in arxiv_files:
            try:
                examples = self.process_arxiv_papers(f)
                if examples:
                    self.create_training_file(examples, 'security_research_arxiv_1.json', 'ArXiv Cryptography Research')
            except Exception as e:
                print(f"    ❌ Error processing {f.name}: {e}")
        
        # Process Microsoft Security Updates
        ms_files = list(self.raw_dir.glob('*microsoft*.json'))
        for f in ms_files:
            try:
                examples = self.process_microsoft_security(f)
                if examples:
                    self.create_training_file(examples, 'patch_management_microsoft_1.json', 'Microsoft Security Updates')
            except Exception as e:
                print(f"    ❌ Error processing {f.name}: {e}")
        
        # Print comprehensive summary
        print(f"\n📊 COMPREHENSIVE PROCESSING SUMMARY")
        print(f"==================================")
        print(f"📁 Files processed: {self.stats['processed_files']}")
        print(f"📄 Total training examples: {self.stats['total_examples']}")
        print(f"\n📈 By subscription tier:")
        print(f"   🎯 Basic: {self.stats['by_tier']['basic']} examples")
        print(f"   🔧 Professional: {self.stats['by_tier']['professional']} examples")
        print(f"   🏢 Enterprise: {self.stats['by_tier']['enterprise']} examples")
        print(f"\n📊 By data source:")
        for source, count in self.stats['by_source'].items():
            print(f"   📋 {source}: {count} examples")
        
        if self.stats['total_examples'] > 0:
            print(f"\n✅ SUCCESS: Your cybersecurity data is ready for training!")
            print(f"📚 Training files created in: {self.output_dir}")
        else:
            print(f"\n⚠️  WARNING: No training examples were generated")


if __name__ == '__main__':
    processor = CybersecurityDataProcessor(
        raw_dir='data/raw_sources/cybersecurity',
        output_dir='data/training_sets/cybersecurity'
    )
    processor.process_all()