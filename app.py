"""
NFL StatPad Game - Main Streamlit Application
A daily NFL trivia game where you pick players to maximize stats
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    GAME_NAME, NFL_TEAMS, TIER_COLORS, TIER_EMOJIS,
    STAT_CATEGORIES, TIMEZONE
)
from data.data_loader import get_player_database
from data.image_fetcher import (
    get_player_headshot_url, get_team_logo_url, get_team_colors,
    get_division_team_logos, get_conference_logo_url, DIVISION_TEAMS,
    NFL_LOGO_URL, AFC_LOGO_URL, NFC_LOGO_URL
)
from config import STAT_QUALIFIERS

# American football icon URL for qualifier-based rows
FOOTBALL_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/1/16/American_football.svg"
from game.puzzle_generator import get_daily_puzzle, format_criteria_display, format_qualifier_display
from game.validator import validate_player_submission, find_player_best_year, search_players
from game.scorer import score_submission, get_top_5_for_criteria, calculate_total_score, generate_share_text

# Page config
st.set_page_config(
    page_title=GAME_NAME,
    page_icon="🏈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme, tier effects, and mobile responsiveness
def load_custom_css():
    st.markdown("""
    <style>
    /* Dark theme base */
    .stApp {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    
    /* Header styling */
    .game-header {
        text-align: center;
        padding: 15px 0;
        border-bottom: 2px solid #333;
        margin-bottom: 15px;
    }
    
    .game-title {
        font-size: 2rem;
        font-weight: bold;
        color: #f39c12;
        margin: 0;
    }
    
    /* Stats header - responsive */
    .stats-header {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 15px;
        background: #16213e;
        border-radius: 10px;
        margin-bottom: 15px;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .stat-box {
        text-align: center;
        min-width: 80px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
    }
    
    .category-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .category-type {
        font-size: 0.6rem;
        color: #888;
    }
    
    /* Game row - mobile responsive */
    .game-row {
        background: #16213e;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
    }
    
    .game-row-content {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    /* Mobile-friendly row card */
    .row-card {
        background: #16213e;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .row-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
        flex-wrap: wrap;
    }
    
    .row-logo {
        width: 50px;
        height: 50px;
        object-fit: contain;
        flex-shrink: 0;
    }
    
    .row-info {
        flex: 1;
        min-width: 150px;
    }
    
    .row-years {
        font-size: 1.1rem;
        font-weight: bold;
        color: #fff;
    }
    
    .row-criteria {
        font-size: 0.85rem;
        color: #ccc;
        margin-top: 2px;
    }
    
    .team-logo {
        width: 50px;
        height: 50px;
        object-fit: contain;
    }
    
    .year-range {
        text-align: center;
        min-width: 60px;
    }
    
    .year-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .year-label {
        font-size: 0.6rem;
        color: #888;
    }
    
    .qualifier-box {
        background: #0e4429;
        padding: 6px 10px;
        border-radius: 5px;
        text-align: center;
        font-size: 0.75rem;
        display: inline-block;
        margin-top: 5px;
    }
    
    .qualifier-type {
        font-size: 0.55rem;
        color: #4ade80;
        margin-top: 3px;
    }
    
    /* Completed row with tier glow */
    .completed-row {
        position: relative;
        overflow: hidden;
    }
    
    .tier-diamond {
        background: linear-gradient(135deg, #1e3a5f 0%, #3B82F6 50%, #1e3a5f 100%);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
        animation: diamond-glow 2s ease-in-out infinite;
    }
    
    .tier-gold {
        background: linear-gradient(135deg, #3d2e0a 0%, #F59E0B 50%, #3d2e0a 100%);
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
    }
    
    .tier-silver {
        background: linear-gradient(135deg, #2d2d2d 0%, #9CA3AF 50%, #2d2d2d 100%);
        box-shadow: 0 0 10px rgba(156, 163, 175, 0.3);
    }
    
    .tier-bronze {
        background: linear-gradient(135deg, #2d1f0a 0%, #CD7F32 50%, #2d1f0a 100%);
    }
    
    .tier-iron {
        background: #374151;
    }
    
    @keyframes diamond-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
        50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.8); }
    }
    
    /* Completed row card - mobile friendly */
    .completed-card {
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 5px;
    }
    
    .completed-card-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .player-info-compact {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .player-score-compact {
        text-align: right;
        white-space: nowrap;
    }
    
    /* Player card in completed row */
    .player-card {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-grow: 1;
        flex-wrap: wrap;
    }
    
    .player-headshot {
        width: 60px;
        height: 45px;
        object-fit: cover;
        border-radius: 5px;
    }
    
    .player-info {
        flex-grow: 1;
        min-width: 120px;
    }
    
    .player-name {
        font-size: 1rem;
        font-weight: bold;
    }
    
    .player-year {
        font-size: 0.8rem;
        color: #888;
    }
    
    .player-stat {
        text-align: right;
    }
    
    .stat-number {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .percentile-badge {
        font-size: 0.65rem;
        color: #888;
    }
    
    /* Leaderboard dropdown */
    .leaderboard {
        background: #0f0f23;
        padding: 8px;
        border-radius: 5px;
        margin-top: 8px;
    }
    
    .leaderboard-header {
        font-size: 0.75rem;
        color: #888;
        margin-bottom: 6px;
    }
    
    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 0.8rem;
        flex-wrap: wrap;
    }
    
    /* Footer buttons */
    .footer-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    
    .toggle-btn {
        background: #333;
        padding: 8px 16px;
        border-radius: 20px;
        cursor: pointer;
    }
    
    /* Share button */
    .share-btn {
        background: #22c55e;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
        margin: 15px auto;
        display: block;
        width: fit-content;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .game-title {
            font-size: 1.5rem;
        }
        
        .stat-value {
            font-size: 1.5rem;
        }
        
        .stat-label {
            font-size: 0.6rem;
        }
        
        .team-logo, .row-logo {
            width: 40px;
            height: 40px;
        }
        
        .year-value {
            font-size: 1rem;
        }
        
        .player-name {
            font-size: 0.9rem;
        }
        
        .stat-number {
            font-size: 1rem;
        }
        
        /* Make columns stack better on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        
        /* Compact the stats header on mobile */
        .stats-header {
            padding: 10px;
            gap: 5px;
        }
        
        .stat-box {
            min-width: 60px;
        }
    }
    
    /* Very small screens */
    @media (max-width: 480px) {
        .game-title {
            font-size: 1.3rem;
        }
        
        .stat-value {
            font-size: 1.3rem;
        }
        
        .completed-card {
            padding: 8px 10px;
        }
        
        .player-info-compact {
            font-size: 0.85rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'puzzle' not in st.session_state:
        st.session_state.puzzle = get_daily_puzzle()
    
    if 'submissions' not in st.session_state:
        st.session_state.submissions = [None] * 5
    
    if 'scores' not in st.session_state:
        st.session_state.scores = [None] * 5
    
    if 'easy_mode' not in st.session_state:
        st.session_state.easy_mode = False
    
    if 'show_how_to_play' not in st.session_state:
        st.session_state.show_how_to_play = False
    
    if 'show_faq' not in st.session_state:
        st.session_state.show_faq = False
    
    if 'expanded_rows' not in st.session_state:
        st.session_state.expanded_rows = [False] * 5
    
    if 'total_guesses' not in st.session_state:
        st.session_state.total_guesses = 0
    
    if 'player_db' not in st.session_state:
        with st.spinner("Loading player database..."):
            st.session_state.player_db = get_player_database()
    
    # Ensure expanded_rows has correct length
    if len(st.session_state.expanded_rows) < 5:
        st.session_state.expanded_rows = [False] * 5


def render_header():
    """Render the game header with Easy Mode toggle"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="game-header" style="border-bottom: none; padding-bottom: 0;">
            <h1 class="game-title">🏈 {GAME_NAME}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # Spacer
        easy_mode = st.checkbox("Easy Mode", value=st.session_state.easy_mode, key="easy_mode_header")
        if easy_mode != st.session_state.easy_mode:
            st.session_state.easy_mode = easy_mode
            st.rerun()


def render_stats_header():
    """Render the stats header with category, score, and guesses"""
    puzzle = st.session_state.puzzle
    total_score = calculate_total_score(st.session_state.scores)
    total_guesses = st.session_state.total_guesses
    
    # Use HTML for better mobile control
    score_display = f"{total_score:,.0f}" if total_score == int(total_score) else f"{total_score:,.1f}"
    
    st.markdown(f"""
    <div class="stats-header">
        <div class="stat-box">
            <div class="stat-value">{puzzle['stat_display']}</div>
            <div class="stat-label">CATEGORY ({puzzle['stat_type']})</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{score_display}</div>
            <div class="stat-label">TOTAL SCORE</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{total_guesses}</div>
            <div class="stat-label">GUESSES</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_logo_info_for_criteria(criteria: dict) -> dict:
    """
    Determine what logo(s) to show based on criteria.
    Returns dict with 'type' (single, division, conference, league, qualifier) and 'urls' list
    """
    team_abbr = criteria.get('team')
    division = criteria.get('division')
    conference = criteria.get('conference')
    qualifier = criteria.get('qualifier')
    
    if team_abbr:
        return {'type': 'single', 'urls': [get_team_logo_url(team_abbr)]}
    elif division:
        if division in DIVISION_TEAMS:
            logos = get_division_team_logos(division)
            return {'type': 'division', 'urls': logos, 'name': division}
        else:
            return {'type': 'single', 'urls': [NFL_LOGO_URL]}
    elif conference:
        if conference.upper() == 'AFC':
            return {'type': 'conference', 'urls': [AFC_LOGO_URL], 'name': 'AFC'}
        elif conference.upper() == 'NFC':
            return {'type': 'conference', 'urls': [NFC_LOGO_URL], 'name': 'NFC'}
        else:
            return {'type': 'single', 'urls': [NFL_LOGO_URL]}
    elif qualifier:
        # Qualifier-only row - show football icon
        return {'type': 'qualifier', 'urls': [FOOTBALL_ICON_URL]}
    else:
        return {'type': 'league', 'urls': [NFL_LOGO_URL]}


def render_game_row(row_index: int):
    """Render a single game row"""
    puzzle = st.session_state.puzzle
    criteria = puzzle['rows'][row_index]
    submission = st.session_state.submissions[row_index]
    score_data = st.session_state.scores[row_index]
    
    logo_info = get_logo_info_for_criteria(criteria)
    logo_url = logo_info['urls'][0] if logo_info['urls'] else NFL_LOGO_URL
    
    year_start = criteria.get('year_start', '')
    year_end = criteria.get('year_end', '')
    qualifier_display = format_qualifier_display(criteria)
    
    if submission is not None and score_data is not None:
        render_completed_row(row_index, submission, score_data, criteria, logo_url)
    else:
        render_input_row(row_index, criteria, logo_info, year_start, year_end, qualifier_display)


def render_completed_row(row_index: int, submission: dict, score_data: dict, criteria: dict, logo_url: str):
    """Render a completed row with player info, tier styling, and criteria display"""
    try:
        tier = score_data.get('tier', 'iron') if score_data else 'iron'
        tier_color = TIER_COLORS.get(tier, '#374151')
        tier_emoji = TIER_EMOJIS.get(tier, '⬛')
        score = score_data.get('score', 0) if score_data else 0
        percentile = score_data.get('percentile', 0) if score_data else 0
        
        player_name = submission.get('player', 'Unknown') if submission else 'Unknown'
        season = submission.get('season', '') if submission else ''
        team = submission.get('team', 'N/A') if submission else 'N/A'
        espn_id = submission.get('espn_id') if submission else None
        nfl_headshot_url = submission.get('headshot_url') if submission else None
        
        # Prefer ESPN headshots (better coverage for retired players)
        # Fall back to NFL.com, then to placeholder
        if espn_id:
            headshot_url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{espn_id}.png&w=350&h=254"
        elif nfl_headshot_url:
            headshot_url = nfl_headshot_url
        else:
            headshot_url = "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=350&h=254"
        
        # Get criteria display text
        criteria_text = format_criteria_display(criteria)
        qualifier_key = criteria.get('qualifier')
        qualifier_value = submission.get('qualifier_value') if submission else None

        # Mobile-friendly completed row card with headshot
        st.markdown(f"""
        <div class="completed-card" style="
            background: linear-gradient(90deg, {tier_color}33 0%, {tier_color}11 50%, transparent 100%);
            border-left: 4px solid {tier_color};
        ">
            <div style="font-size: 0.7rem; color: #888; margin-bottom: 4px;">{criteria_text}</div>
            <div class="completed-card-content" style="display: flex; align-items: center; gap: 12px;">
                <img src="{headshot_url}" style="width: 55px; height: 40px; object-fit: cover; border-radius: 4px; flex-shrink: 0;" onerror="this.src='https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=350&h=254'">
                <div class="player-info-compact" style="flex: 1; min-width: 0;">
                    <span style="font-size: 1.2rem;">{tier_emoji}</span>
                    <span style="font-weight: bold;">{player_name}</span>
                    <span style="color: #888;">({season})</span>
                </div>
                <div class="player-score-compact" style="text-align: right; flex-shrink: 0;">
                    <span style="font-size: 1.2rem; font-weight: bold; color: {tier_color};">{score:,.0f}</span>
                    <span style="color: #888; font-size: 0.75rem;"> pts</span>
                    <span style="color: #666; font-size: 0.65rem; margin-left: 8px;">{percentile:.0f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show qualifier value if applicable
        if qualifier_key and qualifier_value is not None:
            qualifier_info = STAT_QUALIFIERS.get(qualifier_key, {})
            qualifier_display = qualifier_info.get('display', qualifier_key)
            qualifier_column = qualifier_info.get('column', '')
            st.markdown(f"""
            <div style="font-size: 0.7rem; color: #4ade80; margin-top: -5px; margin-bottom: 8px; padding-left: 10px;">
                ✓ {qualifier_display}: {qualifier_value:,.0f} {qualifier_column.replace('_', ' ')}
            </div>
            """, unsafe_allow_html=True)

        # Expandable details - with error handling
        try:
            expanded = False
            if hasattr(st.session_state, 'expanded_rows') and len(st.session_state.expanded_rows) > row_index:
                expanded = st.session_state.expanded_rows[row_index]
            
            with st.expander(f"View details for {player_name}", expanded=expanded):
                # Tier badge
                st.markdown(f"""
                <div style="background: {tier_color}; padding: 5px 12px; border-radius: 15px; 
                            display: inline-block; margin: 8px 0; font-size: 0.85rem;">
                    {tier_emoji} {tier.upper()}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**{player_name}** • {season} • {team}")
                st.markdown(f"**Score:** {score:,.0f} pts ({percentile:.0f}th percentile)")
                
                # Show qualifier details if applicable
                if qualifier_key and qualifier_value is not None:
                    qualifier_info = STAT_QUALIFIERS.get(qualifier_key, {})
                    qualifier_display = qualifier_info.get('display', qualifier_key)
                    st.markdown(f"**Qualifier:** {qualifier_display} → {qualifier_value:,.0f}")
                
                # Top 5 leaderboard
                st.markdown("---")
                st.markdown("**Top 5 for this criteria:**")
                
                try:
                    top_5 = get_top_5_for_criteria(
                        st.session_state.player_db,
                        st.session_state.puzzle['stat_category'],
                        criteria
                    )
                    
                    for i, player in enumerate(top_5, 1):
                        is_selected = (player.get('player', '').lower() == player_name.lower() and 
                                      player.get('season') == season)
                        highlight = "→ " if is_selected else "  "
                        p_name = player.get('player', 'Unknown')
                        p_season = player.get('season', '')
                        p_team = player.get('team', 'N/A')
                        p_stat = player.get('stat_value', 0)
                        st.markdown(f"{highlight}**{i}.** {p_name} ({p_season}) - {p_team} - **{p_stat:,.0f}**")
                except Exception as e:
                    st.markdown("*Could not load top 5*")
        except Exception as e:
            pass  # Silently handle expander errors
            
    except Exception as e:
        st.error(f"Error displaying row: {str(e)}")


@st.cache_data
def get_all_player_names():
    """Get all unique player names from the database (cached)"""
    df = get_player_database()
    if hasattr(df, 'to_pandas'):
        all_players = df.select('player').unique().to_series().to_list()
    else:
        all_players = df['player'].unique().tolist()
    return sorted([p for p in all_players if p is not None])


def render_input_row(row_index: int, criteria: dict, logo_info: dict, year_start: int, year_end: int, qualifier_display: str):
    """Render an input row for player submission - mobile friendly"""
    
    # Get criteria text
    criteria_text = format_criteria_display(criteria)
    
    # Year display
    if year_start and year_end:
        if year_start == year_end:
            year_display = f"{year_start}"
        else:
            year_display = f"{year_start}-{year_end}"
    else:
        year_display = ""
    
    # Build logo HTML based on type (single, division, conference, league)
    if logo_info['type'] == 'division' and len(logo_info.get('urls', [])) == 4:
        # Show all 4 division team logos in a 2x2 grid
        logos = logo_info['urls']
        logo_html = f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2px; width: 60px; height: 60px; flex-shrink: 0;"><img src="{logos[0]}" style="width: 28px; height: 28px; object-fit: contain;"><img src="{logos[1]}" style="width: 28px; height: 28px; object-fit: contain;"><img src="{logos[2]}" style="width: 28px; height: 28px; object-fit: contain;"><img src="{logos[3]}" style="width: 28px; height: 28px; object-fit: contain;"></div>'
    else:
        # Single logo (team, conference, or league)
        logo_url = logo_info['urls'][0] if logo_info['urls'] else NFL_LOGO_URL
        logo_html = f'<img src="{logo_url}" class="row-logo">'
    
    st.markdown(f"""<div class="row-card"><div class="row-header">{logo_html}<div class="row-info"><div class="row-years">{year_display}</div><div class="row-criteria">{criteria_text}</div></div></div></div>""", unsafe_allow_html=True)
    
    # Player input - full width for mobile
    all_players = get_all_player_names()
    
    player_input = st.selectbox(
        "Select player",
        options=[""] + all_players,
        key=f"player_select_{row_index}",
        label_visibility="collapsed",
        index=0
    )
    
    # Year input (if not easy mode)
    if not st.session_state.easy_mode:
        year_input = st.number_input(
            "Year",
            min_value=year_start or 1999,
            max_value=year_end or 2024,
            value=year_end or 2024,
            key=f"year_input_{row_index}",
            label_visibility="collapsed"
        )
    else:
        year_input = None
    
    # Submit button - full width
    if st.button("Submit", key=f"submit_{row_index}", type="primary", use_container_width=True):
        submit_player(row_index, player_input, year_input)


def submit_player(row_index: int, player_name: str, year: int = None):
    """Handle player submission"""
    if not player_name:
        st.error("Please enter a player name")
        return
    
    puzzle = st.session_state.puzzle
    criteria = puzzle['rows'][row_index]
    stat_category = puzzle['stat_category']
    df = st.session_state.player_db
    
    # Increment total guesses for any submission attempt
    st.session_state.total_guesses += 1
    
    # Easy mode: find best year automatically
    if st.session_state.easy_mode or year is None:
        best_year_data = find_player_best_year(df, player_name, stat_category, criteria)
        if best_year_data:
            year = best_year_data['season']
        else:
            st.error(f"Could not find {player_name} matching the criteria")
            return
    
    # Validate submission
    is_valid, player_data, error_msg = validate_player_submission(
        df, player_name, year, stat_category, criteria
    )
    
    if not is_valid:
        st.error(error_msg)
        return
    
    # Score the submission
    score_data = score_submission(df, player_data, stat_category, criteria)
    
    # Update session state
    st.session_state.submissions[row_index] = player_data
    st.session_state.scores[row_index] = score_data
    
    # Rerun to show updated state
    st.rerun()


def render_footer():
    """Render footer with How to Play, FAQ, and Share buttons"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❓ How to Play", use_container_width=True):
            st.session_state.show_how_to_play = True
            st.session_state.show_faq = False
    
    with col2:
        if st.button("📊 FAQ", use_container_width=True):
            st.session_state.show_faq = True
            st.session_state.show_how_to_play = False
    
    with col3:
        # Share button if game is complete
        if all(s is not None for s in st.session_state.submissions):
            if st.button("📤 Share Score", type="primary", use_container_width=True):
                share_score()
    
    # Attribution footer
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 15px 0; border-top: 1px solid #333;">
        <p style="color: #888; font-size: 0.8rem; margin: 0;">
            Made by <strong style="color: #f39c12;">Cole Brandt</strong> • 
            <a href="https://github.com/crbrandt/stat_pad_nfl" target="_blank" style="color: #4ade80; text-decoration: none;">
                GitHub 🔗
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def share_score():
    """Generate and display share text"""
    puzzle = st.session_state.puzzle
    total_score = calculate_total_score(st.session_state.scores)
    
    share_text = generate_share_text(puzzle, st.session_state.scores, total_score)
    
    st.code(share_text, language=None)
    st.info("Copy the text above to share your score!")


def render_how_to_play():
    """Render How to Play modal"""
    if st.session_state.show_how_to_play:
        with st.expander("How to Play", expanded=True):
            st.markdown("""
            ## 🏈 NFL StatPad - How to Play
            
            ### Objective
            Select 5 players with their corresponding years to maximize your score for the stat category shown.
            
            ### How It Works
            1. Each row has specific criteria (team, year range, position, etc.)
            2. Submit a player + year that meets the row's requirements
            3. Your score increases by that player's stat total for that year
            
            ### Tiers
            - 🟦 **Diamond** (100%) - Best possible answer!
            - 🟨 **Gold** (90-99%) - Excellent choice
            - ⬜ **Silver** (75-89%) - Good choice
            - 🟫 **Bronze** (50-74%) - Decent choice
            - ⬛ **Iron** (<50%) - Room for improvement
            
            ### Easy Mode
            Toggle Easy Mode to automatically select the best year for any player you enter.
            
            ### Daily Reset
            A new puzzle is available every day at midnight PST!
            """)
            
            if st.button("Close"):
                st.session_state.show_how_to_play = False
                st.rerun()


def render_faq():
    """Render FAQ modal with fantasy scoring explanation"""
    if st.session_state.show_faq:
        with st.expander("FAQ", expanded=True):
            st.markdown("""
            ## 📊 Frequently Asked Questions
            
            ### How are Fantasy Points calculated?
            
            Fantasy Points use **ESPN Standard Scoring**:
            
            | Category | Points |
            |----------|--------|
            | **Passing Yards** | 1 pt per 25 yards (0.04/yard) |
            | **Passing TDs** | 4 pts each |
            | **Interceptions** | -2 pts each |
            | **Rushing Yards** | 1 pt per 10 yards (0.1/yard) |
            | **Rushing TDs** | 6 pts each |
            | **Receiving Yards** | 1 pt per 10 yards (0.1/yard) |
            | **Receiving TDs** | 6 pts each |
            | **Fumbles Lost** | -2 pts each |
            | **2-Point Conversions** | 2 pts each |
            
            *Note: This is non-PPR (no points per reception).*
            
            ---
            
            ### What years are included?
            
            The database includes NFL player statistics from **1999 to 2024**.
            
            ---
            
            ### How are percentiles calculated?
            
            Your answer is compared against all valid players who meet the row's criteria. 
            The percentile shows where your answer ranks (100% = best possible answer).
            
            ---
            
            ### What qualifiers are available?
            
            Some rows have additional qualifiers like:
            - **Pro Bowl** - Player made the Pro Bowl that season
            - **All-Pro** - Player was named All-Pro that season
            - **Rushing Attempts** - Minimum rushing attempts
            - **Targets** - Minimum receiving targets
            - **Pass Attempts** - Minimum pass attempts
            
            ---
            
            ### Can I play previous days' puzzles?
            
            Currently, only the daily puzzle is available. Each day at midnight PST, a new puzzle is generated.
            """)
            
            if st.button("Close FAQ"):
                st.session_state.show_faq = False
                st.rerun()


def main():
    """Main application entry point"""
    load_custom_css()
    init_session_state()
    
    render_header()
    render_stats_header()
    
    st.markdown("---")
    
    # Render game rows
    for i in range(5):
        render_game_row(i)
    
    render_footer()
    render_how_to_play()
    render_faq()


if __name__ == "__main__":
    main()