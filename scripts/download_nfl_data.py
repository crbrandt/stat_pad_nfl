#!/usr/bin/env python3
"""
NFL Data Downloader
Downloads comprehensive NFL player statistics from nflverse GitHub releases
Covers 1999-2024 (nflverse data availability)

Usage:
    python scripts/download_nfl_data.py

Output:
    data/nfl_player_stats.parquet - Combined player statistics file
"""

import os
import sys
import requests
import polars as pl
from io import BytesIO
import time

# Configuration
START_YEAR = 1999  # nflverse data starts from 1999
END_YEAR = 2024    # Latest available
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'nfl_player_stats.parquet')

# nflverse data URLs
PLAYER_STATS_URL = "https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats_{year}.parquet"


def download_year_stats(year: int) -> pl.DataFrame:
    """Download player stats for a specific year"""
    url = PLAYER_STATS_URL.format(year=year)
    print(f"  Downloading {year}...", end=" ", flush=True)
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            df = pl.read_parquet(BytesIO(response.content))
            print(f"✓ {len(df)} records")
            return df
        else:
            print(f"✗ HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ {e}")
        return None


def process_data(df: pl.DataFrame) -> pl.DataFrame:
    """Process and standardize the downloaded data"""
    
    # Filter to regular season only
    if 'season_type' in df.columns:
        df = df.filter(pl.col('season_type') == 'REG')
    
    # Select and rename columns
    columns_to_keep = {
        'player_display_name': 'player',
        'recent_team': 'team',
        'position': 'position',
        'season': 'season',
        'completions': 'completions',
        'attempts': 'attempts',
        'passing_yards': 'passing_yards',
        'passing_tds': 'passing_tds',
        'interceptions': 'interceptions',
        'carries': 'rushing_attempts',
        'rushing_yards': 'rushing_yards',
        'rushing_tds': 'rushing_tds',
        'receptions': 'receptions',
        'targets': 'targets',
        'receiving_yards': 'receiving_yards',
        'receiving_tds': 'receiving_tds',
        'fantasy_points': 'fantasy_points_weekly',
        'fantasy_points_ppr': 'fantasy_points_ppr_weekly',
    }
    
    # Keep only columns that exist
    available_cols = [c for c in columns_to_keep.keys() if c in df.columns]
    df = df.select(available_cols)
    
    # Rename columns
    rename_map = {k: v for k, v in columns_to_keep.items() if k in df.columns}
    df = df.rename(rename_map)
    
    # Aggregate by player-season (sum weekly stats)
    group_cols = ['player', 'season']
    
    # Get numeric columns for aggregation
    numeric_cols = [c for c in df.columns if c not in group_cols and df[c].dtype in [pl.Float64, pl.Int64, pl.Float32, pl.Int32]]
    
    # For team and position, take the first value
    agg_exprs = [pl.col(c).sum().alias(c) for c in numeric_cols]
    
    # Add first value for team and position
    if 'team' in df.columns:
        agg_exprs.append(pl.col('team').first())
    if 'position' in df.columns:
        agg_exprs.append(pl.col('position').first())
    
    df = df.group_by(group_cols).agg(agg_exprs)
    
    return df


