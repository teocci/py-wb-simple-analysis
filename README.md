# Python Wildberries Simple Analysis

Python tools for analyzing Wildberries product rankings and tracking advertising positions.

## Tools

### Ranking Tracker (`tracker.py`)
Tracks product rankings and advertising positions hourly:
- Fetches product data from Wildberries API
- Saves raw data and analysis files
- Tracks position movements
- Generates daily summaries

```bash
pip install requests schedule
python tracker.py
```

### Position Plotter (`plot_positions.py`)
Visualizes position changes for specific products:
- Creates line charts showing position movement
- Highlights best/worst positions
- Saves plots to `plots` directory

```bash
pip install matplotlib
python plot_positions.py
```

### Ad Tracker (`ad_tracker.py`)
Analyzes latest product positions and advertising status:
- Shows current vs first position of the day
- Generates CSV reports
- Supports organic and advertised product filtering

```bash
# Show advertised products
python ad_tracker.py

# Show organic products
python ad_tracker.py --organic
```

## Directory Structure

```
py-wb-simple-analysis/
├── tracker.py          # Main tracking script
├── plot_positions.py   # Position visualization
├── ad_tracker.py       # Position reporting
├── ranks/             # Raw ranking data
├── analyses/          # Analysis results
├── plots/             # Position charts
└── reports/           # CSV reports
```

## Requirements
- Python 3.8+
- requests
- schedule
- matplotlib

## Installation
```bash
git clone https://github.com/teocci/py-wb-simple-analysis.git
cd py-wb-simple-analysis
pip install -r requirements.txt
```
