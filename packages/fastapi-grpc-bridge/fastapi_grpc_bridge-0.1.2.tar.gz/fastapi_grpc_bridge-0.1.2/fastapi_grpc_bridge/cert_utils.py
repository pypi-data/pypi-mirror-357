import os
import grpc
from typing import Optional, List
from pathlib import Path
from .config import GRPCSecurityConfig, TLSConfig, MTLSConfig


def load_certificate_file(file_path: str) -> bytes:
    """Load certificate or key file and return its contents as bytes"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Certificate file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading certificate file {file_path}: {e}")


def create_server_credentials(config: GRPCSecurityConfig) -> grpc.ServerCredentials:
    """Create gRPC server credentials based on configuration"""
    if not config.is_secure():
        raise ValueError("TLS or mTLS must be enabled to create server credentials")
    
    # Load server certificate and key
    server_cert = load_certificate_file(config.tls.cert_file)
    server_key = load_certificate_file(config.tls.key_file)
    
    # Basic TLS setup
    server_cert_key_pairs = [(server_key, server_cert)]
    
    if config.mtls.enabled:
        # Load CA certificate for client verification
        ca_cert = load_certificate_file(config.mtls.ca_cert_file)
        
        # Create credentials with client certificate verification
        credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=server_cert_key_pairs,
            root_certificates=ca_cert,
            require_client_auth=config.mtls.client_cert_required
        )
    else:
        # Create credentials for TLS only (no client cert verification)
        root_certificates = None
        if config.tls.ca_cert_file:
            root_certificates = load_certificate_file(config.tls.ca_cert_file)
        
        credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=server_cert_key_pairs,
            root_certificates=root_certificates,
            require_client_auth=False
        )
    
    return credentials


def create_client_credentials(config: GRPCSecurityConfig) -> grpc.ChannelCredentials:
    """Create gRPC client credentials based on configuration"""
    if not config.is_secure():
        raise ValueError("TLS or mTLS must be enabled to create client credentials")
    
    root_certificates = None
    private_key = None
    certificate_chain = None
    
    # Load CA certificate if provided
    if config.tls.ca_cert_file:
        root_certificates = load_certificate_file(config.tls.ca_cert_file)
    elif config.mtls.ca_cert_file:
        root_certificates = load_certificate_file(config.mtls.ca_cert_file)
    
    # Load client certificates for mTLS
    if config.mtls.enabled and config.mtls.client_cert_file and config.mtls.client_key_file:
        private_key = load_certificate_file(config.mtls.client_key_file)
        certificate_chain = load_certificate_file(config.mtls.client_cert_file)
    
    credentials = grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain
    )
    
    return credentials


def validate_certificates(config: GRPCSecurityConfig) -> List[str]:
    """Validate all certificate files and return list of issues"""
    issues = []
    
    if not config.is_secure():
        return issues
    
    # Validate TLS certificates
    if config.tls.enabled:
        if not config.tls.cert_file:
            issues.append("TLS cert_file is required when TLS is enabled")
        elif not Path(config.tls.cert_file).exists():
            issues.append(f"TLS certificate file not found: {config.tls.cert_file}")
        
        if not config.tls.key_file:
            issues.append("TLS key_file is required when TLS is enabled")
        elif not Path(config.tls.key_file).exists():
            issues.append(f"TLS key file not found: {config.tls.key_file}")
        
        if config.tls.ca_cert_file and not Path(config.tls.ca_cert_file).exists():
            issues.append(f"TLS CA certificate file not found: {config.tls.ca_cert_file}")
    
    # Validate mTLS certificates
    if config.mtls.enabled:
        if not config.mtls.ca_cert_file:
            issues.append("mTLS ca_cert_file is required when mTLS is enabled")
        elif not Path(config.mtls.ca_cert_file).exists():
            issues.append(f"mTLS CA certificate file not found: {config.mtls.ca_cert_file}")
        
        if config.mtls.client_cert_file and not Path(config.mtls.client_cert_file).exists():
            issues.append(f"mTLS client certificate file not found: {config.mtls.client_cert_file}")
        
        if config.mtls.client_key_file and not Path(config.mtls.client_key_file).exists():
            issues.append(f"mTLS client key file not found: {config.mtls.client_key_file}")
    
    return issues


def generate_self_signed_cert(cert_dir: str = "./certs", 
                             server_name: str = "localhost",
                             days_valid: int = 365) -> dict:
    """
    Generate self-signed certificates for development/testing.
    Returns dictionary with file paths.
    
    Note: This requires the cryptography library to be installed.
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
    except ImportError:
        raise ImportError(
            "cryptography library is required for certificate generation. "
            "Install it with: pip install cryptography"
        )
    
    # Create certificate directory
    cert_path = Path(cert_dir)
    cert_path.mkdir(exist_ok=True)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, server_name),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(server_name),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Save private key
    key_file = cert_path / "server.key"
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save certificate
    cert_file = cert_path / "server.crt"
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    return {
        "cert_file": str(cert_file),
        "key_file": str(key_file),
        "ca_cert_file": str(cert_file)  # Self-signed cert acts as its own CA
    }


# Add ipaddress import at the top level to avoid issues
try:
    import ipaddress
except ImportError:
    pass  # Will be caught when trying to use generate_self_signed_cert 