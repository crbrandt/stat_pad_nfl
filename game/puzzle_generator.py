"""
Puzzle generator for NFL StatPad Game
Generates daily puzzles with stat category and row criteria
"""
import random
import hashlib
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import json
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    STAT_CATEGORIES, NFL_TEAMS, DIVISIONS, CONFERENCES,
    POSITION_GROUPS, CRITERIA_TYPES, MIN_VALID_ANSWERS,
    TIMEZONE, RESET_HOUR, SUPER_BOWL_ERA_START, CURRENT_YEAR
)


def get_puzzle_date() -> date:
    """Get the current puzzle date based on PST timezone"""
    now = datetime.now(TIMEZONE)
    return now.date()


def get_date_seed(puzzle_date: Optional[date] = None) -> int:
    """
    Generate a deterministic seed from a date
    
    Args:
        puzzle_date: Date to generate seed for. Defaults to today.
        
    Returns:
        Integer seed for random number generator
    """
    if puzzle_date is None:
        puzzle_date = get_puzzle_date()
    
    # Create a hash from the date string
    date_str = puzzle_date.isoformat()
    hash_obj = hashlib.md5(date_str.encode())
    seed = int(hash_obj.hexdigest()[:8], 16)
    return seed


def generate_year_range(rng: random.Random, stat_type: str) -> Tuple[int, int]:
    """
    Generate a random year range for criteria
    
    Args:
        rng: Random number generator
        stat_type: Type of stat (affects year range)
        
    Returns:
        Tuple of (start_year, end_year)
    """
    # Different range sizes for variety
    range_sizes = [5, 10, 15, 20]
    range_size = rng.choice(range_sizes)
    
    # Ensure we have enough data (nfl_data_py starts around 1999)
    min_year = 1999
    max_year = CURRENT_YEAR
    
    # Random start year
    start_year = rng.randint(min_year, max_year - range_size)
    end_year = start_year + range_size
    
    return (start_year, end_year)


def generate_criteria(
    rng: random.Random,
    stat_category: str,
    stat_info: Dict,
    used_teams: set,
    used_positions: set,
    row_index: int
) -> Dict:
    """
    Generate criteria for a single row
    
    Args:
        rng: Random number generator
        stat_category: The stat being maximized
        stat_info: Info about the stat category
        used_teams: Set of already used teams
        used_positions: Set of already used positions
        row_index: Index of the current row (0-4)
        
    Returns:
        Dictionary with criteria for the row
    """
    eligible_positions = stat_info['eligible_positions']
    
    # Determine criteria type based on row index for variety
    # First row: usually just team + year
    # Later rows: more complex criteria
    
    criteria = {
        'team': None,
        'year_start': None,
        'year_end': None,
        'position': None,
        'division': None,
        'conference': None,
        'qualifier': None,
        'qualifier_type': None,  # 'same_season' or 'career'
    }
    
    # Always have a year range
    year_start, year_end = generate_year_range(rng, stat_info['type'])
    criteria['year_start'] = year_start
    criteria['year_end'] = year_end
    
    # Decide what additional criteria to add
    criteria_options = []
    
    # Team criteria (if not all teams used)
    available_teams = [t for t in NFL_TEAMS.keys() if t not in used_teams]
    if available_teams:
        criteria_options.append('team')
    
    # Position criteria (only if compatible with stat)
    available_positions = [p for p in eligible_positions if p not in used_positions]
    if available_positions and len(eligible_positions) > 1:
        criteria_options.append('position')
    
    # Division criteria
    criteria_options.append('division')
    
    # Conference criteria
    criteria_options.append('conference')
    
    # Select criteria type
    if row_index == 0:
        # First row: prefer team + year (simpler)
        if 'team' in criteria_options:
            selected = 'team'
        else:
            selected = rng.choice(criteria_options)
    else:
        # Later rows: random selection
        selected = rng.choice(criteria_options)
    
    # Apply selected criteria
    if selected == 'team':
        team = rng.choice(available_teams)
        criteria['team'] = team
        used_teams.add(team)
    elif selected == 'position':
        position = rng.choice(available_positions)
        criteria['position'] = position
        used_positions.add(position)
    elif selected == 'division':
        criteria['division'] = rng.choice(DIVISIONS)
    elif selected == 'conference':
        criteria['conference'] = rng.choice(CONFERENCES)
    
    # Occasionally add a qualifier (20% chance for rows 2-4)
    if row_index >= 2 and rng.random() < 0.2:
        qualifiers = [
            ('pro_bowl', 'same_season', 'Made Pro Bowl'),
            ('playoff', 'same_season', 'Made Playoffs'),
        ]
        qual = rng.choice(qualifiers)
        criteria['qualifier'] = qual[0]
        criteria['qualifier_type'] = qual[1]
        criteria['qualifier_display'] = qual[2]
    
    return criteria


