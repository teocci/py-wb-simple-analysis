"""
Created by Teocci.
Author: teocci@yandex.com
Date: 2025-1월-31
"""
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional

import requests
import schedule

# API Configuration
API_URL = "https://search.wb.ru/exactmatch/ru/common/v9/search"
PARAMS = {
    "ab_testing": "false",
    "appType": 1,
    "curr": "rub",
    "dest": -1257786,
    "lang": "ru",
    "page": 1,
    "query": "",
    "resultset": "catalog",
    "sort": "",
    "spp": 30,
    "suppressSpellcheck": "false"
}
CHECK_INTERVAL_MINUTES = 5  # Run every hour


class WildberriesTracker:
    def __init__(self):
        self.base_url = "https://search.wb.ru/exactmatch/ru/common/v9/search"
        self.ranks_dir = "ranks"
        self.analyses_dir = "analyses"
        self.position_history = defaultdict(list)
        os.makedirs(self.ranks_dir, exist_ok=True)
        os.makedirs(self.analyses_dir, exist_ok=True)

    def fetch_products(self, query: str, sort: str = "popular") -> Dict:
        params = {
            "ab_testing": "false",
            "appType": "1",
            "curr": "rub",
            "dest": "-1257786",
            "lang": "ru",
            "page": "1",
            "query": query,
            "resultset": "catalog",
            "sort": sort,
            "spp": "30",
            "suppressSpellcheck": "false"
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def _save_json(self, data: Dict, prefix: str, directory: str, query: str, sort: str) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}-{query}-{sort}-{timestamp}.json"
            filepath = os.path.join(directory, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving {prefix} file: {e}")
        except Exception as e:
            print(f"Unexpected error saving {prefix} file: {e}")

    def save_raw_data(self, data: Dict, query: str, sort: str) -> None:
        self._save_json(data, "ranks", self.ranks_dir, query, sort)

    def save_analysis(self, analysis: Dict, query: str, sort: str) -> None:
        self._save_json(analysis, "analysis", self.analyses_dir, query, sort)

    def get_previous_position(self, product_id: int) -> Optional[int]:
        history = self.position_history[product_id]
        return history[-1]['position'] if history else None

    def update_position_history(self, product_id: int, position: int, timestamp: str):
        self.position_history[product_id].append({
            'position': position,
            'timestamp': timestamp
        })

    def analyze_rankings(self, data: Dict) -> Dict:
        products = data.get('data', {}).get('products', [])
        timestamp = datetime.now().isoformat()
        analysis = {
            'timestamp': timestamp,
            'total_products': len(products),
            'advertised_products': [],
            'organic_products': [],
            'position_changes': []
        }

        for idx, product in enumerate(products, 1):
            product_id = product.get('id')
            prev_position = self.get_previous_position(product_id)

            product_info = {
                'position': idx,
                'previous_position': prev_position if prev_position else idx,
                'position_change': prev_position - idx if prev_position else 0,
                'id': product_id,
                'name': product.get('name'),
                'brand': product.get('brand'),
                'rating': product.get('rating'),
                'feedbacks': product.get('feedbacks'),
                'price': product.get('sizes', [{}])[0].get('price', {}).get('total')
            }

            self.update_position_history(product_id, idx, timestamp)

            if product.get('log', {}).get('promotion'):
                analysis['advertised_products'].append(product_info)
            else:
                analysis['organic_products'].append(product_info)

            if prev_position and prev_position > idx:
                analysis['position_changes'].append({
                    'id': product_id,
                    'name': product.get('name'),
                    'old_position': prev_position,
                    'new_position': idx,
                    'improvement': prev_position - idx
                })

        analysis['advertised_count'] = len(analysis['advertised_products'])
        analysis['organic_count'] = len(analysis['organic_products'])

        return analysis

    def generate_daily_summary(self, query: str, sort: str):
        summary = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'query': query,
            'sort': sort,
            'position_improvements': [],
            'total_movements': 0
        }

        for product_id, positions in self.position_history.items():
            if len(positions) >= 2:
                first_pos = positions[0]['position']
                last_pos = positions[-1]['position']
                if first_pos > last_pos:
                    summary['position_improvements'].append({
                        'product_id': product_id,
                        'start_position': first_pos,
                        'end_position': last_pos,
                        'improvement': first_pos - last_pos,
                        'timestamps': {
                            'start': positions[0]['timestamp'],
                            'end': positions[-1]['timestamp']
                        }
                    })

        summary['total_movements'] = len(summary['position_improvements'])
        summary['position_improvements'].sort(key=lambda x: x['improvement'], reverse=True)

        self._save_json(summary, "summary", self.ranks_dir, query, sort)
        self.position_history.clear()  # Reset for next day

    def track_rankings(self, query: str, sort: str = "popular"):
        try:
            print(f"Fetching rankings for: {query}")
            data = self.fetch_products(query, sort)
            self.save_raw_data(data, query, sort)

            analysis = self.analyze_rankings(data)
            self.save_analysis(analysis, query, sort)

            print(f"Found {analysis['advertised_count']} advertised and {analysis['organic_count']} organic products")
            if analysis['position_changes']:
                print(f"Detected {len(analysis['position_changes'])} position improvements")
        except Exception as e:
            print(f"Error occurred: {e}")


def main():
    tracker = WildberriesTracker()
    query = "Духи женские"

    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(tracker.track_rankings, query, "popular")
    schedule.every().day.at("23:59").do(tracker.generate_daily_summary, query, "popular")

    tracker.track_rankings(query)  # Initial run

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
