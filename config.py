"""
Configuration settings for NFL StatPad Game
"""
from datetime import datetime
import pytz

# Game Settings
GAME_NAME = "NFL StatPad"
SUPER_BOWL_ERA_START = 1966
CURRENT_YEAR = 2024

# Timezone for daily reset
TIMEZONE = pytz.timezone('America/Los_Angeles')  # PST/PDT
RESET_HOUR = 0  # Midnight

# Stat Categories with display names and eligible positions
STAT_CATEGORIES = {
    'passing_yards': {
        'display_name': 'PASS YDS',
        'type': 'PASSING',
        'eligible_positions': ['QB'],
        'description': 'Passing Yards'
    },
    'passing_tds': {
        'display_name': 'PASS TD',
        'type': 'PASSING',
        'eligible_positions': ['QB'],
        'description': 'Passing Touchdowns'
    },
    'completions': {
        'display_name': 'COMP',
        'type': 'PASSING',
        'eligible_positions': ['QB'],
        'description': 'Completions'
    },
    'passer_rating': {
        'display_name': 'RTG',
        'type': 'PASSING',
        'eligible_positions': ['QB'],
        'description': 'Passer Rating'
    },
    'rushing_yards': {
        'display_name': 'RUSH YDS',
        'type': 'RUSHING',
        'eligible_positions': ['QB', 'RB', 'WR', 'FB'],
        'description': 'Rushing Yards'
    },
    'rushing_tds': {
        'display_name': 'RUSH TD',
        'type': 'RUSHING',
        'eligible_positions': ['QB', 'RB', 'WR', 'FB'],
        'description': 'Rushing Touchdowns'
    },
    'rushing_attempts': {
        'display_name': 'RUSH ATT',
        'type': 'RUSHING',
        'eligible_positions': ['QB', 'RB', 'WR', 'FB'],
        'description': 'Rushing Attempts'
    },
    'receiving_yards': {
        'display_name': 'REC YDS',
        'type': 'RECEIVING',
        'eligible_positions': ['WR', 'TE', 'RB', 'FB'],
        'description': 'Receiving Yards'
    },
    'receiving_tds': {
        'display_name': 'REC TD',
        'type': 'RECEIVING',
        'eligible_positions': ['WR', 'TE', 'RB', 'FB'],
        'description': 'Receiving Touchdowns'
    },
    'receptions': {
        'display_name': 'REC',
        'type': 'RECEIVING',
        'eligible_positions': ['WR', 'TE', 'RB', 'FB'],
        'description': 'Receptions'
    },
    'sacks': {
        'display_name': 'SACKS',
        'type': 'DEFENSE',
        'eligible_positions': ['DE', 'DT', 'LB', 'OLB', 'ILB', 'MLB', 'EDGE'],
        'description': 'Sacks'
    },
    'interceptions': {
        'display_name': 'INT',
        'type': 'DEFENSE',
        'eligible_positions': ['CB', 'S', 'FS', 'SS', 'DB', 'LB', 'OLB', 'ILB', 'MLB'],
        'description': 'Interceptions'
    },
    'tackles_total': {
        'display_name': 'TACKLES',
        'type': 'DEFENSE',
        'eligible_positions': ['CB', 'S', 'FS', 'SS', 'DB', 'LB', 'OLB', 'ILB', 'MLB', 'DE', 'DT'],
        'description': 'Total Tackles'
    },
    'forced_fumbles': {
        'display_name': 'FF',
        'type': 'DEFENSE',
        'eligible_positions': ['CB', 'S', 'FS', 'SS', 'DB', 'LB', 'OLB', 'ILB', 'MLB', 'DE', 'DT'],
        'description': 'Forced Fumbles'
    },
    'fantasy_points': {
        'display_name': 'FPTS',
        'type': 'FANTASY',
        'eligible_positions': ['QB', 'RB', 'WR', 'TE', 'FB'],
        'description': 'Fantasy Points (Standard)'
    },
    'fantasy_points_ppr': {
        'display_name': 'FPTS PPR',
        'type': 'FANTASY',
        'eligible_positions': ['QB', 'RB', 'WR', 'TE', 'FB'],
        'description': 'Fantasy Points (PPR)'
    }
}

