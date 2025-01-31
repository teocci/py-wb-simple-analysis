"""
Created by Teocci.
Author: teocci@yandex.com
Date: 2025-1월-31
"""

import glob
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple

import matplotlib.pyplot as plt


def load_analysis_files(directory: str) -> List[Dict]:
    files = glob.glob(os.path.join(directory, 'analysis-*.json'))
    data = []
    for file in sorted(files):
        with open(file, 'r', encoding='utf-8') as f:
            data.append(json.load(f))
    return data


def extract_product_positions(analyses: List[Dict], product_id: int) -> Tuple[List[str], List[int]]:
    timestamps = []
    positions = []

    for analysis in analyses:
        all_products = analysis['advertised_products'] + analysis['organic_products']
        for product in all_products:
            if product['id'] == product_id:
                timestamps.append(datetime.fromisoformat(analysis['timestamp']))
                positions.append(product['position'])
                break

    return timestamps, positions


def plot_product_movement(product_id: int, analyses_dir: str = 'analyses'):
    analyses = load_analysis_files(analyses_dir)
    if not analyses:
        print("No analysis files found")
        return

    timestamps, positions = extract_product_positions(analyses, product_id)
    if not positions:
        print(f"Product {product_id} not found in analyses")
        return

    product_name = None
    for analysis in analyses:
        for product in analysis['advertised_products'] + analysis['organic_products']:
            if product['id'] == product_id:
                product_name = product['name']
                break
        if product_name:
            break

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, positions, 'b-o')

    plt.title(f'Position Movement\nProduct: {product_name if product_name else product_id}')
    plt.xlabel('Time')
    plt.ylabel('Position (1=Best, 100=Worst)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)

    # Add min/max position indicators
    min_pos = min(positions)
    max_pos = max(positions)
    plt.axhline(y=min_pos, color='g', linestyle='--', alpha=0.5, label=f'Best Position: {min_pos}')
    plt.axhline(y=max_pos, color='r', linestyle='--', alpha=0.5, label=f'Worst Position: {max_pos}')
    plt.legend()

    plt.ylim(max(positions) + 5, max(1, min(positions) - 5))  # Set range with padding
    plt.tight_layout()

    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(os.path.join(plot_dir, f'movement-{product_id}-{timestamp}.png'))
    plt.close()


if __name__ == "__main__":
    product_id = int(input("Enter product ID to plot: "))
    plot_product_movement(product_id)
