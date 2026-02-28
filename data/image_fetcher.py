"""
Player image fetcher for NFL StatPad Game
Fetches player headshots from ESPN, NFL.com, or provides fallback
"""
import os
import requests
from typing import Optional, Dict
from functools import lru_cache

# ESPN CDN URL pattern
ESPN_HEADSHOT_URL = "https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{espn_id}.png&w=350&h=254"

# NFL.com CDN URL pattern (requires player slug)
NFL_HEADSHOT_URL = "https://static.www.nfl.com/image/private/f_auto,q_auto/league/{player_slug}"

# Fallback silhouette
FALLBACK_IMAGE = "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=350&h=254"

# Team logo URLs (ESPN)
TEAM_LOGO_URL = "https://a.espncdn.com/i/teamlogos/nfl/500/{team}.png"

# Alternative team logo URL (smaller)
TEAM_LOGO_URL_SMALL = "https://a.espncdn.com/i/teamlogos/nfl/500/scoreboard/{team}.png"

# Conference logos
AFC_LOGO_URL = "https://a.espncdn.com/i/teamlogos/nfl/500/afc.png"
NFC_LOGO_URL = "https://a.espncdn.com/i/teamlogos/nfl/500/nfc.png"
# NFL shield logo - using a reliable source
NFL_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/a/a2/National_Football_League_logo.svg"

# Division to teams mapping
DIVISION_TEAMS = {
    'AFC East': ['BUF', 'MIA', 'NE', 'NYJ'],
    'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
    'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
    'AFC West': ['DEN', 'KC', 'LV', 'LAC'],
    'NFC East': ['DAL', 'NYG', 'PHI', 'WAS'],
    'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
    'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
    'NFC West': ['ARI', 'LAR', 'SF', 'SEA'],
}


@lru_cache(maxsize=1000)
def get_player_headshot_url(espn_id: Optional[str] = None, 
                            player_id: Optional[str] = None,
                            player_name: Optional[str] = None) -> str:
    """
    Get player headshot URL
    
    Args:
        espn_id: ESPN player ID (preferred)
        player_id: GSIS player ID
        player_name: Player name (for fallback lookup)
        
    Returns:
        URL to player headshot image
    """
    # Try ESPN first (most reliable)
    if espn_id:
        url = ESPN_HEADSHOT_URL.format(espn_id=espn_id)
        if verify_image_exists(url):
            return url
    
    # Return fallback
    return FALLBACK_IMAGE


