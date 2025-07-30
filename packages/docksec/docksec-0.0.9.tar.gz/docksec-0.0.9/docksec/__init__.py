"""
DockSec - AI-Powered Docker Security Analyzer
"""

__version__ = "0.0.7"
__author__ = "Advait Patel"

from .utils import (
    get_custom_logger,
    load_docker_file,
    get_llm,
    analyze_security,
    AnalsesResponse,
    ScoreResponse
)

from .config import (
    BASE_DIR,
    OPENAI_API_KEY
)
from .config import docker_agent_prompt, docker_score_prompt, RESULTS_DIR
from .docker_scanner import DockerSecurityScanner
from .utils import ScoreResponse, get_llm, print_section

__all__ = [
    'get_custom_logger',
    'load_docker_file', 
    'get_llm',
    'analyze_security',
    'AnalsesResponse',
    'ScoreResponse',
    'docker_agent_prompt',
    'docker_score_prompt',
    'DockerSecurityScanner',
    'BASE_DIR',
    'OPENAI_API_KEY',
    'RESULTS_DIR',
    'print_section'
]