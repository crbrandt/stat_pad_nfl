"""
Validator for NFL StatPad Game
Validates player submissions against criteria including stat qualifiers
Uses Polars for data operations
"""
import polars as pl
from typing import Dict, List, Optional, Tuple
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    NFL_TEAMS, POSITION_GROUPS, STAT_CATEGORIES, 
    REVERSE_TEAM_MAPPINGS, TEAM_NAME_MAPPINGS, STAT_QUALIFIERS
)


def get_team_variants(team_abbr: str) -> List[str]:
    """Get all possible team abbreviation variants for a team"""
    if team_abbr in REVERSE_TEAM_MAPPINGS:
        return REVERSE_TEAM_MAPPINGS[team_abbr]
    return [team_abbr]


def normalize_team(team_abbr: str) -> str:
    """Normalize a team abbreviation to the standard config format"""
    if team_abbr in TEAM_NAME_MAPPINGS:
        return TEAM_NAME_MAPPINGS[team_abbr]
    return team_abbr


def check_threshold_qualifier(player_row: dict, qualifier_info: dict) -> Tuple[bool, str]:
    """
    Check if a player meets a threshold qualifier
    
    Returns:
        Tuple of (meets_qualifier, error_message)
    """
    column = qualifier_info.get('column')
    operator = qualifier_info.get('operator', '>=')
    value = qualifier_info.get('value', 0)
    display = qualifier_info.get('display', 'qualifier')
    
    player_value = player_row.get(column)
    
    if player_value is None:
        return False, f"No {column} data available"
    
    # Apply operator
    if operator == '>=':
        meets = player_value >= value
    elif operator == '>':
        meets = player_value > value
    elif operator == '<=':
        meets = player_value <= value
    elif operator == '<':
        meets = player_value < value
    elif operator == '==':
        meets = player_value == value
    else:
        meets = player_value >= value
    
    if not meets:
        return False, f"Does not meet {display} requirement ({player_value:.0f} {column})"
    
    return True, ""


def check_fantasy_rank_qualifier(
    df: pl.DataFrame, 
    player_row: dict, 
    qualifier_info: dict,
    year: int
) -> Tuple[bool, str]:
    """
    Check if a player meets a fantasy ranking qualifier
    
    Returns:
        Tuple of (meets_qualifier, error_message)
    """
    position = qualifier_info.get('position')
    rank_column = qualifier_info.get('rank_column', 'fantasy_points')
    max_rank = qualifier_info.get('max_rank')
    min_rank = qualifier_info.get('min_rank')
    display = qualifier_info.get('display', 'fantasy rank')
    
    player_name = player_row.get('player', '')
    player_position = player_row.get('position', '')
    
    # Get all players at this position for this year
    position_players = df.filter(
        (pl.col('season') == year) &
        (pl.col('position') == position) &
        (pl.col(rank_column).is_not_null()) &
        (pl.col(rank_column) > 0)
    ).sort(rank_column, descending=True)
    
    if len(position_players) == 0:
        return False, f"No {position} data for {year}"
    
    # Find player's rank
    player_rank = None
    for i, row in enumerate(position_players.iter_rows(named=True), 1):
        if row.get('player', '').lower() == player_name.lower():
            player_rank = i
            break
    
    if player_rank is None:
        # Player might be at a different position
        return False, f"{player_name} was not ranked as a {position} in {year}"
    
    # Check rank requirements
    if max_rank is not None and player_rank > max_rank:
        return False, f"{player_name} was #{player_rank} fantasy {position} in {year} (need Top {max_rank})"
    
    if min_rank is not None and player_rank < min_rank:
        return False, f"{player_name} was #{player_rank} fantasy {position} in {year} (need outside Top {min_rank - 1})"
    
    return True, ""