# Tier thresholds (percentile-based)
TIER_THRESHOLDS = {
    'diamond': 100,    # Exactly 100th percentile (best answer)
    'gold': 90,        # 90-99th percentile
    'silver': 75,      # 75-89th percentile
    'bronze': 50,      # 50-74th percentile
    'iron': 0          # Below 50th percentile
}

# Tier colors for UI
TIER_COLORS = {
    'diamond': '#3B82F6',   # Blue
    'gold': '#F59E0B',      # Gold/Yellow
    'silver': '#9CA3AF',    # Silver/Gray
    'bronze': '#CD7F32',    # Bronze
    'iron': '#374151'       # Dark gray
}

# Tier emojis for sharing
TIER_EMOJIS = {
    'diamond': '🟦',
    'gold': '🟨',
    'silver': '⬜',
    'bronze': '🟫',
    'iron': '⬛'
}

# NFL Teams with abbreviations and divisions
NFL_TEAMS = {
    'ARI': {'name': 'Arizona Cardinals', 'division': 'NFC West'},
    'ATL': {'name': 'Atlanta Falcons', 'division': 'NFC South'},
    'BAL': {'name': 'Baltimore Ravens', 'division': 'AFC North'},
    'BUF': {'name': 'Buffalo Bills', 'division': 'AFC East'},
    'CAR': {'name': 'Carolina Panthers', 'division': 'NFC South'},
    'CHI': {'name': 'Chicago Bears', 'division': 'NFC North'},
    'CIN': {'name': 'Cincinnati Bengals', 'division': 'AFC North'},
    'CLE': {'name': 'Cleveland Browns', 'division': 'AFC North'},
    'DAL': {'name': 'Dallas Cowboys', 'division': 'NFC East'},
    'DEN': {'name': 'Denver Broncos', 'division': 'AFC West'},
    'DET': {'name': 'Detroit Lions', 'division': 'NFC North'},
    'GB': {'name': 'Green Bay Packers', 'division': 'NFC North'},
    'HOU': {'name': 'Houston Texans', 'division': 'AFC South'},
    'IND': {'name': 'Indianapolis Colts', 'division': 'AFC South'},
    'JAX': {'name': 'Jacksonville Jaguars', 'division': 'AFC South'},
    'KC': {'name': 'Kansas City Chiefs', 'division': 'AFC West'},
    'LAC': {'name': 'Los Angeles Chargers', 'division': 'AFC West'},
    'LAR': {'name': 'Los Angeles Rams', 'division': 'NFC West'},
    'LV': {'name': 'Las Vegas Raiders', 'division': 'AFC West'},
    'MIA': {'name': 'Miami Dolphins', 'division': 'AFC East'},
    'MIN': {'name': 'Minnesota Vikings', 'division': 'NFC North'},
    'NE': {'name': 'New England Patriots', 'division': 'AFC East'},
    'NO': {'name': 'New Orleans Saints', 'division': 'NFC South'},
    'NYG': {'name': 'New York Giants', 'division': 'NFC East'},
    'NYJ': {'name': 'New York Jets', 'division': 'AFC East'},
    'PHI': {'name': 'Philadelphia Eagles', 'division': 'NFC East'},
    'PIT': {'name': 'Pittsburgh Steelers', 'division': 'AFC North'},
    'SEA': {'name': 'Seattle Seahawks', 'division': 'NFC West'},
    'SF': {'name': 'San Francisco 49ers', 'division': 'NFC West'},
    'TB': {'name': 'Tampa Bay Buccaneers', 'division': 'NFC South'},
    'TEN': {'name': 'Tennessee Titans', 'division': 'AFC South'},
    'WAS': {'name': 'Washington Commanders', 'division': 'NFC East'},
}

