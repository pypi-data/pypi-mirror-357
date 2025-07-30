"""
Basic Usage Examples for CryptoPIX

This script demonstrates the fundamental operations of the CryptoPIX library
including key generation, encryption, decryption, and digital signatures.
"""

import cryptopix

def demo_key_encapsulation():
    """Demonstrate ChromaCrypt Key Encapsulation Mechanism"""
    print("=== ChromaCrypt KEM Demo ===")
    
    # Create KEM instance
    kem = cryptopix.create_kem(security_level=128)
    print("Created ChromaCrypt KEM with 128-bit post-quantum security")
    
    # Generate key pair
    public_key, private_key = kem.keygen()
    print("Generated key pair")
    print(f"Public key visual size: {len(public_key.visual_representation)} bytes")
    
    # Encapsulate shared secret
    shared_secret, capsule = kem.encapsulate(public_key)
    print(f"Encapsulated {len(shared_secret)} byte shared secret")
    print(f"Capsule size: {len(capsule)} bytes")
    
    # Decapsulate shared secret
    recovered_secret = kem.decapsulate(private_key, capsule)
    print(f"Decapsulated {len(recovered_secret)} byte shared secret")
    
    # Verify
    success = shared_secret == recovered_secret
    print(f"KEM test: {'PASSED' if success else 'FAILED'}")
    
    return success

def demo_digital_signatures():
    """Demonstrate ChromaCrypt Digital Signatures"""
    print("\n=== ChromaCrypt Digital Signatures Demo ===")
    
    # Create signature scheme
    sign = cryptopix.create_signature_scheme(security_level=128)
    print("Created ChromaCrypt signature scheme with 128-bit post-quantum security")
    
    # Generate signing key pair
    key_pair = sign.keygen()
    print("Generated signature key pair")
    print(f"Visual public key size: {len(key_pair.visual_public_key)} bytes")
    
    # Sign message
    message = b"Hello, this is a message signed with revolutionary ChromaCrypt!"
    signature = sign.sign(message, key_pair)
    print(f"Signed {len(message)} byte message")
    print(f"Signature contains {len(signature.color_commitment)} color commitments")
    
    # Verify signature
    is_valid = sign.verify(message, signature, key_pair)
    print(f"Signature verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Test with wrong message
    wrong_message = b"This is a different message"
    is_invalid = not sign.verify(wrong_message, signature, key_pair)
    print(f"Wrong message rejection: {'PASSED' if is_invalid else 'FAILED'}")
    
    return is_valid and is_invalid

def demo_symmetric_encryption():
    """Demonstrate Color Cipher symmetric encryption"""
    print("\n=== Color Cipher Symmetric Encryption Demo ===")
    
    # Create cipher instance
    cipher = cryptopix.create_cipher(security_level=128)
    print("Created ColorCipher with 128-bit security")
    
    # Test secure mode (with image output)
    plaintext = b"This is secret data encrypted with ChromaCrypt color transformation!"
    password = "super_secure_password_123"
    
    print("\n--- Secure Mode ---")
    image_data, color_key = cipher.encrypt(plaintext, password)
    print(f"Encrypted {len(plaintext)} bytes to {len(image_data)} byte image")
    print(f"Generated color key with {color_key.metadata.get('color_count', 0)} colors")
    
    # Decrypt
    recovered_text = cipher.decrypt(image_data, color_key, password)
    secure_success = plaintext == recovered_text
    print(f"Secure decryption: {'PASSED' if secure_success else 'FAILED'}")
    
    # Test fast mode (with hex color string output)
    print("\n--- Fast Mode ---")
    cipher.fast_mode = True
    color_string, fast_key = cipher.encrypt(plaintext, password)
    print(f"Fast encrypted to {len(color_string)} character color string")
    print(f"Color string preview: {color_string[:60]}...")
    
    # Decrypt fast mode
    recovered_fast = cipher.decrypt(color_string, fast_key, password)
    fast_success = plaintext == recovered_fast
    print(f"Fast decryption: {'PASSED' if fast_success else 'FAILED'}")
    
    return secure_success and fast_success

def demo_color_hashing():
    """Demonstrate Color Hash functions"""
    print("\n=== Color Hash Demo ===")
    
    # Create hash instance
    hasher = cryptopix.create_hash(security_level=128)
    print("Created ColorHash with 128-bit security")
    
    # Hash data to colors
    data = b"Hello, ChromaCrypt! This data will be hashed to colors."
    colors = hasher.hash_to_colors(data)
    print(f"Hashed {len(data)} bytes to {len(colors)} colors")
    print(f"First few colors: {colors[:3]}...")
    
    # Hash to hex string
    hex_hash = hasher.hash_to_hex_string(data)
    print(f"Hex color hash: {hex_hash[:30]}...")
    
    # Verify hash
    is_valid = hasher.verify_hash(data, colors)
    print(f"Hash verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Test with different data
    different_data = b"Different data"
    is_different = not hasher.verify_hash(different_data, colors)
    print(f"Different data rejection: {'PASSED' if is_different else 'FAILED'}")
    
    # Hash properties analysis
    properties = hasher.get_hash_properties(colors)
    print(f"Hash entropy: {properties['entropy']:.2f}")
    print(f"Unique colors: {properties['unique_colors']}/{properties['total_colors']}")
    
    return is_valid and is_different

def demo_visual_steganography():
    """Demonstrate visual steganographic properties"""
    print("\n=== Visual Steganography Demo ===")
    
    # Generate KEM keys with visual representation
    kem = cryptopix.create_kem(128)
    public_key, private_key = kem.keygen()
    
    # Save visual public key
    with open('demo_public_key.png', 'wb') as f:
        f.write(public_key.visual_representation)
    print("Saved visual public key as demo_public_key.png")
    
    # Generate signature with visual output
    sign = cryptopix.create_signature_scheme(128)
    key_pair = sign.keygen()
    message = b"Visual signature demo"
    signature = sign.sign(message, key_pair)
    
    # Save visual signature
    with open('demo_signature.png', 'wb') as f:
        f.write(signature.visual_signature)
    print("Saved visual signature as demo_signature.png")
    
    # Create color hash image
    hasher = cryptopix.create_hash(128)
    hash_data = b"This hash will be visualized as an image"
    hash_image = hasher.hash_to_image(hash_data)
    
    with open('demo_hash.png', 'wb') as f:
        f.write(hash_image)
    print("Saved color hash as demo_hash.png")
    
    print("Visual representations created - check the PNG files!")
    return True

def main():
    """Run all demos"""
    print("CryptoPIX Revolutionary Post-Quantum Cryptography Demo")
    print("=" * 60)
    
    results = []
    
    # Run demonstrations
    results.append(demo_key_encapsulation())
    results.append(demo_digital_signatures())
    results.append(demo_symmetric_encryption())
    results.append(demo_color_hashing())
    results.append(demo_visual_steganography())
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    
    demos = [
        "ChromaCrypt KEM",
        "Digital Signatures", 
        "Symmetric Encryption",
        "Color Hashing",
        "Visual Steganography"
    ]
    
    for demo, result in zip(demos, results):
        status = "PASSED" if result else "FAILED"
        print(f"{demo:<25} {status}")
    
    total_passed = sum(results)
    print(f"\nTotal: {total_passed}/{len(results)} demos passed")
    
    if total_passed == len(results):
        print("\n🎉 All CryptoPIX demos completed successfully!")
        print("The revolutionary post-quantum cryptography is working perfectly!")
    else:
        print(f"\n⚠️  {len(results) - total_passed} demo(s) failed")

if __name__ == "__main__":
    main()