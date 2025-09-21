from typing import TypedDict
from datetime import datetime
import os

class LogEntry(TypedDict):
    topic: str
    clarity: str
    intent: str
    requires_clarification: bool
    confidence_score: str
    valid: bool
    timestamp: datetime

def write_log(log: LogEntry, file_name: str = 'log.txt') -> None:
    file_name_datetime = '_'.join(file_name,datetime.now().isoformat())
    path = os.path.join('logs',file_name_datetime)
    with open(path, 'a') as f:
        f.write(f"Topic: {log.get('topic', 'N/A')}\n")
        f.write(f"Chiarezza: {log.get('clarity', 'N/A')}\n")
        f.write(f"Intent: {log.get('intent', 'N/A')}\n")
        f.write(f"Richiede chiarimenti: {log.get('requires_clarification', 'N/A')}\n")
        f.write(f"Confidence: {log.get('confidence_score', 'N/A')}\n")
        f.write(f"Valido: {log.get('valid', 'N/A')}\n")
        f.write(f"Timestamp: {log.get('timestamp','N/A')}\n")