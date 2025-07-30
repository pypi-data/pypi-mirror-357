from .base import TableHandlerBase
import csv


class CSVHandler(TableHandlerBase):
    """CSV适配器"""

    def write(self, data: List[Dict], file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)

    def read(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)