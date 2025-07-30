from typing import TypedDict, Optional
from datetime import datetime
from dataclasses import dataclass
from chainsaws.aws.dynamodb.dynamodb_models import DynamoDBAPIConfig

@dataclass
class LockStatus:
    """Status of a distributed lock."""
    is_locked: bool
    owner_id: Optional[str]
    expires_at: Optional[int]
    last_renewed_at: Optional[datetime]
    metadata: Optional[dict]

@dataclass
class LockConfig(DynamoDBAPIConfig):
    """Configuration for distributed lock."""
    table_name: str  # DynamoDB table name
    ttl_seconds: int  # Lock timeout in seconds
    owner_id: str  # Unique identifier for lock owner
    retry_times: int  # Number of retry attempts
    retry_delay: float  # Delay between retries in seconds
    heartbeat_interval: int  # Interval for lock renewal in seconds

class LockItem(TypedDict):
    """Lock item structure in DynamoDB."""
    lock_id: str  # Unique lock identifier
    owner_id: str  # ID of the lock owner
    expires_at: int  # Expiration timestamp
    created_at: datetime  # Lock creation time
    last_renewed_at: Optional[datetime]  # Last renewal time
    metadata: Optional[dict]  # Additional lock metadata 