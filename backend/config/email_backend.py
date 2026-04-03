"""
Custom email backend that explicitly configures SSL context with certifi CA bundle.

This resolves SSLCertVerificationError when Django's default SMTP backend
can't find system CA certificates.
"""
import ssl
import certifi
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as DjangoSMTPBackend


class CertifiEmailBackend(DjangoSMTPBackend):
    """
    SMTP email backend that uses certifi's CA bundle for SSL verification.
    
    This backend extends Django's default SMTP backend to explicitly set
    the SSL context with certifi's certificate bundle, ensuring Gmail and
    other SMTP servers can be properly verified.
    
    For environments with TLS inspection (corporate proxies, antivirus, etc.)
    that inject self-signed certificates, you can set EMAIL_SKIP_SSL_VERIFY=True
    in your .env file to skip SSL certificate verification.
    
    WARNING: Skipping SSL verification should only be used in development/testing
    environments where security is not critical.
    """
    
    def open(self):
        """
        Ensure an open connection to the email server with proper SSL context.
        Returns True if connection is opened, False if it was already open.
        """
        if self.connection:
            return False
            
        connection_params = {
            'timeout': self.timeout,
        }
        
        # Create the connection
        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                **connection_params
            )
            
            # If using TLS, upgrade the connection with appropriate SSL context
            if self.use_tls:
                # Check if SSL verification should be skipped (for dev/testing only)
                skip_ssl_verify = getattr(settings, 'EMAIL_SKIP_SSL_VERIFY', False)
                
                if skip_ssl_verify:
                    # Create unverified context (INSECURE - dev/testing only)
                    ssl_context = ssl._create_unverified_context()
                else:
                    # Create SSL context with certifi bundle (SECURE)
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    
                self.connection.starttls(context=ssl_context)
                
            # Authenticate if credentials provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
                
            return True
        except Exception:
            if not self.fail_silently:
                raise
