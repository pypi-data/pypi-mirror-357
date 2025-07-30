"""
CryptoPIX Color Lattice Engine

Implements the core Color Lattice Learning with Errors (CLWE) operations
that form the mathematical foundation of the ChromaCrypt algorithm suite.
"""

import os
import numpy as np
import hashlib
from typing import Tuple, Optional
from .parameters import ChromaCryptParams

class ColorLatticeEngine:
    """Core engine for Color Lattice Learning with Errors (CLWE)"""
    
    def __init__(self, params: ChromaCryptParams):
        self.params = params
        self.rng = np.random.default_rng()
        
    def generate_lattice_matrix(self, seed: bytes) -> np.ndarray:
        """Generate lattice matrix A from seed using deterministic process"""
        # Use seed to create deterministic random state
        rng = np.random.default_rng(int.from_bytes(seed[:8], 'big'))
        
        # Generate lattice matrix with specific structure for CLWE
        matrix = rng.integers(
            0, self.params.modulus, 
            size=(self.params.lattice_dimension, self.params.lattice_dimension),
            dtype=np.int64
        )
        
        # Ensure matrix has good properties for lattice cryptography
        # Add small perturbations to diagonal for better conditioning
        for i in range(min(matrix.shape)):
            matrix[i, i] = (matrix[i, i] + 1) % self.params.modulus
            
        return matrix
    
    def generate_secret_vector(self, seed: bytes) -> np.ndarray:
        """Generate secret vector s with small coefficients for security"""
        rng = np.random.default_rng(int.from_bytes(seed[8:16], 'big'))
        
        # Secret vector with bounded coefficients (ternary for efficiency)
        secret = rng.integers(
            -self.params.error_bound, self.params.error_bound + 1,
            size=self.params.lattice_dimension,
            dtype=np.int32
        )
        return secret
    
    def generate_error_vector(self, size: int, seed: Optional[bytes] = None) -> np.ndarray:
        """Generate error vector with discrete Gaussian distribution"""
        if seed:
            rng = np.random.default_rng(int.from_bytes(seed[:8], 'big'))
        else:
            rng = self.rng
            
        # Use discrete Gaussian approximation with bounded uniform distribution
        errors = rng.integers(
            -self.params.error_bound, self.params.error_bound + 1,
            size=size,
            dtype=np.int32
        )
        return errors
    
    def color_lattice_multiply(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Perform lattice multiplication with modular arithmetic"""
        # Ensure compatible types
        matrix = matrix.astype(np.int64)
        vector = vector.astype(np.int64)
        
        # Standard matrix-vector multiplication
        result = np.dot(matrix, vector) % self.params.modulus
        return result.astype(np.int64)
    
    def solve_clwe_sample(self, lattice_point: np.ndarray, secret: np.ndarray, 
                         matrix: np.ndarray) -> np.ndarray:
        """Solve CLWE sample to recover message (for decryption)"""
        # This is the core CLWE solving operation
        # In practice, this would use advanced lattice reduction techniques
        
        # Simplified approach: compute A*s and subtract from lattice_point
        expected = self.color_lattice_multiply(matrix, secret)
        difference = (lattice_point - expected) % self.params.modulus
        
        # The difference should be close to the original message + error
        # For now, we assume error is small and can be ignored
        return difference
    
    def create_clwe_sample(self, matrix: np.ndarray, secret: np.ndarray, 
                          message: np.ndarray, error: np.ndarray) -> np.ndarray:
        """Create CLWE sample: b = A*s + e + encode(message)"""
        # Compute A*s
        lattice_mult = self.color_lattice_multiply(matrix, secret)
        
        # Add error and encoded message
        result = (lattice_mult + error + message) % self.params.modulus
        return result.astype(np.int64)
    
    def encode_message_to_lattice(self, message: bytes) -> np.ndarray:
        """Encode message into lattice space"""
        # Convert message to integer array
        message_ints = np.frombuffer(message, dtype=np.uint8)
        
        # Extend or truncate to lattice dimension
        lattice_message = np.zeros(self.params.lattice_dimension, dtype=np.int64)
        
        # Fill with message data
        for i in range(min(len(message_ints), self.params.lattice_dimension)):
            lattice_message[i] = int(message_ints[i])
        
        # If message is shorter than lattice dimension, use hash to fill remaining
        if len(message_ints) < self.params.lattice_dimension:
            hash_seed = hashlib.sha256(message).digest()
            rng = np.random.default_rng(int.from_bytes(hash_seed[:8], 'big'))
            
            for i in range(len(message_ints), self.params.lattice_dimension):
                lattice_message[i] = rng.integers(0, 256)
        
        return lattice_message
    
    def decode_lattice_to_message(self, lattice_data: np.ndarray, 
                                 original_length: int) -> bytes:
        """Decode lattice data back to message"""
        # Extract message bytes from lattice
        message_ints = lattice_data[:original_length] % 256
        
        # Convert to bytes
        message_bytes = bytes(message_ints.astype(np.uint8))
        return message_bytes
    
    def get_lattice_security_level(self) -> float:
        """Estimate security level of current lattice parameters"""
        # Simplified security estimation based on lattice dimension and modulus
        # In practice, this would use more sophisticated analysis
        
        log_dimension = np.log2(self.params.lattice_dimension)
        log_modulus = np.log2(self.params.modulus)
        
        # Root Hermite Factor estimation
        delta = (self.params.lattice_dimension / (2 * np.pi * np.e)) ** (1 / (2 * self.params.lattice_dimension))
        
        # Estimated bit security
        estimated_security = log_dimension * log_modulus / (4 * np.log2(delta))
        
        return min(estimated_security, self.params.security_level)
    
    def validate_lattice_parameters(self) -> bool:
        """Validate that lattice parameters provide adequate security"""
        security_level = self.get_lattice_security_level()
        
        # Check if estimated security meets target
        if security_level < self.params.security_level * 0.8:  # Allow 20% margin
            return False
        
        # Check modulus is appropriate size
        min_modulus_bits = {128: 16, 192: 20, 256: 24}
        actual_modulus_bits = self.params.modulus.bit_length()
        
        if actual_modulus_bits < min_modulus_bits.get(self.params.security_level, 16):
            return False
        
        return True