# Historical team name mappings (for older data)
# Maps data abbreviations to config abbreviations
TEAM_NAME_MAPPINGS = {
    'OAK': 'LV',      # Oakland Raiders -> Las Vegas Raiders
    'SD': 'LAC',      # San Diego Chargers -> LA Chargers
    'STL': 'LAR',     # St. Louis Rams -> LA Rams
    'PHO': 'ARI',     # Phoenix Cardinals -> Arizona Cardinals
    'RAI': 'LV',      # Raiders alternate
    'RAM': 'LAR',     # Rams alternate
    'LA': 'LAR',      # LA Rams (data uses LA, config uses LAR)
}

# Reverse mappings (config abbreviations to data abbreviations)
REVERSE_TEAM_MAPPINGS = {
    'LV': ['LV', 'OAK', 'RAI'],      # Las Vegas Raiders (was Oakland)
    'LAC': ['LAC', 'SD'],             # LA Chargers (was San Diego)
    'LAR': ['LAR', 'LA', 'STL', 'RAM'],  # LA Rams (was St. Louis, data uses LA)
    'ARI': ['ARI', 'PHO'],            # Arizona Cardinals (was Phoenix)
}

# Divisions for criteria
DIVISIONS = [
    'AFC East', 'AFC North', 'AFC South', 'AFC West',
    'NFC East', 'NFC North', 'NFC South', 'NFC West'
]

# Conferences
CONFERENCES = ['AFC', 'NFC']

# Position groups for criteria
POSITION_GROUPS = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE'],
    'OL': ['OT', 'OG', 'C', 'T', 'G'],
    'DL': ['DE', 'DT', 'NT'],
    'LB': ['LB', 'OLB', 'ILB', 'MLB', 'EDGE'],
    'DB': ['CB', 'S', 'FS', 'SS', 'DB'],
    'K': ['K'],
    'P': ['P'],
}

# Criteria types for puzzle generation
CRITERIA_TYPES = [
    'team',           # Player was on specific team
    'year_range',     # Player played in year range
    'position',       # Player position
    'division',       # Player's team division
    'conference',     # Player's team conference
    'pro_bowl',       # Made Pro Bowl (same season or career)
    'playoff',        # Made playoffs (same season)
]

# Minimum valid answers per row
MIN_VALID_ANSWERS = 12

# =============================================================================
# STAT QUALIFIERS - Creative criteria for puzzle variety
# =============================================================================

# Qualifier types:
# - 'threshold': Compare a stat against a value (>, <, >=, <=, ==)
# - 'fantasy_rank': Player's fantasy ranking at their position
# - 'career': Career-based qualifier (checked across all seasons)

