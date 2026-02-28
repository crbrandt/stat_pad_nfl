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
    TIMEZONE, RESET_HOUR, SUPER_BOWL_ERA_START, CURRENT_YEAR,
    STAT_QUALIFIERS, get_compatible_qualifiers
)


def get_puzzle_date() -> date:
    """Get the current puzzle date based on PST timezone"""
    now = datetime.now(TIMEZONE)
    return now.date()


def get_date_seed(puzzle_date: Optional[date] = None) -> int:
    """Generate a deterministic seed from a date"""
    if puzzle_date is None:
        puzzle_date = get_puzzle_date()
    
    date_str = puzzle_date.isoformat()
    hash_obj = hashlib.md5(date_str.encode())
    seed = int(hash_obj.hexdigest()[:8], 16)
    return seed


def generate_year_range(rng: random.Random, stat_type: str) -> Tuple[int, int]:
    """Generate a random year range for criteria"""
    range_sizes = [5, 10, 15, 20]
    range_size = rng.choice(range_sizes)
    
    min_year = 1999
    max_year = CURRENT_YEAR
    
    start_year = rng.randint(min_year, max_year - range_size)
    end_year = start_year + range_size
    
    return (start_year, end_year)


def generate_criteria(
    rng: random.Random,
    stat_category: str,
    stat_info: Dict,
    used_teams: set,
    used_positions: set,
    used_qualifiers: set,
    row_index: int,
    force_type: Optional[str] = None
) -> Dict:
    """
    Generate criteria for a single row
    
    Args:
        rng: Random number generator
        stat_category: The stat being maximized
        stat_info: Info about the stat category
        used_teams: Set of already used teams
        used_positions: Set of already used positions
        used_qualifiers: Set of already used qualifiers
        row_index: Index of the current row (0-4)
        force_type: Force a specific criteria type ('team_based' or 'qualifier')
    """
    eligible_positions = stat_info['eligible_positions']
    
    criteria = {
        'team': None,
        'year_start': None,
        'year_end': None,
        'position': None,
        'division': None,
        'conference': None,
        'qualifier': None,
        'qualifier_type': None,
        'qualifier_display': None,
    }
    
    # Always have a year range
    year_start, year_end = generate_year_range(rng, stat_info['type'])
    criteria['year_start'] = year_start
    criteria['year_end'] = year_end
    
    # Get compatible qualifiers for this stat category
    compatible_qualifiers = get_compatible_qualifiers(stat_category)
    available_qualifiers = [q for q in compatible_qualifiers if q not in used_qualifiers]
    
    # Determine if this row should use a stat qualifier or team-based criteria
    use_qualifier = False
    
    if force_type == 'qualifier':
        use_qualifier = True
    elif force_type == 'team_based':
        use_qualifier = False
    else:
        # Default logic: rows 2-4 have 40% chance of using a qualifier
        if row_index >= 1 and available_qualifiers and rng.random() < 0.4:
            use_qualifier = True
    
    if use_qualifier and available_qualifiers:
        # Select a stat qualifier
        qualifier_key = rng.choice(available_qualifiers)
        qualifier_info = STAT_QUALIFIERS[qualifier_key]
        
        criteria['qualifier'] = qualifier_key
        criteria['qualifier_type'] = qualifier_info.get('qualifier_type', 'same_season')
        criteria['qualifier_display'] = qualifier_info.get('display', qualifier_key)
        used_qualifiers.add(qualifier_key)
        
    else:
        # Use team-based criteria
        criteria_options = []
        
        # Team criteria
        available_teams = [t for t in NFL_TEAMS.keys() if t not in used_teams]
        if available_teams:
            criteria_options.append('team')
        
        # Division criteria
        criteria_options.append('division')
        
        # Conference criteria
        criteria_options.append('conference')
        
        # Position criteria (only if compatible with stat and multiple positions)
        available_positions = [p for p in eligible_positions if p not in used_positions]
        if available_positions and len(eligible_positions) > 1:
            criteria_options.append('position')
        
        # Select criteria type
        if row_index == 0:
            # First row: prefer team (simpler start)
            if 'team' in criteria_options:
                selected = 'team'
            else:
                selected = rng.choice(criteria_options)
        else:
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
    
    return criteria


def generate_puzzle(puzzle_date: Optional[date] = None, override: Optional[Dict] = None) -> Dict:
    """Generate a complete puzzle for a given date"""
    if override:
        return override
    
    if puzzle_date is None:
        puzzle_date = get_puzzle_date()
    
    seed = get_date_seed(puzzle_date)
    rng = random.Random(seed)
    
    # Select stat category
    stat_keys = list(STAT_CATEGORIES.keys())
    stat_category = rng.choice(stat_keys)
    stat_info = STAT_CATEGORIES[stat_category]
    
    # Determine puzzle structure:
    # - 2-3 team-based rows
    # - 2-3 qualifier-based rows
    # This ensures variety in every puzzle
    
    num_qualifier_rows = rng.choice([2, 2, 3])  # Weighted towards 2
    num_team_rows = 5 - num_qualifier_rows
    
    # Shuffle which rows get qualifiers
    row_types = ['team_based'] * num_team_rows + ['qualifier'] * num_qualifier_rows
    rng.shuffle(row_types)
    
    # But always make row 0 team-based for a simpler start
    if row_types[0] == 'qualifier':
        # Find first team_based and swap
        for i in range(1, 5):
            if row_types[i] == 'team_based':
                row_types[0], row_types[i] = row_types[i], row_types[0]
                break
    
    # Generate 5 rows of criteria
    rows = []
    used_teams = set()
    used_positions = set()
    used_qualifiers = set()
    
    for i in range(5):
        criteria = generate_criteria(
            rng, stat_category, stat_info,
            used_teams, used_positions, used_qualifiers, i,
            force_type=row_types[i]
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
    """Format criteria for display in UI"""
    parts = []
    
    # Qualifier takes precedence in display
    if criteria.get('qualifier_display'):
        parts.append(criteria['qualifier_display'])
    
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
    """Format qualifier for display"""
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
    """Get today's puzzle (with override support)"""
    today = get_puzzle_date()
    
    # Check for override
    override = get_override(today)
    if override:
        return override
    
    # Generate puzzle
    return generate_puzzle(today)


def update_puzzle_row(puzzle_date: date, row_index: int, new_criteria: Dict) -> Dict:
    """
    Update a single row in a puzzle without affecting other rows.
    If no override exists, creates one from the generated puzzle.
    
    Args:
        puzzle_date: The date of the puzzle to update
        row_index: Index of the row to update (0-4)
        new_criteria: New criteria for the row
    
    Returns:
        The updated puzzle config
    """
    # Get existing override or generate the puzzle
    existing = get_override(puzzle_date)
    if existing:
        puzzle = existing.copy()
        puzzle['rows'] = existing['rows'].copy()
    else:
        puzzle = generate_puzzle(puzzle_date)
    
    # Update the specific row
    if 0 <= row_index < len(puzzle['rows']):
        puzzle['rows'][row_index] = new_criteria
    
    # Save as override
    save_override(puzzle_date, puzzle)
    
    return puzzle


def get_current_puzzle_for_editing(puzzle_date: date = None) -> Dict:
    """
    Get the current puzzle for editing purposes.
    Returns the override if it exists, otherwise the generated puzzle.
    """
    if puzzle_date is None:
        puzzle_date = get_puzzle_date()
    
    override = get_override(puzzle_date)
    if override:
        return override
    
    return generate_puzzle(puzzle_date)


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