def validate_qualifier(
    df: pl.DataFrame,
    player_row: dict,
    qualifier_key: str,
    year: int
) -> Tuple[bool, str]:
    """
    Validate a player against a stat qualifier
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if qualifier_key not in STAT_QUALIFIERS:
        return True, ""  # Unknown qualifier, pass by default
    
    qualifier_info = STAT_QUALIFIERS[qualifier_key]
    qualifier_type = qualifier_info.get('type')
    
    if qualifier_type == 'threshold':
        return check_threshold_qualifier(player_row, qualifier_info)
    elif qualifier_type == 'fantasy_rank':
        return check_fantasy_rank_qualifier(df, player_row, qualifier_info, year)
    else:
        return True, ""  # Unknown type, pass by default


def validate_player_submission(
    df: pl.DataFrame,
    player_name: str,
    year: int,
    stat_category: str,
    criteria: Dict
) -> Tuple[bool, Optional[Dict], str]:
    """
    Validate a player submission against criteria
    
    Args:
        df: Player database DataFrame (Polars)
        player_name: Name of the player submitted
        year: Year submitted
        stat_category: The stat category being maximized
        criteria: Row criteria to validate against
        
    Returns:
        Tuple of (is_valid, player_data, error_message)
    """
    player_name = str(player_name).strip()
    
    # Find player in database
    player_name_lower = player_name.lower()
    player_matches = df.filter(
        (pl.col('player').str.to_lowercase().str.contains(player_name_lower)) &
        (pl.col('season') == year)
    )
    
    if len(player_matches) == 0:
        player_matches = df.filter(
            (pl.col('player').str.to_lowercase() == player_name_lower) &
            (pl.col('season') == year)
        )
    
    if len(player_matches) == 0:
        return False, None, f"Player '{player_name}' not found for year {year}"
    
    # Get the best match
    if stat_category in player_matches.columns:
        player_matches = player_matches.sort(stat_category, descending=True)
    
    player_row = player_matches.row(0, named=True)
    
    # Check if player has the stat
    stat_value = player_row.get(stat_category)
    if stat_value is None:
        return False, None, f"No {stat_category} data for {player_name} in {year}"
    
    if stat_value <= 0:
        return False, None, f"{player_name} has no {stat_category} in {year}"
    
    # Validate against team criteria
    if criteria.get('team'):
        player_team = player_row.get('team', '')
        valid_teams = get_team_variants(criteria['team'])
        if player_team not in valid_teams:
            team_name = NFL_TEAMS.get(criteria['team'], {}).get('name', criteria['team'])
            return False, None, f"{player_name} was not on {team_name} in {year}"
    
    # Check year range
    if criteria.get('year_start') and year < criteria['year_start']:
        return False, None, f"Year {year} is before {criteria['year_start']}"
    
    if criteria.get('year_end') and year > criteria['year_end']:
        return False, None, f"Year {year} is after {criteria['year_end']}"
    
    # Check position
    if criteria.get('position'):
        player_position = player_row.get('position', '')
        valid_positions = POSITION_GROUPS.get(criteria['position'], [criteria['position']])
        if player_position not in valid_positions:
            return False, None, f"{player_name} is not a {criteria['position']}"
    
    # Check division
    if criteria.get('division'):
        player_team = player_row.get('team', '')
        normalized_team = normalize_team(player_team)
        team_info = NFL_TEAMS.get(normalized_team, {})
        if team_info.get('division') != criteria['division']:
            return False, None, f"{player_name}'s team was not in {criteria['division']} in {year}"
    
    # Check conference
    if criteria.get('conference'):
        player_team = player_row.get('team', '')
        normalized_team = normalize_team(player_team)
        team_info = NFL_TEAMS.get(normalized_team, {})
        team_division = team_info.get('division', '')
        if criteria['conference'] not in team_division:
            return False, None, f"{player_name}'s team was not in {criteria['conference']} in {year}"
    
    # Check stat qualifier and get qualifier value
    qualifier_value = None
    if criteria.get('qualifier'):
        is_valid, error_msg = validate_qualifier(df, player_row, criteria['qualifier'], year)
        if not is_valid:
            return False, None, error_msg
        
        # Get the qualifier value for display
        qualifier_info = STAT_QUALIFIERS.get(criteria['qualifier'], {})
        qualifier_column = qualifier_info.get('column')
        if qualifier_column and qualifier_column in player_row:
            qualifier_value = player_row.get(qualifier_column)
    
    # Build player data response
    player_data = {
        'player': player_row.get('player', player_name),
        'season': int(year),
        'team': player_row.get('team', 'N/A'),
        'position': player_row.get('position', 'N/A'),
        'stat_value': float(stat_value),
        'player_id': player_row.get('player_id'),
        'espn_id': player_row.get('espn_id'),
        'headshot_url': player_row.get('headshot_url'),
        'qualifier_value': qualifier_value,
    }
    
    return True, player_data, ""


def find_player_best_year(
    df: pl.DataFrame,
    player_name: str,
    stat_category: str,
    criteria: Dict
) -> Optional[Dict]:
    """Find the best year for a player given criteria (for Easy Mode)"""
    player_matches = df.filter(
        pl.col('player').str.to_lowercase().str.contains(player_name.lower())
    )
    
    if len(player_matches) == 0:
        return None
    
    # Apply criteria filters
    if criteria.get('year_start'):
        player_matches = player_matches.filter(pl.col('season') >= criteria['year_start'])
    
    if criteria.get('year_end'):
        player_matches = player_matches.filter(pl.col('season') <= criteria['year_end'])
    
    if criteria.get('team'):
        valid_teams = get_team_variants(criteria['team'])
        player_matches = player_matches.filter(pl.col('team').is_in(valid_teams))
    
    if criteria.get('position'):
        valid_positions = POSITION_GROUPS.get(criteria['position'], [criteria['position']])
        player_matches = player_matches.filter(pl.col('position').is_in(valid_positions))
    
    if criteria.get('division'):
        teams_in_div = [abbr for abbr, info in NFL_TEAMS.items() 
                       if info.get('division') == criteria['division']]
        player_matches = player_matches.filter(pl.col('team').is_in(teams_in_div))
    
    if criteria.get('conference'):
        teams_in_conf = [abbr for abbr, info in NFL_TEAMS.items() 
                        if criteria['conference'] in info.get('division', '')]
        player_matches = player_matches.filter(pl.col('team').is_in(teams_in_conf))
    
    # Filter by stat existence
    if stat_category in player_matches.columns:
        player_matches = player_matches.filter(
            pl.col(stat_category).is_not_null() & 
            (pl.col(stat_category) > 0)
        )
    else:
        return None
    
    if len(player_matches) == 0:
        return None
    
    # For qualifier-based criteria, filter to years that meet the qualifier
    if criteria.get('qualifier'):
        valid_rows = []
        for row in player_matches.iter_rows(named=True):
            is_valid, _ = validate_qualifier(df, row, criteria['qualifier'], row['season'])
            if is_valid:
                valid_rows.append(row)
        
        if not valid_rows:
            return None
        
        # Sort by stat value and get best
        valid_rows.sort(key=lambda x: x.get(stat_category, 0), reverse=True)
        best_row = valid_rows[0]
    else:
        # Get best year (sort by stat descending, take first)
        best_row = player_matches.sort(stat_category, descending=True).row(0, named=True)
    
    return {
        'player': best_row.get('player', player_name),
        'season': int(best_row['season']),
        'team': best_row.get('team', 'N/A'),
        'position': best_row.get('position', 'N/A'),
        'stat_value': float(best_row[stat_category]),
        'player_id': best_row.get('player_id'),
        'espn_id': best_row.get('espn_id'),
        'headshot_url': best_row.get('headshot_url'),
    }


def search_players(
    df: pl.DataFrame,
    query: str,
    stat_category: str,
    criteria: Dict,
    limit: int = 10
) -> List[Dict]:
    """Search for players matching a query and criteria"""
    if not query or len(query) < 2:
        return []
    
    matches = df.filter(
        pl.col('player').str.to_lowercase().str.contains(query.lower())
    )
    
    # Apply criteria filters
    if criteria.get('year_start'):
        matches = matches.filter(pl.col('season') >= criteria['year_start'])
    
    if criteria.get('year_end'):
        matches = matches.filter(pl.col('season') <= criteria['year_end'])
    
    if criteria.get('team'):
        matches = matches.filter(pl.col('team') == criteria['team'])
    
    if criteria.get('position'):
        valid_positions = POSITION_GROUPS.get(criteria['position'], [criteria['position']])
        matches = matches.filter(pl.col('position').is_in(valid_positions))
    
    if criteria.get('division'):
        teams_in_div = [abbr for abbr, info in NFL_TEAMS.items() 
                       if info.get('division') == criteria['division']]
        matches = matches.filter(pl.col('team').is_in(teams_in_div))
    
    if criteria.get('conference'):
        teams_in_conf = [abbr for abbr, info in NFL_TEAMS.items() 
                        if criteria['conference'] in info.get('division', '')]
        matches = matches.filter(pl.col('team').is_in(teams_in_conf))
    
    # Filter by stat existence
    if stat_category in matches.columns:
        matches = matches.filter(
            pl.col(stat_category).is_not_null() & 
            (pl.col(stat_category) > 0)
        )
    
    if len(matches) == 0:
        return []
    
    # Get unique players with their best stat
    matches = matches.sort(stat_category, descending=True)
    seen_players = set()
    results = []
    
    for row in matches.iter_rows(named=True):
        player = row.get('player', '')
        if player.lower() not in seen_players:
            seen_players.add(player.lower())
            results.append({
                'player': player,
                'season': int(row['season']),
                'team': row.get('team', 'N/A'),
                'position': row.get('position', 'N/A'),
                'stat_value': float(row[stat_category]),
            })
            if len(results) >= limit:
                break
    
    return results


def get_all_valid_players(
    df: pl.DataFrame,
    stat_category: str,
    criteria: Dict
) -> pl.DataFrame:
    """Get all valid player-year combinations for criteria"""
    result = df
    
    # Filter by stat existence
    if stat_category in result.columns:
        result = result.filter(
            pl.col(stat_category).is_not_null() & 
            (pl.col(stat_category) > 0)
        )
    else:
        return pl.DataFrame()
    
    # Apply criteria filters
    if criteria.get('year_start'):
        result = result.filter(pl.col('season') >= criteria['year_start'])
    
    if criteria.get('year_end'):
        result = result.filter(pl.col('season') <= criteria['year_end'])
    
    if criteria.get('team'):
        result = result.filter(pl.col('team') == criteria['team'])
    
    if criteria.get('position'):
        valid_positions = POSITION_GROUPS.get(criteria['position'], [criteria['position']])
        result = result.filter(pl.col('position').is_in(valid_positions))
    
    if criteria.get('division'):
        teams_in_div = [abbr for abbr, info in NFL_TEAMS.items() 
                       if info.get('division') == criteria['division']]
        result = result.filter(pl.col('team').is_in(teams_in_div))
    
    if criteria.get('conference'):
        teams_in_conf = [abbr for abbr, info in NFL_TEAMS.items() 
                        if criteria['conference'] in info.get('division', '')]
        result = result.filter(pl.col('team').is_in(teams_in_conf))
    
    # For qualifier-based criteria, filter to rows that meet the qualifier
    if criteria.get('qualifier'):
        valid_indices = []
        for i, row in enumerate(result.iter_rows(named=True)):
            is_valid, _ = validate_qualifier(df, row, criteria['qualifier'], row['season'])
            if is_valid:
                valid_indices.append(i)
        
        if valid_indices:
            result = result[valid_indices]
        else:
            return pl.DataFrame()
    
    # Sort by stat value
    result = result.sort(stat_category, descending=True)
    
    return result