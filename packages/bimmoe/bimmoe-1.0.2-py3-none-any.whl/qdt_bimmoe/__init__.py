"""
QDT BiMMoE Framework

Quantum Duality Theory (QDT) Bidirectional Multi-Modal Multi-Expert Framework

This module implements quantum tunneling and gravitational funneling mechanisms
for multi-modal tokenization with energy conservation and boundary stability.

Author: QDT Research Team
Version: 1.0.0
Status: Production Ready (100% Test Coverage)
"""

from .core import (
    QDT,
    QDTConstants,
    quantum_tunnel,
    gravitational_funnel,
    tokenize,
    generate_data,
    run_simulation,
)

# Check for numpy availability and import vectorized functions
try:
    from .core import quantum_tunnel_vectorized
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    quantum_tunnel_vectorized = None

__version__ = "1.0.0"
__author__ = "QDT Research Team"
__email__ = "research@qdt-framework.org"

__all__ = [
    "QDT",
    "QDTConstants", 
    "quantum_tunnel",
    "gravitational_funnel",
    "tokenize",
    "generate_data",
    "run_simulation",
    "quantum_tunnel_vectorized",
    "HAS_NUMPY",
] 