from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
import os


@dataclass
class TLSConfig:
    """Configuration for TLS settings"""
    enabled: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_cert_file: Optional[str] = None
    server_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate TLS configuration"""
        if self.enabled:
            if not self.cert_file or not self.key_file:
                raise ValueError("cert_file and key_file are required when TLS is enabled")
            
            # Validate files exist
            if not Path(self.cert_file).exists():
                raise FileNotFoundError(f"Certificate file not found: {self.cert_file}")
            if not Path(self.key_file).exists():
                raise FileNotFoundError(f"Key file not found: {self.key_file}")
            if self.ca_cert_file and not Path(self.ca_cert_file).exists():
                raise FileNotFoundError(f"CA certificate file not found: {self.ca_cert_file}")


@dataclass 
class MTLSConfig:
    """Configuration for mutual TLS (mTLS) settings"""
    enabled: bool = False
    client_cert_required: bool = True
    ca_cert_file: Optional[str] = None
    client_cert_file: Optional[str] = None
    client_key_file: Optional[str] = None
    verify_client_cert: bool = True
    
    def __post_init__(self):
        """Validate mTLS configuration"""
        if self.enabled:
            if not self.ca_cert_file:
                raise ValueError("ca_cert_file is required when mTLS is enabled")
            
            # Validate CA cert exists
            if not Path(self.ca_cert_file).exists():
                raise FileNotFoundError(f"CA certificate file not found: {self.ca_cert_file}")
            
            # If client certs are provided, validate them
            if self.client_cert_file:
                if not Path(self.client_cert_file).exists():
                    raise FileNotFoundError(f"Client certificate file not found: {self.client_cert_file}")
            if self.client_key_file:
                if not Path(self.client_key_file).exists():
                    raise FileNotFoundError(f"Client key file not found: {self.client_key_file}")


@dataclass
class GRPCSecurityConfig:
    """Main configuration class for gRPC security settings"""
    host: str = "[::]"
    port: int = 50051
    max_workers: int = 10
    tls: TLSConfig = field(default_factory=TLSConfig)
    mtls: MTLSConfig = field(default_factory=MTLSConfig)
    insecure: bool = True  # Default to insecure for backward compatibility
    
    def __post_init__(self):
        """Validate overall configuration"""
        if self.tls.enabled and self.insecure:
            raise ValueError("Cannot enable both TLS and insecure mode")
        
        if self.mtls.enabled and not self.tls.enabled:
            # mTLS requires TLS to be enabled
            self.tls.enabled = True
            if not self.tls.cert_file or not self.tls.key_file:
                raise ValueError("TLS cert_file and key_file are required when mTLS is enabled")
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GRPCSecurityConfig':
        """Create configuration from dictionary"""
        tls_config = TLSConfig(**config_dict.get('tls', {}))
        mtls_config = MTLSConfig(**config_dict.get('mtls', {}))
        
        return cls(
            host=config_dict.get('host', '[::]'),
            port=config_dict.get('port', 50051),
            max_workers=config_dict.get('max_workers', 10),
            tls=tls_config,
            mtls=mtls_config,
            insecure=config_dict.get('insecure', True)
        )
    
    @classmethod
    def from_env(cls) -> 'GRPCSecurityConfig':
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv('GRPC_HOST', '[::]'),
            port=int(os.getenv('GRPC_PORT', '50051')),
            max_workers=int(os.getenv('GRPC_MAX_WORKERS', '10')),
            insecure=os.getenv('GRPC_INSECURE', 'true').lower() == 'true',
            tls=TLSConfig(
                enabled=os.getenv('GRPC_TLS_ENABLED', 'false').lower() == 'true',
                cert_file=os.getenv('GRPC_TLS_CERT_FILE'),
                key_file=os.getenv('GRPC_TLS_KEY_FILE'),
                ca_cert_file=os.getenv('GRPC_TLS_CA_CERT_FILE'),
                server_name=os.getenv('GRPC_TLS_SERVER_NAME')
            ),
            mtls=MTLSConfig(
                enabled=os.getenv('GRPC_MTLS_ENABLED', 'false').lower() == 'true',
                client_cert_required=os.getenv('GRPC_MTLS_CLIENT_CERT_REQUIRED', 'true').lower() == 'true',
                ca_cert_file=os.getenv('GRPC_MTLS_CA_CERT_FILE'),
                client_cert_file=os.getenv('GRPC_MTLS_CLIENT_CERT_FILE'),
                client_key_file=os.getenv('GRPC_MTLS_CLIENT_KEY_FILE'),
                verify_client_cert=os.getenv('GRPC_MTLS_VERIFY_CLIENT_CERT', 'true').lower() == 'true'
            )
        )
    
    def is_secure(self) -> bool:
        """Check if any secure mode is enabled"""
        return self.tls.enabled or self.mtls.enabled 