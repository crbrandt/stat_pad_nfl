"""
Scorer for NFL StatPad Game
Calculates scores, percentiles, and tiers
Uses Polars for data operations
"""
import polars as pl
from typing import Dict, List, Optional, Tuple
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TIER_THRESHOLDS, TIER_COLORS, TIER_EMOJIS
from game.validator import get_all_valid_players


def calculate_percentile(
    stat_value: float,
    all_values: pl.Series
) -> float:
    """
    Calculate percentile rank of a stat value
    
    Args:
        stat_value: The value to rank
        all_values: Series of all valid values (Polars)
        
    Returns:
        Percentile (0-100)
    """
    if len(all_values) == 0:
        return 0
    
    # Count how many values are less than or equal
    rank = (all_values <= stat_value).sum()
    percentile = (rank / len(all_values)) * 100
    
    return round(percentile, 1)


def get_tier(percentile: float) -> str:
    """
    Get tier name based on percentile
    
    Args:
        percentile: Percentile value (0-100)
        
    Returns:
        Tier name ('diamond', 'gold', 'silver', 'bronze', 'iron')
    """
    if percentile >= TIER_THRESHOLDS['diamond']:
        return 'diamond'
    elif percentile >= TIER_THRESHOLDS['gold']:
        return 'gold'
    elif percentile >= TIER_THRESHOLDS['silver']:
        return 'silver'
    elif percentile >= TIER_THRESHOLDS['bronze']:
        return 'bronze'
    else:
        return 'iron'


def get_tier_color(tier: str) -> str:
    """Get the color for a tier"""
    return TIER_COLORS.get(tier, TIER_COLORS['iron'])


def get_tier_emoji(tier: str) -> str:
    """Get the emoji for a tier"""
    return TIER_EMOJIS.get(tier, TIER_EMOJIS['iron'])


def score_submission(
    df: pl.DataFrame,
    player_data: Dict,
    stat_category: str,
    criteria: Dict
) -> Dict:
    """
    Score a player submission
    
    Args:
        df: Player database DataFrame (Polars)
        player_data: Validated player data
        stat_category: The stat category being maximized
        criteria: Row criteria
        
    Returns:
        Dictionary with score, percentile, tier info
    """
    stat_value = player_data['stat_value']
    
    # Get all valid players for this criteria
    valid_players = get_all_valid_players(df, stat_category, criteria)
    
    if len(valid_players) == 0:
        return {
            'score': stat_value,
            'percentile': 100,
            'tier': 'diamond',
            'tier_color': get_tier_color('diamond'),
            'tier_emoji': get_tier_emoji('diamond'),
            'rank': 1,
            'total_valid': 1,
        }
    
    # Calculate percentile
    all_values = valid_players[stat_category]
    percentile = calculate_percentile(stat_value, all_values)
    
    # Get tier
    tier = get_tier(percentile)
    
    # Calculate rank (count how many are greater + 1)
    rank = (all_values > stat_value).sum() + 1
    
    return {
        'score': stat_value,
        'percentile': percentile,
        'tier': tier,
        'tier_color': get_tier_color(tier),
        'tier_emoji': get_tier_emoji(tier),
        'rank': int(rank),
        'total_valid': len(valid_players),
    }


def get_top_5_for_criteria(
    df: pl.DataFrame,
    stat_category: str,
    criteria: Dict
) -> List[Dict]:
    """
    Get top 5 players for given criteria
    
    Args:
        df: Player database DataFrame (Polars)
        stat_category: The stat category being maximized
        criteria: Row criteria
        
    Returns:
        List of top 5 player dictionaries
    """
    valid_players = get_all_valid_players(df, stat_category, criteria)
    
    if len(valid_players) == 0:
        return []
    
    top_5 = valid_players.head(5)
    
    results = []
    for i, row in enumerate(top_5.iter_rows(named=True), 1):
        results.append({
            'rank': i,
            'player': row.get('player', 'Unknown'),
            'season': int(row['season']),
            'team': row.get('team', 'N/A'),
            'stat_value': float(row[stat_category]),
        })
    
    return results


def calculate_total_score(submissions: List[Dict]) -> float:
    """
    Calculate total score from all submissions
    
    Args:
        submissions: List of submission dictionaries
        
    Returns:
        Total score
    """
    return sum(s.get('score', 0) for s in submissions if s)


def generate_share_text(
    puzzle: Dict,
    submissions: List[Dict],
    total_score: float,
    app_url: str = "statpadnfl.streamlit.app"
) -> str:
    """
    Generate shareable text with emoji tiers
    
    Args:
        puzzle: Puzzle configuration
        submissions: List of scored submissions
        total_score: Total score
        app_url: URL to the app
        
    Returns:
        Shareable text string
    """
    # Get emojis for each submission
    emojis = []
    for sub in submissions:
        if sub and sub.get('tier'):
            emojis.append(get_tier_emoji(sub['tier']))
        else:
            emojis.append('⬛')  # Not submitted
    
    emoji_line = ''.join(emojis)
    
    # Format score
    score_str = f"{total_score:,.0f}" if total_score == int(total_score) else f"{total_score:,.1f}"
    
    # Build share text
    share_text = f"""🏈 NFL StatPad - {puzzle['date']}
Category: {puzzle['stat_display']}

{emoji_line}

Score: {score_str} pts
Play at: {app_url}"""
    
    return share_text


def get_game_summary(
    puzzle: Dict,
    submissions: List[Dict],
    df: pl.DataFrame
) -> Dict:
    """
    Get complete game summary
    
    Args:
        puzzle: Puzzle configuration
        submissions: List of scored submissions
        df: Player database DataFrame (Polars)
        
    Returns:
        Dictionary with game summary
    """
    stat_category = puzzle['stat_category']
    
    # Calculate totals
    total_score = calculate_total_score(submissions)
    completed_rows = sum(1 for s in submissions if s and s.get('score'))
    
    # Get top 5 for each row
    row_leaderboards = []
    for i, row_criteria in enumerate(puzzle['rows']):
        top_5 = get_top_5_for_criteria(df, stat_category, row_criteria)
        row_leaderboards.append(top_5)
    
    # Calculate max possible score
    max_score = sum(
        lb[0]['stat_value'] if lb else 0 
        for lb in row_leaderboards
    )
    
    # Calculate overall percentile
    if max_score > 0:
        overall_percentile = (total_score / max_score) * 100
    else:
        overall_percentile = 0
    
    return {
        'total_score': total_score,
        'max_score': max_score,
        'overall_percentile': round(overall_percentile, 1),
        'completed_rows': completed_rows,
        'total_rows': 5,
        'row_leaderboards': row_leaderboards,
        'submissions': submissions,
    }


if __name__ == "__main__":
    # Test scorer
    print("Testing scorer...")
    
    # Test tier calculation
    for pct in [100, 95, 85, 60, 30]:
        tier = get_tier(pct)
        emoji = get_tier_emoji(tier)
        color = get_tier_color(tier)
        print(f"{pct}% -> {tier} {emoji} ({color})")