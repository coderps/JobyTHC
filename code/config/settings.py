"""
Configuration settings for the MES (Manufacturing Execution System) application.

This module loads environment variables and provides default configuration values
for NATS event broker connectivity.
"""
import os


class Settings:
    """Application configuration settings loaded from environment variables."""
    # NATS event broker URL (defaults to local development instance)
    NATS_URL: str = os.getenv("NATS_URL", "nats://localhost:4222")
    
    # NATS client identifier for this MES orchestrator instance
    NATS_CLIENT_NAME: str = os.getenv("NATS_CLIENT_NAME", "mes-orchestrator")


# Global settings instance used throughout the application
settings = Settings()