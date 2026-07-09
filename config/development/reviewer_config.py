"""
Project Reviewer Agent Configuration
==================================

Configuration settings for the Project Reviewer Agent
"""

import os

# OpenRouter API Configuration
OPENROUTER_CONFIG = {
    "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
    "base_url": "https://openrouter.ai/api/v1",
    "model": "anthropic/claude-3.5-sonnet",  # More affordable model
    "max_tokens": 1500,  # Reduced to fit within credit limits
    "temperature": 0.9
}

# Review Criteria Weights
REVIEW_WEIGHTS = {
    "code_quality": 0.20,
    "architecture": 0.15,
    "ai_ml_implementation": 0.15,
    "performance": 0.10,
    "security": 0.15,
    "documentation": 0.10,
    "testing": 0.10,
    "maintainability": 0.10,
    "scalability": 0.05
}

# Severity Thresholds
SEVERITY_THRESHOLDS = {
    "critical": 8.0,  # Issues that must be fixed before production
    "high": 6.0,     # Important issues that should be addressed
    "medium": 4.0,   # Issues that can be addressed in next iteration
    "low": 2.0       # Minor issues or suggestions
}

# File Size Limits (bytes)
FILE_SIZE_LIMITS = {
    "large_file_warning": 500000,  # 500KB
    "large_file_critical": 1000000  # 1MB
}

# Complexity Thresholds
COMPLEXITY_THRESHOLDS = {
    "function_length": {
        "warning": 50,
        "critical": 100
    },
    "cyclomatic_complexity": {
        "warning": 10,
        "critical": 20
    },
    "directory_depth": {
        "warning": 4,
        "critical": 6
    }
}

# Language-specific patterns
LANGUAGE_PATTERNS = {
    "python": {
        "ml_libraries": [
            "tensorflow", "torch", "sklearn", "pandas", "numpy",
            "scipy", "matplotlib", "seaborn", "plotly", "keras",
            "transformers", "openai", "langchain"
        ],
        "web_frameworks": [
            "fastapi", "flask", "django", "starlette", "aiohttp"
        ],
        "testing_frameworks": [
            "pytest", "unittest", "nose", "mock"
        ]
    },
    "javascript": {
        "frameworks": [
            "react", "vue", "angular", "express", "next", "nuxt"
        ],
        "testing_frameworks": [
            "jest", "mocha", "jasmine", "cypress", "playwright"
        ]
    }
}

# Security Patterns to Check
SECURITY_PATTERNS = {
    "sql_injection": [
        r'execute\s*\(\s*f?["\'].*[{%].*["\']',  # Only flag execute statements with formatting
        r'cur\.execute\s*\(\s*f?["\'].*[{%].*["\']',  # Cursor execute with formatting
        r'["\'].*\+.*["\'].*execute',  # String concatenation in execute
    ],
    "hardcoded_secrets": [
        r'password\s*=\s*["\'][^"\']{2,}["\']',  # Minimum 2 chars to avoid false positives
        r'api_key\s*=\s*["\'][^"\']{10,}["\']',  # Minimum 10 chars for API keys
        r'secret\s*=\s*["\'][^"\']{5,}["\']'  # Minimum 5 chars for secrets
    ],
    "unsafe_deserialization": [
        r'pickle\.loads?\s*\(\s*(?!.*model|.*joblib)',  # Pickle load but exclude model files
        r'eval\s*\(\s*(?!.*test)',  # eval function but exclude test files  
        r'exec\s*\(\s*(?!.*test)',  # exec function but exclude test files
        r'__import__\s*\(\s*input',  # Dynamic imports with user input
        r'\.loads?\s*\(\s*request\.',  # Any loads with request data
    ]
}

# Documentation Requirements
DOCUMENTATION_REQUIREMENTS = {
    "readme_sections": [
        "installation", "usage", "api", "examples", "contributing"
    ],
    "code_comment_ratio": 0.15,  # 15% of lines should be comments
    "docstring_coverage": 0.80   # 80% of functions should have docstrings
}

# Testing Requirements
TESTING_REQUIREMENTS = {
    "min_test_coverage": 0.70,   # 70% test coverage
    "test_to_code_ratio": 0.30,  # 30% of files should be tests
    "required_test_types": [
        "unit", "integration", "end_to_end"
    ]
}

# Performance Benchmarks
PERFORMANCE_BENCHMARKS = {
    "max_file_size_mb": 1.0,
    "max_function_lines": 50,
    "max_class_methods": 20,
    "max_parameters": 5
}

# AI/ML Specific Checks
AI_ML_REQUIREMENTS = {
    "model_versioning": True,
    "data_validation": True,
    "experiment_tracking": True,
    "model_monitoring": True,
    "feature_store": False,  # Optional
    "a_b_testing": False     # Optional
}