def verify_image_exists(url: str, timeout: int = 2) -> bool:
    """
    Verify that an image URL returns a valid image
    
    Args:
        url: Image URL to verify
        timeout: Request timeout in seconds
        
    Returns:
        True if image exists and is valid
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            return 'image' in content_type
    except:
        pass
    return False


def get_team_logo_url(team_abbr: str, size: str = 'large') -> str:
    """
    Get team logo URL
    
    Args:
        team_abbr: Team abbreviation (e.g., 'KC', 'SF')
        size: 'large' or 'small'
        
    Returns:
        URL to team logo image
    """
    # Normalize team abbreviation
    team_abbr = team_abbr.upper().strip()
    
    # Handle special cases
    team_mapping = {
        'LV': 'lv',      # Las Vegas Raiders
        'LAC': 'lac',    # LA Chargers
        'LAR': 'lar',    # LA Rams (sometimes 'la')
        'WSH': 'wsh',    # Washington (sometimes 'was')
        'WAS': 'wsh',
        'JAX': 'jax',    # Jacksonville
        'JAC': 'jax',
    }
    
    team_code = team_mapping.get(team_abbr, team_abbr.lower())
    
    if size == 'small':
        return TEAM_LOGO_URL_SMALL.format(team=team_code)
    return TEAM_LOGO_URL.format(team=team_code)


# Team colors for fallback styling
TEAM_COLORS = {
    'ARI': {'primary': '#97233F', 'secondary': '#000000'},
    'ATL': {'primary': '#A71930', 'secondary': '#000000'},
    'BAL': {'primary': '#241773', 'secondary': '#000000'},
    'BUF': {'primary': '#00338D', 'secondary': '#C60C30'},
    'CAR': {'primary': '#0085CA', 'secondary': '#101820'},
    'CHI': {'primary': '#0B162A', 'secondary': '#C83803'},
    'CIN': {'primary': '#FB4F14', 'secondary': '#000000'},
    'CLE': {'primary': '#311D00', 'secondary': '#FF3C00'},
    'DAL': {'primary': '#003594', 'secondary': '#869397'},
    'DEN': {'primary': '#FB4F14', 'secondary': '#002244'},
    'DET': {'primary': '#0076B6', 'secondary': '#B0B7BC'},
    'GB': {'primary': '#203731', 'secondary': '#FFB612'},
    'HOU': {'primary': '#03202F', 'secondary': '#A71930'},
    'IND': {'primary': '#002C5F', 'secondary': '#A2AAAD'},
    'JAX': {'primary': '#006778', 'secondary': '#D7A22A'},
    'KC': {'primary': '#E31837', 'secondary': '#FFB81C'},
    'LAC': {'primary': '#0080C6', 'secondary': '#FFC20E'},
    'LAR': {'primary': '#003594', 'secondary': '#FFA300'},
    'LV': {'primary': '#000000', 'secondary': '#A5ACAF'},
    'MIA': {'primary': '#008E97', 'secondary': '#FC4C02'},
    'MIN': {'primary': '#4F2683', 'secondary': '#FFC62F'},
    'NE': {'primary': '#002244', 'secondary': '#C60C30'},
    'NO': {'primary': '#D3BC8D', 'secondary': '#101820'},
    'NYG': {'primary': '#0B2265', 'secondary': '#A71930'},
    'NYJ': {'primary': '#125740', 'secondary': '#000000'},
    'PHI': {'primary': '#004C54', 'secondary': '#A5ACAF'},
    'PIT': {'primary': '#FFB612', 'secondary': '#101820'},
    'SEA': {'primary': '#002244', 'secondary': '#69BE28'},
    'SF': {'primary': '#AA0000', 'secondary': '#B3995D'},
    'TB': {'primary': '#D50A0A', 'secondary': '#FF7900'},
    'TEN': {'primary': '#0C2340', 'secondary': '#4B92DB'},
    'WAS': {'primary': '#5A1414', 'secondary': '#FFB612'},
}


def get_division_team_logos(division: str) -> list:
    """
    Get list of team logo URLs for a division
    
    Args:
        division: Division name (e.g., 'AFC East')
        
    Returns:
        List of team logo URLs
    """
    teams = DIVISION_TEAMS.get(division, [])
    return [get_team_logo_url(team) for team in teams]


def get_conference_logo_url(conference: str) -> str:
    """
    Get conference logo URL
    
    Args:
        conference: 'AFC', 'NFC', or 'NFL'
        
    Returns:
        URL to conference logo
    """
    conference = conference.upper().strip()
    if conference == 'AFC':
        return AFC_LOGO_URL
    elif conference == 'NFC':
        return NFC_LOGO_URL
    else:
        return NFL_LOGO_URL


def get_team_colors(team_abbr: str) -> Dict[str, str]:
    """
    Get team colors for styling
    
    Args:
        team_abbr: Team abbreviation
        
    Returns:
        Dictionary with 'primary' and 'secondary' color hex codes
    """
    team_abbr = team_abbr.upper().strip()
    return TEAM_COLORS.get(team_abbr, {'primary': '#333333', 'secondary': '#666666'})


def generate_player_placeholder_svg(team_abbr: str, player_name: str = "") -> str:
    """
    Generate an SVG placeholder for players without headshots
    
    Args:
        team_abbr: Team abbreviation for colors
        player_name: Player name for initials
        
    Returns:
        SVG string
    """
    colors = get_team_colors(team_abbr)
    
    # Get initials
    initials = ""
    if player_name:
        parts = player_name.split()
        if len(parts) >= 2:
            initials = parts[0][0] + parts[-1][0]
        elif len(parts) == 1:
            initials = parts[0][0]
    
    svg = f'''
    <svg width="350" height="254" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{colors['primary']}"/>
        <circle cx="175" cy="100" r="60" fill="{colors['secondary']}" opacity="0.3"/>
        <text x="175" y="115" font-family="Arial, sans-serif" font-size="48" 
              fill="white" text-anchor="middle" font-weight="bold">{initials.upper()}</text>
        <rect x="125" y="170" width="100" height="60" rx="5" fill="{colors['secondary']}" opacity="0.3"/>
    </svg>
    '''
    return svg


if __name__ == "__main__":
    # Test image fetcher
    print("Testing image fetcher...")
    
    # Test team logos
    for team in ['KC', 'SF', 'DAL', 'NE']:
        url = get_team_logo_url(team)
        exists = verify_image_exists(url)
        print(f"{team} logo: {url} - {'✓' if exists else '✗'}")
    
    # Test player headshot (Patrick Mahomes ESPN ID: 3139477)
    url = get_player_headshot_url(espn_id="3139477")
    print(f"Mahomes headshot: {url}")