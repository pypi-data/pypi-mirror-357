"""
CryptoPIX Color Transformation Engine

Implements the revolutionary color transformation algorithms that convert
lattice points to colors and provide the visual steganographic properties
of the ChromaCrypt system.
"""

import hashlib
import numpy as np
from typing import Tuple, List, Dict, Any
from PIL import Image
from io import BytesIO
import json

from .parameters import ChromaCryptParams

class ColorTransformEngine:
    """Engine for CryptoPIX color transformations in lattice space"""
    
    def __init__(self, params: ChromaCryptParams):
        self.params = params
        
    def lattice_to_color(self, lattice_point: np.ndarray, position: int, 
                        context: Dict[str, Any] = None) -> Tuple[int, int, int]:
        """Transform lattice point to RGB color using enhanced CryptoPIX methodology"""
        context = context or {}
        
        # Multi-stage color generation
        base_color = self._extract_base_color(lattice_point)
        position_color = self._apply_position_transform(base_color, position)
        context_color = self._apply_context_transform(position_color, context)
        
        return self._normalize_color(context_color)
    
    def _extract_base_color(self, lattice_point: np.ndarray) -> Tuple[int, int, int]:
        """Extract base RGB values from lattice coordinates"""
        if self.params.color_depth == 24:
            # Standard RGB extraction
            r = int(lattice_point[0] % 256)
            g = int(lattice_point[1] % 256) if len(lattice_point) > 1 else 0
            b = int(lattice_point[2] % 256) if len(lattice_point) > 2 else 0
            
        elif self.params.color_depth == 32:
            # Extended color space with alpha blending
            r = int(lattice_point[0] % 256)
            g = int(lattice_point[1] % 256) if len(lattice_point) > 1 else 0
            b = int(lattice_point[2] % 256) if len(lattice_point) > 2 else 0
            alpha = int(lattice_point[3] % 256) if len(lattice_point) > 3 else 128
            
            # Blend with alpha
            r = (r * alpha + (255 - alpha) * 128) // 255
            g = (g * alpha + (255 - alpha) * 128) // 255
            b = (b * alpha + (255 - alpha) * 128) // 255
            
        else:  # 48-bit high precision
            # High precision color extraction
            r = int(lattice_point[0] % 65536) >> 8
            g = int(lattice_point[1] % 65536) >> 8 if len(lattice_point) > 1 else 0
            b = int(lattice_point[2] % 65536) >> 8 if len(lattice_point) > 2 else 0
            
        return (r, g, b)
    
    def _apply_position_transform(self, color: Tuple[int, int, int], 
                                position: int) -> Tuple[int, int, int]:
        """Apply position-based geometric transformation"""
        r, g, b = color
        
        # Generate position-dependent hash
        position_bytes = position.to_bytes(8, 'big')
        position_hash = hashlib.sha256(position_bytes).digest()
        
        # Apply geometric transformation
        # Use golden ratio for optimal distribution
        phi = 1.618033988749895
        angle = (position * phi) % (2 * np.pi)
        
        # Create transformation matrix based on position
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        transform_matrix = np.array([
            [cos_a, -sin_a, position_hash[0] / 255.0],
            [sin_a, cos_a, position_hash[1] / 255.0],
            [0, 0, 1]
        ])
        
        # Apply transformation
        color_vector = np.array([r / 255.0, g / 255.0, 1.0])
        transformed = np.dot(transform_matrix, color_vector)
        
        # Extract transformed colors
        r_new = int((transformed[0] % 1.0) * 255)
        g_new = int((transformed[1] % 1.0) * 255)
        b_new = (b + position_hash[2]) % 256
        
        return (r_new, g_new, b_new)
    
    def _apply_context_transform(self, color: Tuple[int, int, int], 
                               context: Dict[str, Any]) -> Tuple[int, int, int]:
        """Apply context-dependent transformations"""
        r, g, b = color
        
        # Previous colors influence (chain dependency)
        if 'previous_colors' in context:
            prev_colors = context['previous_colors']
            if prev_colors:
                # Average of previous colors
                prev_r = sum(c[0] for c in prev_colors) // len(prev_colors)
                prev_g = sum(c[1] for c in prev_colors) // len(prev_colors)
                prev_b = sum(c[2] for c in prev_colors) // len(prev_colors)
                
                # Apply influence
                r = (r + prev_r // 4) % 256
                g = (g + prev_g // 4) % 256
                b = (b + prev_b // 4) % 256
        
        # Global key influence
        if 'key_hash' in context:
            key_hash = context['key_hash']
            r = (r + key_hash[0]) % 256
            g = (g + key_hash[1]) % 256
            b = (b + key_hash[2]) % 256
        
        return (r, g, b)
    
    def _normalize_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Ensure color values are in valid range"""
        r, g, b = color
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    def color_to_lattice(self, color: Tuple[int, int, int], position: int,
                        context: Dict[str, Any] = None) -> np.ndarray:
        """Reverse transform color to lattice coordinates"""
        context = context or {}
        r, g, b = color
        
        # Reverse context transformations
        if 'key_hash' in context:
            key_hash = context['key_hash']
            r = (r - key_hash[0]) % 256
            g = (g - key_hash[1]) % 256
            b = (b - key_hash[2]) % 256
        
        # Reverse position transformation (simplified)
        position_bytes = position.to_bytes(8, 'big')
        position_hash = hashlib.sha256(position_bytes).digest()
        b = (b - position_hash[2]) % 256
        
        # Convert back to lattice coordinates
        lattice_coords = np.array([r, g, b], dtype=np.int64)
        
        # Extend to full lattice dimension
        if len(lattice_coords) < self.params.lattice_dimension:
            # Pad with derived values using deterministic expansion
            padding = np.zeros(self.params.lattice_dimension - 3, dtype=np.int64)
            
            # Use color values to generate padding deterministically
            seed_value = (r << 16) | (g << 8) | b
            rng = np.random.default_rng(seed_value)
            
            for i in range(len(padding)):
                padding[i] = rng.integers(0, self.params.modulus)
                
            lattice_coords = np.concatenate([lattice_coords, padding])
            
        return lattice_coords[:self.params.lattice_dimension]
    
    def create_visual_representation(self, colors: List[Tuple[int, int, int]], 
                                   format: str = 'PNG') -> bytes:
        """Create visual representation of colors as image"""
        if not colors:
            colors = [(0, 0, 0)]
            
        # Calculate optimal image dimensions
        total_pixels = len(colors)
        width = int(np.ceil(np.sqrt(total_pixels)))
        height = int(np.ceil(total_pixels / width))
        
        # Pad colors if needed
        while len(colors) < width * height:
            colors.append((0, 0, 0))
            
        # Create image
        img = Image.new('RGB', (width, height))
        img.putdata(colors[:width * height])
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format=format)
        return img_buffer.getvalue()
    
    def extract_colors_from_image(self, image_data: bytes) -> List[Tuple[int, int, int]]:
        """Extract colors from image data"""
        img = Image.open(BytesIO(image_data))
        img = img.convert('RGB')  # Ensure RGB mode
        
        colors = list(img.getdata())
        # Filter out padding (black pixels at the end)
        while colors and colors[-1] == (0, 0, 0):
            colors.pop()
            
        return colors
    
    def create_color_pattern(self, colors: List[Tuple[int, int, int]], 
                           pattern_type: str = 'spiral') -> List[Tuple[int, int, int]]:
        """Arrange colors in specific geometric patterns"""
        if not colors:
            return colors
            
        if pattern_type == 'spiral':
            return self._arrange_spiral(colors)
        elif pattern_type == 'fibonacci':
            return self._arrange_fibonacci(colors)
        elif pattern_type == 'golden':
            return self._arrange_golden_ratio(colors)
        else:
            return colors  # Linear arrangement
    
    def _arrange_spiral(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Arrange colors in spiral pattern"""
        if len(colors) <= 1:
            return colors
            
        # Create spiral ordering
        n = len(colors)
        width = int(np.ceil(np.sqrt(n)))
        height = int(np.ceil(n / width))
        
        # Generate spiral indices
        spiral_order = []
        visited = [[False] * width for _ in range(height)]
        
        # Directions: right, down, left, up
        dx = [0, 1, 0, -1]
        dy = [1, 0, -1, 0]
        direction = 0
        
        x, y = 0, 0
        for i in range(min(n, width * height)):
            if 0 <= x < height and 0 <= y < width and not visited[x][y]:
                spiral_order.append(x * width + y)
                visited[x][y] = True
                
                # Try to continue in current direction
                nx, ny = x + dx[direction], y + dy[direction]
                if not (0 <= nx < height and 0 <= ny < width and not visited[nx][ny]):
                    # Change direction
                    direction = (direction + 1) % 4
                    nx, ny = x + dx[direction], y + dy[direction]
                
                x, y = nx, ny
            else:
                # Find next unvisited cell
                found = False
                for i in range(height):
                    for j in range(width):
                        if not visited[i][j]:
                            x, y = i, j
                            found = True
                            break
                    if found:
                        break
        
        # Rearrange colors according to spiral order
        arranged_colors = [colors[0]] * len(colors)
        for i, spiral_idx in enumerate(spiral_order[:len(colors)]):
            if spiral_idx < len(colors):
                arranged_colors[i] = colors[spiral_idx]
                
        return arranged_colors
    
    def _arrange_fibonacci(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Arrange colors using Fibonacci sequence spacing"""
        if len(colors) <= 2:
            return colors
            
        # Generate Fibonacci sequence
        fib = [1, 1]
        while fib[-1] < len(colors):
            fib.append(fib[-1] + fib[-2])
        
        # Rearrange colors using Fibonacci indices
        arranged = []
        used_indices = set()
        
        for f in fib:
            idx = f % len(colors)
            if idx not in used_indices:
                arranged.append(colors[idx])
                used_indices.add(idx)
        
        # Add remaining colors
        for i, color in enumerate(colors):
            if i not in used_indices:
                arranged.append(color)
                
        return arranged
    
    def _arrange_golden_ratio(self, colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Arrange colors using golden ratio distribution"""
        if len(colors) <= 1:
            return colors
            
        phi = 1.618033988749895
        arranged = []
        
        # Generate golden ratio sequence
        indices = []
        for i in range(len(colors)):
            golden_idx = int((i * phi) % len(colors))
            indices.append(golden_idx)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_indices = []
        for idx in indices:
            if idx not in seen:
                unique_indices.append(idx)
                seen.add(idx)
        
        # Add any missing indices
        for i in range(len(colors)):
            if i not in seen:
                unique_indices.append(i)
        
        # Arrange colors
        for idx in unique_indices[:len(colors)]:
            arranged.append(colors[idx])
            
        return arranged