"""
Created by Teocci.
Author: teocci@yandex.com
Date: 2025-1월-31
"""
import argparse
import csv
import glob
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Tuple


def get_first_and_latest_analysis(analyses_dir: str = 'analyses') -> Tuple[Optional[Dict], Optional[Dict]]:
    today = datetime.now().strftime('%Y%m%d')
    files = glob.glob(os.path.join(analyses_dir, f'analysis-*-{today}*.json'))

    if not files:
        return None, None

    first_file = min(files, key=os.path.getctime)
    latest_file = max(files, key=os.path.getctime)

    with open(first_file, 'r', encoding='utf-8') as f:
        first = json.load(f)
    with open(latest_file, 'r', encoding='utf-8') as f:
        latest = json.load(f)

    return first, latest


def get_first_position(product_id: int, first_analysis: Dict) -> Optional[int]:
    all_products = (first_analysis['advertised_products'] +
                    first_analysis['organic_products'])
    for product in all_products:
        if product['id'] == product_id:
            return product['position']
    return None


def save_to_csv(products: List[Dict], report_type: str, timestamp: str) -> str:
    os.makedirs('reports', exist_ok=True)
    report_id = str(uuid.uuid4())[:8]
    filename = f'report-{report_type}-{timestamp}-{report_id}.csv'
    filepath = os.path.join('reports', filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Position', 'First Position Today', 'ID', 'Name',
                         'Brand', 'Rating', 'Feedbacks'])
        for p in products:
            writer.writerow([
                p['position'],
                p.get('first_position', '-'),
                p['id'],
                p['name'],
                p['brand'],
                p['rating'],
                p['feedbacks']
            ])
    return filepath


def print_product_list(first_analysis: Dict, latest_analysis: Dict,
                       show_advertised: bool = True) -> None:
    products = (latest_analysis['advertised_products'] if show_advertised
                else latest_analysis['organic_products'])
    list_type = "Advertised" if show_advertised else "Organic"
    timestamp = datetime.fromisoformat(latest_analysis['timestamp']).strftime('%Y%m%d_%H%M%S')

    print(
        f"\n{list_type} Products - {datetime.fromisoformat(latest_analysis['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)

    for product in products:
        first_pos = get_first_position(product['id'], first_analysis)
        product['first_position'] = first_pos
        first_pos_str = f"[{first_pos}]" if first_pos else "[-]"
        print(f"{product['position']:3d} {first_pos_str:6} {product['id']:10d} {product['name']}")

    csv_file = save_to_csv(products, list_type.lower(), timestamp)
    print(f"\nReport saved to: {csv_file}")


def main():
    parser = argparse.ArgumentParser(description='List advertised or organic products')
    parser.add_argument('--organic', action='store_true',
                        help='Show organic products instead of advertised')
    args = parser.parse_args()

    first_analysis, latest_analysis = get_first_and_latest_analysis()
    if not first_analysis or not latest_analysis:
        print("No analysis files found for today")
        return

    print_product_list(first_analysis, latest_analysis, not args.organic)


if __name__ == "__main__":
    main()