STAT_QUALIFIERS = {
    # =========================================================================
    # FANTASY RANKING QUALIFIERS (same season)
    # =========================================================================
    'fantasy_top_5_qb': {
        'display': 'Top 5 Fantasy QB',
        'type': 'fantasy_rank',
        'position': 'QB',
        'rank_column': 'fantasy_points',
        'max_rank': 5,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['PASSING', 'RUSHING', 'FANTASY'],
    },
    'fantasy_top_10_qb': {
        'display': 'Top 10 Fantasy QB',
        'type': 'fantasy_rank',
        'position': 'QB',
        'rank_column': 'fantasy_points',
        'max_rank': 10,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['PASSING', 'RUSHING', 'FANTASY'],
    },
    'fantasy_outside_top_10_qb': {
        'display': 'Outside Top 10 Fantasy QB',
        'type': 'fantasy_rank',
        'position': 'QB',
        'rank_column': 'fantasy_points',
        'min_rank': 11,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['PASSING', 'RUSHING', 'FANTASY'],
    },
    'fantasy_top_5_rb': {
        'display': 'Top 5 Fantasy RB',
        'type': 'fantasy_rank',
        'position': 'RB',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 5,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RUSHING', 'RECEIVING', 'FANTASY'],
    },
    'fantasy_top_10_rb': {
        'display': 'Top 10 Fantasy RB',
        'type': 'fantasy_rank',
        'position': 'RB',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 10,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RUSHING', 'RECEIVING', 'FANTASY'],
    },
    'fantasy_outside_top_10_rb': {
        'display': 'Outside Top 10 Fantasy RB',
        'type': 'fantasy_rank',
        'position': 'RB',
        'rank_column': 'fantasy_points_ppr',
        'min_rank': 11,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RUSHING', 'RECEIVING', 'FANTASY'],
    },
    'fantasy_top_5_wr': {
        'display': 'Top 5 Fantasy WR',
        'type': 'fantasy_rank',
        'position': 'WR',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 5,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RECEIVING', 'FANTASY'],
    },
    'fantasy_top_10_wr': {
        'display': 'Top 10 Fantasy WR',
        'type': 'fantasy_rank',
        'position': 'WR',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 10,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RECEIVING', 'FANTASY'],
    },
    'fantasy_outside_top_10_wr': {
        'display': 'Outside Top 10 Fantasy WR',
        'type': 'fantasy_rank',
        'position': 'WR',
        'rank_column': 'fantasy_points_ppr',
        'min_rank': 11,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RECEIVING', 'FANTASY'],
    },
    'fantasy_top_5_te': {
        'display': 'Top 5 Fantasy TE',
        'type': 'fantasy_rank',
        'position': 'TE',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 5,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RECEIVING', 'FANTASY'],
    },
    'fantasy_top_10_te': {
        'display': 'Top 10 Fantasy TE',
        'type': 'fantasy_rank',
        'position': 'TE',
        'rank_column': 'fantasy_points_ppr',
        'max_rank': 10,
        'qualifier_type': 'same_season',
        'eligible_stat_types': ['RECEIVING', 'FANTASY'],
    },
    
    # =========================================================================
    # STAT THRESHOLD QUALIFIERS - QB specific (same season)
    # =========================================================================
    'qb_300_rush_yards': {
        'display': '300+ Rush Yards',
        'type': 'threshold',
        'column': 'rushing_yards',
        'operator': '>=',
        'value': 300,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    'qb_500_rush_yards': {
        'display': '500+ Rush Yards',
        'type': 'threshold',
        'column': 'rushing_yards',
        'operator': '>=',
        'value': 500,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    'qb_5_rush_tds': {
        'display': '5+ Rush TDs',
        'type': 'threshold',
        'column': 'rushing_tds',
        'operator': '>=',
        'value': 5,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    'qb_under_10_int': {
        'display': 'Under 10 INTs',
        'type': 'threshold',
        'column': 'interceptions_thrown',
        'operator': '<',
        'value': 10,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    'qb_4000_pass_yards': {
        'display': '4000+ Pass Yards',
        'type': 'threshold',
        'column': 'passing_yards',
        'operator': '>=',
        'value': 4000,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    'qb_30_pass_tds': {
        'display': '30+ Pass TDs',
        'type': 'threshold',
        'column': 'passing_tds',
        'operator': '>=',
        'value': 30,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB'],
        'eligible_stat_types': ['PASSING'],
    },
    
    # =========================================================================
    # STAT THRESHOLD QUALIFIERS - RB specific (same season)
    # =========================================================================
    'rb_1000_rush_yards': {
        'display': '1000+ Rush Yards',
        'type': 'threshold',
        'column': 'rushing_yards',
        'operator': '>=',
        'value': 1000,
        'qualifier_type': 'same_season',
        'eligible_positions': ['RB', 'FB'],
        'eligible_stat_types': ['RUSHING'],
    },
    'rb_50_receptions': {
        'display': '50+ Receptions',
        'type': 'threshold',
        'column': 'receptions',
        'operator': '>=',
        'value': 50,
        'qualifier_type': 'same_season',
        'eligible_positions': ['RB', 'FB'],
        'eligible_stat_types': ['RUSHING', 'RECEIVING'],
    },
    'rb_10_rush_tds': {
        'display': '10+ Rush TDs',
        'type': 'threshold',
        'column': 'rushing_tds',
        'operator': '>=',
        'value': 10,
        'qualifier_type': 'same_season',
        'eligible_positions': ['RB', 'FB'],
        'eligible_stat_types': ['RUSHING'],
    },
    'rb_under_500_rush_yards': {
        'display': 'Under 500 Rush Yards',
        'type': 'threshold',
        'column': 'rushing_yards',
        'operator': '<',
        'value': 500,
        'qualifier_type': 'same_season',
        'eligible_positions': ['RB', 'FB'],
        'eligible_stat_types': ['RECEIVING'],  # For receiving-focused RBs
    },
    
    # =========================================================================
    # STAT THRESHOLD QUALIFIERS - WR/TE specific (same season)
    # =========================================================================
    'wr_1000_rec_yards': {
        'display': '1000+ Rec Yards',
        'type': 'threshold',
        'column': 'receiving_yards',
        'operator': '>=',
        'value': 1000,
        'qualifier_type': 'same_season',
        'eligible_positions': ['WR', 'TE'],
        'eligible_stat_types': ['RECEIVING'],
    },
    'wr_100_receptions': {
        'display': '100+ Receptions',
        'type': 'threshold',
        'column': 'receptions',
        'operator': '>=',
        'value': 100,
        'qualifier_type': 'same_season',
        'eligible_positions': ['WR', 'TE'],
        'eligible_stat_types': ['RECEIVING'],
    },
    'wr_10_rec_tds': {
        'display': '10+ Rec TDs',
        'type': 'threshold',
        'column': 'receiving_tds',
        'operator': '>=',
        'value': 10,
        'qualifier_type': 'same_season',
        'eligible_positions': ['WR', 'TE'],
        'eligible_stat_types': ['RECEIVING'],
    },
    'wr_under_50_receptions': {
        'display': 'Under 50 Receptions',
        'type': 'threshold',
        'column': 'receptions',
        'operator': '<',
        'value': 50,
        'qualifier_type': 'same_season',
        'eligible_positions': ['WR', 'TE'],
        'eligible_stat_types': ['RECEIVING'],  # Big play receivers
    },
    
    # =========================================================================
    # GENERAL STAT THRESHOLDS (any position)
    # =========================================================================
    'any_200_fantasy_pts': {
        'display': '200+ Fantasy Pts',
        'type': 'threshold',
        'column': 'fantasy_points',
        'operator': '>=',
        'value': 200,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB', 'RB', 'WR', 'TE', 'FB'],
        'eligible_stat_types': ['PASSING', 'RUSHING', 'RECEIVING', 'FANTASY'],
    },
    'any_300_fantasy_pts': {
        'display': '300+ Fantasy Pts',
        'type': 'threshold',
        'column': 'fantasy_points',
        'operator': '>=',
        'value': 300,
        'qualifier_type': 'same_season',
        'eligible_positions': ['QB', 'RB', 'WR', 'TE', 'FB'],
        'eligible_stat_types': ['PASSING', 'RUSHING', 'RECEIVING', 'FANTASY'],
    },
}

# Helper function to get qualifiers compatible with a stat category
def get_compatible_qualifiers(stat_category: str) -> list:
    """Get list of qualifier keys compatible with a stat category"""
    stat_info = STAT_CATEGORIES.get(stat_category, {})
    stat_type = stat_info.get('type', '')
    eligible_positions = stat_info.get('eligible_positions', [])
    
    compatible = []
    for key, qual in STAT_QUALIFIERS.items():
        # Check if stat type is compatible
        if stat_type not in qual.get('eligible_stat_types', []):
            continue
        
        # For position-specific qualifiers, check position compatibility
        qual_positions = qual.get('eligible_positions', [])
        if qual_positions:
            # At least one eligible position must match
            if not any(pos in eligible_positions for pos in qual_positions):
                continue
        
        compatible.append(key)
    
    return compatible
