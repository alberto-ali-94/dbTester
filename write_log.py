from typing import TypedDict
from datetime import datetime

class LogEntry(TypedDict):
    topic: str
    clarity: str
    intent: str
    requires_clarification: bool
    confidence_score: str
    valid: bool
    timestamp: datetime

def write_log(log: LogEntry, file_name: str = 'log.txt') -> None:
    with open(file_name, 'a') as f:
        f.write(f"Topic: {log.get('topic', 'N/A')}\n")
        f.write(f"Chiarezza: {log.get('clarity', 'N/A')}\n")
        f.write(f"Intent: {log.get('intent', 'N/A')}\n")
        f.write(f"Richiede chiarimenti: {log.get('requires_clarification', 'N/A')}\n")
        f.write(f"Confidence: {log.get('confidence_score', 'N/A')}\n")
        f.write(f"Valido: {log.get('valid', 'N/A')}\n")
        f.write(f"Timestamp: {log.get('timestamp','N/A')}\n")