def calculate_fantasy_points(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate fantasy points using standard scoring"""
    
    # Standard scoring: 0.04 pts/pass yard, 4 pts/pass TD, -2 pts/INT
    # 0.1 pts/rush yard, 6 pts/rush TD
    # 0.1 pts/rec yard, 6 pts/rec TD
    
    fantasy_expr = pl.lit(0.0)
    
    if 'passing_yards' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('passing_yards').fill_null(0) * 0.04
    if 'passing_tds' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('passing_tds').fill_null(0) * 4
    if 'interceptions' in df.columns:
        fantasy_expr = fantasy_expr - pl.col('interceptions').fill_null(0) * 2
    if 'rushing_yards' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('rushing_yards').fill_null(0) * 0.1
    if 'rushing_tds' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('rushing_tds').fill_null(0) * 6
    if 'receiving_yards' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('receiving_yards').fill_null(0) * 0.1
    if 'receiving_tds' in df.columns:
        fantasy_expr = fantasy_expr + pl.col('receiving_tds').fill_null(0) * 6
    
    df = df.with_columns(fantasy_expr.round(1).alias('fantasy_points'))
    
    # PPR: Add 1 pt per reception
    ppr_expr = pl.col('fantasy_points')
    if 'receptions' in df.columns:
        ppr_expr = ppr_expr + pl.col('receptions').fill_null(0) * 1
    
    df = df.with_columns(ppr_expr.round(1).alias('fantasy_points_ppr'))
    
    return df


def calculate_passer_rating(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate NFL passer rating for QBs"""
    
    if not all(c in df.columns for c in ['completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions']):
        return df
    
    # NFL passer rating formula
    att = pl.col('attempts').fill_null(0)
    comp = pl.col('completions').fill_null(0)
    yards = pl.col('passing_yards').fill_null(0)
    tds = pl.col('passing_tds').fill_null(0)
    ints = pl.col('interceptions').fill_null(0)
    
    # Avoid division by zero
    att_safe = pl.when(att > 0).then(att).otherwise(1)
    
    a = ((comp / att_safe) - 0.3) * 5
    b = ((yards / att_safe) - 3) * 0.25
    c = (tds / att_safe) * 20
    d = 2.375 - ((ints / att_safe) * 25)
    
    # Clip values
    a = pl.when(a < 0).then(0).when(a > 2.375).then(2.375).otherwise(a)
    b = pl.when(b < 0).then(0).when(b > 2.375).then(2.375).otherwise(b)
    c = pl.when(c < 0).then(0).when(c > 2.375).then(2.375).otherwise(c)
    d = pl.when(d < 0).then(0).when(d > 2.375).then(2.375).otherwise(d)
    
    rating = ((a + b + c + d) / 6) * 100
    
    # Only calculate for players with attempts
    rating = pl.when(att > 0).then(rating.round(1)).otherwise(None)
    
    df = df.with_columns(rating.alias('passer_rating'))
    
    return df


def main():
    """Main function to download and combine NFL data"""
    print("=" * 60)
    print("NFL Data Downloader (using Polars)")
    print(f"Downloading nflverse data: {START_YEAR}-{END_YEAR}")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        df = download_year_stats(year)
        if df is not None:
            all_data.append(df)
        time.sleep(0.3)  # Small delay between requests
    
    if not all_data:
        print("ERROR: No data downloaded!")
        sys.exit(1)
    
    print("\nCombining data...")
    df = pl.concat(all_data, how='diagonal')
    print(f"  Raw records: {len(df):,}")
    
    print("Processing data...")
    df = process_data(df)
    print(f"  After aggregation: {len(df):,}")
    
    print("Calculating fantasy points...")
    df = calculate_fantasy_points(df)
    
    print("Calculating passer ratings...")
    df = calculate_passer_rating(df)
    
    # Select final columns in order
    final_columns = [
        'player', 'season', 'team', 'position',
        'completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions', 'passer_rating',
        'rushing_yards', 'rushing_tds', 'rushing_attempts',
        'receptions', 'receiving_yards', 'receiving_tds', 'targets',
        'fantasy_points', 'fantasy_points_ppr'
    ]
    
    # Keep only columns that exist
    final_columns = [c for c in final_columns if c in df.columns]
    df = df.select(final_columns)
    
    # Remove rows with no meaningful stats
    stat_cols = ['passing_yards', 'rushing_yards', 'receiving_yards']
    stat_cols = [c for c in stat_cols if c in df.columns]
    if stat_cols:
        filter_expr = pl.lit(False)
        for col in stat_cols:
            filter_expr = filter_expr | (pl.col(col).fill_null(0) > 0)
        df = df.filter(filter_expr)
    
    # Sort by season descending, then player
    df = df.sort(['season', 'player'], descending=[True, False])
    
    # Save to parquet
    print(f"\nSaving to {OUTPUT_FILE}...")
    df.write_parquet(OUTPUT_FILE)
    
    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Total records: {len(df):,}")
    print(f"Unique players: {df['player'].n_unique():,}")
    print(f"Seasons covered: {df['season'].min()}-{df['season'].max()}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")
    print(f"Output: {OUTPUT_FILE}")
    
    # Sample data
    print("\nSample records (2024):")
    sample = df.filter(pl.col('season') == 2024).head(10)
    print(sample)
    
    # Check for specific players
    print("\nVerifying key players:")
    test_players = ['Patrick Mahomes', 'Tom Brady', 'Larry Fitzgerald', 'Jerry Rice']
    for player in test_players:
        matches = df.filter(pl.col('player').str.contains(player))
        if len(matches) > 0:
            years = matches['season'].to_list()
            print(f"  ✓ {player}: {len(matches)} seasons ({min(years)}-{max(years)})")
        else:
            print(f"  ✗ {player}: NOT FOUND")


if __name__ == "__main__":
    main()