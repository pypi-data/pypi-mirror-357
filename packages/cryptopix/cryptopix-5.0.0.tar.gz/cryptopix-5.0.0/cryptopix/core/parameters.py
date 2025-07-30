"""
CryptoPIX Parameters Module

Defines security parameters and configuration for ChromaCrypt algorithms.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ChromaCryptParams:
    """ChromaCrypt algorithm parameters"""
    lattice_dimension: int
    modulus: int
    error_bound: int
    color_depth: int
    geometric_bits: int
    security_level: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary"""
        return {
            'lattice_dimension': self.lattice_dimension,
            'modulus': self.modulus,
            'error_bound': self.error_bound,
            'color_depth': self.color_depth,
            'geometric_bits': self.geometric_bits,
            'security_level': self.security_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChromaCryptParams':
        """Create parameters from dictionary"""
        return cls(**data)

# Security parameter sets
CHROMACRYPT_128_PARAMS = {
    'lattice_dimension': 512,
    'modulus': 65537,
    'error_bound': 6,
    'color_depth': 24,
    'geometric_bits': 8,
    'security_level': 128
}

CHROMACRYPT_192_PARAMS = {
    'lattice_dimension': 768,
    'modulus': 1048583,
    'error_bound': 8,
    'color_depth': 32,
    'geometric_bits': 16,
    'security_level': 192
}

CHROMACRYPT_256_PARAMS = {
    'lattice_dimension': 1024,
    'modulus': 16777259,
    'error_bound': 10,
    'color_depth': 48,
    'geometric_bits': 32,
    'security_level': 256
}

# Fast mode parameters (reduced security for speed)
CHROMACRYPT_FAST_128_PARAMS = {
    'lattice_dimension': 256,
    'modulus': 65537,
    'error_bound': 4,
    'color_depth': 24,
    'geometric_bits': 4,
    'security_level': 128
}

def get_params(security_level: int, fast_mode: bool = False) -> ChromaCryptParams:
    """Get parameters for specified security level"""
    if fast_mode and security_level == 128:
        return ChromaCryptParams(**CHROMACRYPT_FAST_128_PARAMS)
    elif security_level == 128:
        return ChromaCryptParams(**CHROMACRYPT_128_PARAMS)
    elif security_level == 192:
        return ChromaCryptParams(**CHROMACRYPT_192_PARAMS)
    elif security_level == 256:
        return ChromaCryptParams(**CHROMACRYPT_256_PARAMS)
    else:
        raise ValueError(f"Unsupported security level: {security_level}")

def validate_params(params: ChromaCryptParams) -> bool:
    """Validate parameter set"""
    # Basic validation
    if params.lattice_dimension <= 0:
        return False
    if params.modulus <= 1:
        return False
    if params.error_bound < 0:
        return False
    if params.color_depth not in [24, 32, 48]:
        return False
    if params.geometric_bits <= 0:
        return False
    if params.security_level not in [128, 192, 256]:
        return False
    
    # Security level validation
    min_dimensions = {128: 256, 192: 384, 256: 512}
    if params.lattice_dimension < min_dimensions[params.security_level]:
        return False
    
    return True