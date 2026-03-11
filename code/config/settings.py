import os


class Settings:
    NATS_URL: str = os.getenv("NATS_URL", "nats://localhost:4222")
    NATS_CLIENT_NAME: str = os.getenv("NATS_CLIENT_NAME", "mes-orchestrator")


settings = Settings()