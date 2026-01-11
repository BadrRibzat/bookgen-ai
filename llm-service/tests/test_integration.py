import pytest
import requests
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestLLMIntegration:
    """Integration tests for LLM service"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_content_generation(self, client):
        """Test content generation endpoint"""
        payload = {
            "domain": "cybersecurity",
            "prompt": "Write a security incident response plan for small businesses.",
            "max_tokens": 500
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "domain" in data
        assert len(data["content"].split()) >= 50  # Reasonable content length

    def test_domain_validation(self, client):
        """Test domain validation"""
        valid_domains = ["cybersecurity", "ai_ml", "nutrition", "ecommerce"]
        invalid_domain = "invalid_domain"

        # Test valid domains
        for domain in valid_domains:
            payload = {
                "domain": domain,
                "prompt": "Test prompt",
                "max_tokens": 100
            }
            response = client.post("/generate", json=payload)
            assert response.status_code == 200

        # Test invalid domain
        payload = {
            "domain": invalid_domain,
            "prompt": "Test prompt",
            "max_tokens": 100
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 400

    def test_prompt_quality(self, client):
        """Test prompt quality and response relevance"""
        test_cases = [
            {
                "domain": "cybersecurity",
                "prompt": "Explain encryption basics for beginners.",
                "expected_keywords": ["encryption", "key", "algorithm"]
            },
            {
                "domain": "ai_ml",
                "prompt": "Describe machine learning workflow.",
                "expected_keywords": ["data", "model", "training", "prediction"]
            }
        ]

        for case in test_cases:
            payload = {
                "domain": case["domain"],
                "prompt": case["prompt"],
                "max_tokens": 300
            }
            response = client.post("/generate", json=payload)
            assert response.status_code == 200
            content = response.json()["content"].lower()

            # Check if response contains expected keywords
            has_keywords = any(keyword in content for keyword in case["expected_keywords"])
            assert has_keywords, f"Response missing expected keywords for {case['domain']}"

    def test_generation_limits(self, client):
        """Test token limits and constraints"""
        # Test max tokens limit
        payload = {
            "domain": "cybersecurity",
            "prompt": "Write about network security.",
            "max_tokens": 1000  # Large limit
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        content = response.json()["content"]
        # Should not exceed reasonable limits
        assert len(content.split()) <= 200  # Approximate token limit

    def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        # Missing required fields
        incomplete_payloads = [
            {"domain": "cybersecurity"},  # Missing prompt
            {"prompt": "Test prompt"},    # Missing domain
            {}                           # Empty payload
        ]

        for payload in incomplete_payloads:
            response = client.post("/generate", json=payload)
            assert response.status_code in [400, 422]  # Bad request or validation error

    def test_real_world_scenarios_integration(self, client):
        """Test real-world content generation scenarios"""
        scenarios = [
            {
                "domain": "cybersecurity",
                "prompt": "Create a checklist for implementing zero-trust security.",
                "min_words": 100
            },
            {
                "domain": "ai_ml",
                "prompt": "Explain how AI can optimize supply chain management.",
                "min_words": 150
            },
            {
                "domain": "nutrition",
                "prompt": "Design a meal plan for vegan athletes.",
                "min_words": 200
            },
            {
                "domain": "ecommerce",
                "prompt": "Write a guide for launching a dropshipping business.",
                "min_words": 180
            }
        ]

        for scenario in scenarios:
            payload = {
                "domain": scenario["domain"],
                "prompt": scenario["prompt"],
                "max_tokens": 800
            }
            response = client.post("/generate", json=payload)
            assert response.status_code == 200
            content = response.json()["content"]

            # Check content quality
            word_count = len(content.split())
            assert word_count >= scenario["min_words"], f"Content too short for {scenario['domain']}: {word_count} words"

            # Check for domain-specific terminology
            domain_indicators = {
                "cybersecurity": ["security", "threat", "risk", "protection"],
                "ai_ml": ["machine learning", "algorithm", "data", "model"],
                "nutrition": ["diet", "nutrients", "meal", "calories"],
                "ecommerce": ["business", "customers", "sales", "market"]
            }

            indicators = domain_indicators[scenario["domain"]]
            content_lower = content.lower()
            has_domain_terms = any(term in content_lower for term in indicators)
            assert has_domain_terms, f"Missing domain-specific terms in {scenario['domain']} content"