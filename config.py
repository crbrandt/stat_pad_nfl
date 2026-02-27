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