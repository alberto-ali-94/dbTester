from typing import TypedDict
from datetime import datetime
import os

class LogEntry(TypedDict):
    model_id: str
    test_proposed: str


def write_log(log: LogEntry, file_name: str = 'log') -> None:
    file_name_datetime = f"{file_name}_{datetime.now().isoformat()}.txt"
    path = os.path.join('logs',file_name_datetime)
    with open(file_name_datetime, 'a') as f:
        if isinstance(log, list):
            for item in log:
                f.write(f"Model ID: {item.get('model_id', 'N/A')}\n")
                f.write(f"Test Proposed: {item.get('test_proposed', 'N/A')}\n")
                f.write("-" * 50 + "\n")
        # Se è un singolo dizionario
        elif isinstance(log, dict):
            for key, value in log.items():
                f.write(f'{key}: {value}\n')
            f.write("-" * 50 + "\n")
