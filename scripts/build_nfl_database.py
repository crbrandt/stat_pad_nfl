#!/usr/bin/env python3
"""
NFL Database Builder Script
Scrapes comprehensive NFL player statistics from Pro Football Reference
Covers 1970-2025 (Super Bowl era through current season)

Usage:
    python scripts/build_nfl_database.py

Output:
    data/nfl_player_stats.parquet - Comprehensive player statistics file
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
START_YEAR = 1970  # Super Bowl era
END_YEAR = 2025    # Current completed season
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'nfl_player_stats.parquet')

# Rate limiting
REQUEST_DELAY = 3  # Seconds between requests to avoid rate limiting

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Team abbreviation mappings (historical to current)
TEAM_MAPPINGS = {
    'OAK': 'LV', 'RAI': 'LV',  # Raiders
    'SD': 'LAC', 'SDG': 'LAC',  # Chargers
    'STL': 'LAR', 'RAM': 'LAR',  # Rams
    'PHO': 'ARI', 'CRD': 'ARI',  # Cardinals
    'BOS': 'NE',  # Patriots
    'HOU': 'HOU',  # Texans (keep as is, different from Oilers)
    'HST': 'TEN',  # Oilers -> Titans
    'BAL': 'IND',  # Colts (pre-1984)
    '2TM': None, '3TM': None, '4TM': None,  # Multi-team seasons
}


def normalize_team(team: str) -> str:
    """Normalize team abbreviation to current name"""
    if pd.isna(team) or team is None:
        return None
    team = str(team).upper().strip()
    if team in TEAM_MAPPINGS:
        return TEAM_MAPPINGS[team]
    return team


def clean_player_name(name: str) -> str:
    """Clean player name, removing special characters"""
    if pd.isna(name):
        return None
    # Remove asterisks (Pro Bowl), plus signs (All-Pro), etc.
    name = str(name).replace('*', '').replace('+', '').strip()
    return name


def scrape_passing_stats(year: int) -> pd.DataFrame:
    """Scrape passing statistics for a given year"""
    url = f"https://www.pro-football-reference.com/years/{year}/passing.htm"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"    ⚠ Passing {year}: HTTP {response.status_code}")
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', {'id': 'passing'})
        if not table:
            print(f"    ⚠ Passing {year}: No table found")
            return pd.DataFrame()
        
        df = pd.read_html(str(table))[0]
        
        # Handle multi-level columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
        
        # Standardize column names
        df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
        
        # Remove header rows that got included as data
        df = df[df['player'].notna() & (df['player'] != 'Player')]
        
        df['season'] = year
        df['stat_type'] = 'passing'
        
        print(f"    ✓ Passing {year}: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"    ⚠ Passing {year}: {e}")
        return pd.DataFrame()


def scrape_rushing_stats(year: int) -> pd.DataFrame:
    """Scrape rushing statistics for a given year"""
    url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', {'id': 'rushing'})
        if not table:
            return pd.DataFrame()
        
        df = pd.read_html(str(table))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
        
        df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
        df = df[df['player'].notna() & (df['player'] != 'Player')]
        
        df['season'] = year
        df['stat_type'] = 'rushing'
        
        print(f"    ✓ Rushing {year}: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"    ⚠ Rushing {year}: {e}")
        return pd.DataFrame()


def scrape_receiving_stats(year: int) -> pd.DataFrame:
    """Scrape receiving statistics for a given year"""
    url = f"https://www.pro-football-reference.com/years/{year}/receiving.htm"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', {'id': 'receiving'})
        if not table:
            return pd.DataFrame()
        
        df = pd.read_html(str(table))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
        
        df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
        df = df[df['player'].notna() & (df['player'] != 'Player')]
        
        df['season'] = year
        df['stat_type'] = 'receiving'
        
        print(f"    ✓ Receiving {year}: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"    ⚠ Receiving {year}: {e}")
        return pd.DataFrame()


def scrape_defense_stats(year: int) -> pd.DataFrame:
    """Scrape defensive statistics for a given year"""
    url = f"https://www.pro-football-reference.com/years/{year}/defense.htm"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', {'id': 'defense'})
        if not table:
            return pd.DataFrame()
        
        df = pd.read_html(str(table))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
        
        df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
        df = df[df['player'].notna() & (df['player'] != 'Player')]
        
        df['season'] = year
        df['stat_type'] = 'defense'
        
        print(f"    ✓ Defense {year}: {len(df)} records")
        return df
        
    except Exception as e:
        print(f"    ⚠ Defense {year}: {e}")
        return pd.DataFrame()


def scrape_year(year: int) -> pd.DataFrame:
    """Scrape all stats for a given year"""
    print(f"  Scraping {year}...")
    
    dfs = []
    
    # Passing
    df_pass = scrape_passing_stats(year)
    if len(df_pass) > 0:
        dfs.append(df_pass)
    time.sleep(REQUEST_DELAY)
    
    # Rushing
    df_rush = scrape_rushing_stats(year)
    if len(df_rush) > 0:
        dfs.append(df_rush)
    time.sleep(REQUEST_DELAY)
    
    # Receiving
    df_rec = scrape_receiving_stats(year)
    if len(df_rec) > 0:
        dfs.append(df_rec)
    time.sleep(REQUEST_DELAY)
    
    # Defense
    df_def = scrape_defense_stats(year)
    if len(df_def) > 0:
        dfs.append(df_def)
    time.sleep(REQUEST_DELAY)
    
    if not dfs:
        return pd.DataFrame()
    
    return pd.concat(dfs, ignore_index=True)


def process_and_merge_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process and merge all stat types into unified player-season records"""
    
    # Clean player names
    df['player'] = df['player'].apply(clean_player_name)
    
    # Normalize team abbreviations
    if 'tm' in df.columns:
        df['team'] = df['tm'].apply(normalize_team)
    elif 'team' in df.columns:
        df['team'] = df['team'].apply(normalize_team)
    
    # Standardize position column
    if 'pos' in df.columns:
        df['position'] = df['pos'].str.upper()
    elif 'position' not in df.columns:
        df['position'] = None
    
    # Create unified records by player-season
    # Group by player, season, team and aggregate stats
    
    # First, let's identify the stat columns we care about
    stat_columns = {
        # Passing
        'cmp': 'completions',
        'att': 'attempts', 
        'yds': 'yards',
        'td': 'tds',
        'int': 'interceptions',
        'rate': 'passer_rating',
        'passing_yds': 'passing_yards',
        'passing_td': 'passing_tds',
        
        # Rushing
        'rushing_yds': 'rushing_yards',
        'rushing_td': 'rushing_tds',
        'rushing_att': 'rushing_attempts',
        
        # Receiving
        'rec': 'receptions',
        'receiving_yds': 'receiving_yards',
        'receiving_td': 'receiving_tds',
        'tgt': 'targets',
        
        # Defense
        'sk': 'sacks',
        'solo': 'tackles_solo',
        'ast': 'tackles_ast',
        'comb': 'tackles_total',
        'ff': 'forced_fumbles',
        'fr': 'fumble_recoveries',
        'def_int': 'interceptions_def',
    }
    
    # Rename columns
    for old, new in stat_columns.items():
        if old in df.columns and new not in df.columns:
            df[new] = pd.to_numeric(df[old], errors='coerce')
    
    # Convert numeric columns
    numeric_cols = ['completions', 'attempts', 'yards', 'tds', 'interceptions', 
                   'passer_rating', 'passing_yards', 'passing_tds',
                   'rushing_yards', 'rushing_tds', 'rushing_attempts',
                   'receptions', 'receiving_yards', 'receiving_tds', 'targets',
                   'sacks', 'tackles_solo', 'tackles_ast', 'tackles_total',
                   'forced_fumbles', 'fumble_recoveries', 'interceptions_def']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_fantasy_points(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate fantasy points for each player-season"""
    
    # Standard scoring
    df['fantasy_points'] = 0.0
    
    # Passing: 0.04 pts/yard, 4 pts/TD, -2 pts/INT
    if 'passing_yards' in df.columns:
        df['fantasy_points'] += df['passing_yards'].fillna(0) * 0.04
    if 'passing_tds' in df.columns:
        df['fantasy_points'] += df['passing_tds'].fillna(0) * 4
    if 'interceptions' in df.columns:
        df['fantasy_points'] -= df['interceptions'].fillna(0) * 2
    
    # Rushing: 0.1 pts/yard, 6 pts/TD
    if 'rushing_yards' in df.columns:
        df['fantasy_points'] += df['rushing_yards'].fillna(0) * 0.1
    if 'rushing_tds' in df.columns:
        df['fantasy_points'] += df['rushing_tds'].fillna(0) * 6
    
    # Receiving: 0.1 pts/yard, 6 pts/TD
    if 'receiving_yards' in df.columns:
        df['fantasy_points'] += df['receiving_yards'].fillna(0) * 0.1
    if 'receiving_tds' in df.columns:
        df['fantasy_points'] += df['receiving_tds'].fillna(0) * 6
    
    # PPR: Add 1 pt per reception
    df['fantasy_points_ppr'] = df['fantasy_points'].copy()
    if 'receptions' in df.columns:
        df['fantasy_points_ppr'] += df['receptions'].fillna(0) * 1
    
    # Round to 1 decimal
    df['fantasy_points'] = df['fantasy_points'].round(1)
    df['fantasy_points_ppr'] = df['fantasy_points_ppr'].round(1)
    
    return df


def main():
    """Main function to build the NFL database"""
    print("=" * 60)
    print("NFL Database Builder")
    print(f"Scraping Pro Football Reference: {START_YEAR}-{END_YEAR}")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        year_data = scrape_year(year)
        if len(year_data) > 0:
            all_data.append(year_data)
        
        # Progress update
        progress = (year - START_YEAR + 1) / (END_YEAR - START_YEAR + 1) * 100
        print(f"  Progress: {progress:.1f}%")
    
    if not all_data:
        print("ERROR: No data scraped!")
        sys.exit(1)
    
    print("\nProcessing data...")
    df = pd.concat(all_data, ignore_index=True)
    print(f"  Raw records: {len(df)}")
    
    # Process and clean
    df = process_and_merge_data(df)
    print(f"  After processing: {len(df)}")
    
    # Calculate fantasy points
    df = calculate_fantasy_points(df)
    
    # Select final columns
    final_columns = [
        'player', 'season', 'team', 'position', 'stat_type',
        'completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions', 'passer_rating',
        'rushing_yards', 'rushing_tds', 'rushing_attempts',
        'receptions', 'receiving_yards', 'receiving_tds', 'targets',
        'sacks', 'tackles_total', 'forced_fumbles', 'interceptions_def',
        'fantasy_points', 'fantasy_points_ppr'
    ]
    
    # Keep only columns that exist
    final_columns = [c for c in final_columns if c in df.columns]
    df = df[final_columns]
    
    # Remove duplicates (same player-season-stat_type)
    df = df.drop_duplicates(subset=['player', 'season', 'stat_type'], keep='first')
    
    # Save to parquet
    print(f"\nSaving to {OUTPUT_FILE}...")
    df.to_parquet(OUTPUT_FILE, index=False)
    
    # Summary
    print("\n" + "=" * 60)
    print("DATABASE BUILD COMPLETE")
    print("=" * 60)
    print(f"Total records: {len(df):,}")
    print(f"Unique players: {df['player'].nunique():,}")
    print(f"Seasons covered: {df['season'].min()}-{df['season'].max()}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")
    print(f"Output: {OUTPUT_FILE}")
    
    # Sample data
    print("\nSample records:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()