def generate_puzzle(puzzle_date: Optional[date] = None, override: Optional[Dict] = None) -> Dict:
    """
    Generate a complete puzzle for a given date
    
    Args:
        puzzle_date: Date to generate puzzle for. Defaults to today.
        override: Optional override configuration
        
    Returns:
        Dictionary with puzzle configuration
    """
    if override:
        return override
    
    if puzzle_date is None:
        puzzle_date = get_puzzle_date()
    
    # Get deterministic random generator
    seed = get_date_seed(puzzle_date)
    rng = random.Random(seed)
    
    # Select stat category
    stat_keys = list(STAT_CATEGORIES.keys())
    stat_category = rng.choice(stat_keys)
    stat_info = STAT_CATEGORIES[stat_category]
    
    # Generate 5 rows of criteria
    rows = []
    used_teams = set()
    used_positions = set()
    
    for i in range(5):
        criteria = generate_criteria(
            rng, stat_category, stat_info,
            used_teams, used_positions, i
        )
        rows.append(criteria)
    
    puzzle = {
        'date': puzzle_date.isoformat(),
        'stat_category': stat_category,
        'stat_display': stat_info['display_name'],
        'stat_type': stat_info['type'],
        'stat_description': stat_info['description'],
        'rows': rows,
    }
    
    return puzzle


def format_criteria_display(criteria: Dict) -> str:
    """
    Format criteria for display in UI
    
    Args:
        criteria: Criteria dictionary
        
    Returns:
        Human-readable criteria string
    """
    parts = []
    
    if criteria.get('team'):
        team_info = NFL_TEAMS.get(criteria['team'], {})
        team_name = team_info.get('name', criteria['team'])
        parts.append(team_name)
    
    if criteria.get('position'):
        parts.append(criteria['position'])
    
    if criteria.get('division'):
        parts.append(criteria['division'])
    
    if criteria.get('conference'):
        parts.append(criteria['conference'])
    
    if criteria.get('year_start') and criteria.get('year_end'):
        parts.append(f"{criteria['year_start']}-{criteria['year_end']}")
    
    return ', '.join(parts)


def format_qualifier_display(criteria: Dict) -> Optional[str]:
    """
    Format qualifier for display
    
    Args:
        criteria: Criteria dictionary
        
    Returns:
        Qualifier display string or None
    """
    if criteria.get('qualifier_display'):
        qualifier_type = criteria.get('qualifier_type', 'same_season')
        type_label = 'SAME SEASON' if qualifier_type == 'same_season' else 'CAREER'
        return f"{criteria['qualifier_display']}\n{type_label}"
    return None


# Override storage
OVERRIDE_FILE = os.path.join(os.path.dirname(__file__), 'puzzle_overrides.json')


def load_overrides() -> Dict:
    """Load puzzle overrides from file"""
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_override(puzzle_date: date, puzzle_config: Dict):
    """Save a puzzle override"""
    overrides = load_overrides()
    overrides[puzzle_date.isoformat()] = puzzle_config
    with open(OVERRIDE_FILE, 'w') as f:
        json.dump(overrides, f, indent=2)


def get_override(puzzle_date: date) -> Optional[Dict]:
    """Get override for a specific date if it exists"""
    overrides = load_overrides()
    return overrides.get(puzzle_date.isoformat())


def get_daily_puzzle() -> Dict:
    """
    Get today's puzzle (with override support)
    
    Returns:
        Puzzle configuration dictionary
    """
    today = get_puzzle_date()
    
    # Check for override
    override = get_override(today)
    if override:
        return override
    
    # Generate puzzle
    return generate_puzzle(today)


if __name__ == "__main__":
    # Test puzzle generation
    print("Testing puzzle generator...")
    
    puzzle = get_daily_puzzle()
    print(f"\nDate: {puzzle['date']}")
    print(f"Category: {puzzle['stat_display']} ({puzzle['stat_type']})")
    print(f"\nRows:")
    for i, row in enumerate(puzzle['rows']):
        display = format_criteria_display(row)
        qualifier = format_qualifier_display(row)
        print(f"  {i+1}. {display}")
        if qualifier:
            print(f"     Qualifier: {qualifier}")