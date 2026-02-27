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

# Custom CSS for dark theme and tier effects
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
        padding: 20px 0;
        border-bottom: 2px solid #333;
        margin-bottom: 20px;
    }
    
    .game-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f39c12;
        margin: 0;
    }
    
    /* Stats header */
    .stats-header {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 20px;
        background: #16213e;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .stat-box {
        text-align: center;
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
    }
    
    .category-name {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .category-type {
        font-size: 0.7rem;
        color: #888;
    }
    
    /* Row styling */
    .game-row {
        background: #16213e;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .team-logo {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }
    
    .year-range {
        text-align: center;
        min-width: 80px;
    }
    
    .year-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .year-label {
        font-size: 0.7rem;
        color: #888;
    }
    
    .qualifier-box {
        background: #0e4429;
        padding: 8px 12px;
        border-radius: 5px;
        text-align: center;
        font-size: 0.8rem;
    }
    
    .qualifier-type {
        font-size: 0.6rem;
        color: #4ade80;
        margin-top: 4px;
    }
    
    /* Add player button */
    .add-player-btn {
        background: #22c55e;
        color: white;
        padding: 15px 30px;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        flex-grow: 1;
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
    
    /* Player card in completed row */
    .player-card {
        display: flex;
        align-items: center;
        gap: 15px;
        flex-grow: 1;
    }
    
    .player-headshot {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: 5px;
    }
    
    .player-info {
        flex-grow: 1;
    }
    
    .player-name {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .player-year {
        font-size: 0.9rem;
        color: #888;
    }
    
    .player-stat {
        text-align: right;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .percentile-badge {
        font-size: 0.7rem;
        color: #888;
    }
    
    /* Leaderboard dropdown */
    .leaderboard {
        background: #0f0f23;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    
    .leaderboard-header {
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 8px;
    }
    
    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        font-size: 0.85rem;
    }
    
    /* Footer buttons */
    .footer-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    
    .toggle-btn {
        background: #333;
        padding: 10px 20px;
        border-radius: 20px;
        cursor: pointer;
    }
    
    /* Share button */
    .share-btn {
        background: #22c55e;
        color: white;
        padding: 15px 30px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
        margin: 20px auto;
        display: block;
        width: fit-content;
    }
    
    /* Modal styling */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: #1a1a2e;
        padding: 30px;
        border-radius: 15px;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    
    if 'expanded_rows' not in st.session_state:
        st.session_state.expanded_rows = [False] * 5
    
    if 'total_guesses' not in st.session_state:
        st.session_state.total_guesses = 0
    
    if 'player_db' not in st.session_state:
        with st.spinner("Loading player database..."):
            st.session_state.player_db = get_player_database()


def render_header():
    """Render the game header"""
    st.markdown(f"""
    <div class="game-header">
        <h1 class="game-title">🏈 {GAME_NAME}</h1>
    </div>
    """, unsafe_allow_html=True)


def render_stats_header():
    """Render the stats header with category, score, and guesses"""
    puzzle = st.session_state.puzzle
    total_score = calculate_total_score(st.session_state.scores)
    total_guesses = st.session_state.total_guesses  # Use total guesses including failed attempts
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: bold;">{puzzle['stat_display']}</div>
            <div style="font-size: 0.8rem; color: #888;">CATEGORY<br>({puzzle['stat_type']})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score_display = f"{total_score:,.0f}" if total_score == int(total_score) else f"{total_score:,.1f}"
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 3rem; font-weight: bold;">{score_display}</div>
            <div style="font-size: 0.8rem; color: #888;">TOTAL SCORE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 3rem; font-weight: bold;">{total_guesses}</div>
            <div style="font-size: 0.8rem; color: #888;">TOTAL GUESSES</div>
        </div>
        """, unsafe_allow_html=True)


def get_logo_info_for_criteria(criteria: dict) -> dict:
    """
    Determine what logo(s) to show based on criteria.
    Returns dict with 'type' (single, division, conference, league) and 'urls' list
    """
    team_abbr = criteria.get('team')
    division = criteria.get('division')
    conference = criteria.get('conference')
    
    if team_abbr:
        # Single team
        return {'type': 'single', 'urls': [get_team_logo_url(team_abbr)]}
    elif division:
        # Division - show all 4 team logos
        if division in DIVISION_TEAMS:
            logos = get_division_team_logos(division)
            return {'type': 'division', 'urls': logos, 'name': division}
        else:
            return {'type': 'single', 'urls': [NFL_LOGO_URL]}
    elif conference:
        # Conference - show AFC or NFC logo
        if conference.upper() == 'AFC':
            return {'type': 'conference', 'urls': [AFC_LOGO_URL], 'name': 'AFC'}
        elif conference.upper() == 'NFC':
            return {'type': 'conference', 'urls': [NFC_LOGO_URL], 'name': 'NFC'}
        else:
            return {'type': 'single', 'urls': [NFL_LOGO_URL]}
    else:
        # League-wide - show NFL logo
        return {'type': 'league', 'urls': [NFL_LOGO_URL]}


def render_game_row(row_index: int):
    """Render a single game row"""
    puzzle = st.session_state.puzzle
    criteria = puzzle['rows'][row_index]
    submission = st.session_state.submissions[row_index]
    score_data = st.session_state.scores[row_index]
    
    # Get logo info based on criteria
    logo_info = get_logo_info_for_criteria(criteria)
    
    # For backward compatibility, use first logo URL
    logo_url = logo_info['urls'][0] if logo_info['urls'] else NFL_LOGO_URL
    
    # Format year range
    year_start = criteria.get('year_start', '')
    year_end = criteria.get('year_end', '')
    
    # Format qualifier
    qualifier_display = format_qualifier_display(criteria)
    
    if submission is not None and score_data is not None:
        # Completed row
        render_completed_row(row_index, submission, score_data, criteria, logo_url)
    else:
        # Incomplete row - show input
        render_input_row(row_index, criteria, logo_info, year_start, year_end, qualifier_display)


def render_completed_row(row_index: int, submission: dict, score_data: dict, criteria: dict, logo_url: str):
    """Render a completed row with player info and tier styling"""
    tier = score_data.get('tier', 'iron')
    tier_color = TIER_COLORS.get(tier, '#374151')
    tier_emoji = TIER_EMOJIS.get(tier, '⬛')
    score = score_data.get('score', 0)
    percentile = score_data.get('percentile', 0)

    # Get player headshot
    espn_id = submission.get('espn_id')
    headshot_url = get_player_headshot_url(espn_id=espn_id) if espn_id else None

    # Create a colored container for the completed row
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {tier_color}33 0%, {tier_color}11 50%, transparent 100%);
        border-left: 4px solid {tier_color};
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.3rem;">{tier_emoji}</span>
            <span style="font-weight: bold;">{submission['player']}</span>
            <span style="color: #888;">({submission['season']})</span>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 1.3rem; font-weight: bold; color: {tier_color};">{score:,.0f}</span>
            <span style="color: #888; font-size: 0.8rem;"> pts</span>
            <span style="color: #666; font-size: 0.7rem; margin-left: 10px;">{percentile:.0f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create expandable section for details
    with st.expander(f"View details for {submission['player']}", expanded=st.session_state.expanded_rows[row_index]):
        # Player card
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if headshot_url:
                st.image(headshot_url, width=80)
            else:
                st.image(logo_url, width=60)
        
        with col2:
            st.markdown(f"""
            <div>
                <div style="font-size: 1.3rem; font-weight: bold;">{submission['player']}</div>
                <div style="color: #888;">{submission['season']} • {submission.get('team', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: bold; color: {tier_color};">
                    {score_data['score']:,.0f}
                </div>
                <div style="font-size: 0.7rem; color: #888;">
                    {score_data['percentile']:.0f}th PERCENTILE
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tier badge
        st.markdown(f"""
        <div style="background: {tier_color}; padding: 5px 15px; border-radius: 15px; 
                    display: inline-block; margin: 10px 0;">
            {TIER_EMOJIS.get(tier, '⬛')} {tier.upper()}
        </div>
        """, unsafe_allow_html=True)
        
        # Top 5 leaderboard
        st.markdown("---")
        st.markdown("**Top 5 for this criteria:**")
        
        top_5 = get_top_5_for_criteria(
            st.session_state.player_db,
            st.session_state.puzzle['stat_category'],
            criteria
        )
        
        for i, player in enumerate(top_5, 1):
            is_selected = (player['player'].lower() == submission['player'].lower() and 
                          player['season'] == submission['season'])
            highlight = "→ " if is_selected else "  "
            st.markdown(f"{highlight}**{i}.** {player['player']} ({player['season']}) - {player['team']} - **{player['stat_value']:,.0f}**")


def get_player_autocomplete_options(df, search_term: str, limit: int = 10) -> list:
    """Get autocomplete suggestions for player names"""
    if not search_term or len(search_term) < 2:
        return []
    
    search_lower = search_term.lower()
    
    # Get unique player names
    if hasattr(df, 'to_pandas'):
        # Polars DataFrame
        all_players = df.select('player').unique().to_series().to_list()
    else:
        # Pandas DataFrame
        all_players = df['player'].unique().tolist()
    
    # Filter by search term (first name, last name, or full name)
    matches = []
    for player in all_players:
        if player is None:
            continue
        player_lower = player.lower()
        # Match if search term is at start of first name, last name, or anywhere in name
        name_parts = player_lower.split()
        if (player_lower.startswith(search_lower) or 
            any(part.startswith(search_lower) for part in name_parts) or
            search_lower in player_lower):
            matches.append(player)
    
    # Sort by relevance (exact start match first, then alphabetical)
    def sort_key(name):
        name_lower = name.lower()
        if name_lower.startswith(search_lower):
            return (0, name)
        elif any(part.startswith(search_lower) for part in name_lower.split()):
            return (1, name)
        else:
            return (2, name)
    
    matches.sort(key=sort_key)
    return matches[:limit]


@st.cache_data
def get_all_player_names():
    """Get all unique player names from the database (cached)"""
    df = get_player_database()
    if hasattr(df, 'to_pandas'):
        # Polars DataFrame
        all_players = df.select('player').unique().to_series().to_list()
    else:
        # Pandas DataFrame
        all_players = df['player'].unique().tolist()
    # Filter out None values and sort
    return sorted([p for p in all_players if p is not None])


def search_players_callback(search_term: str) -> list:
    """Callback function for st_searchbox to search players"""
    if not search_term or len(search_term) < 2:
        return []
    
    search_lower = search_term.lower()
    all_players = get_all_player_names()
    
    # Filter by search term
    matches = []
    for player in all_players:
        player_lower = player.lower()
        name_parts = player_lower.split()
        if (player_lower.startswith(search_lower) or 
            any(part.startswith(search_lower) for part in name_parts) or
            search_lower in player_lower):
            matches.append(player)
    
    # Sort by relevance
    def sort_key(name):
        name_lower = name.lower()
        if name_lower.startswith(search_lower):
            return (0, name)
        elif any(part.startswith(search_lower) for part in name_lower.split()):
            return (1, name)
        else:
            return (2, name)
    
    matches.sort(key=sort_key)
    return matches[:15]


def render_input_row(row_index: int, criteria: dict, logo_info: dict, year_start: int, year_end: int, qualifier_display: str):
    """Render an input row for player submission"""
    
    col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
    
    with col1:
        # Handle different logo types
        if logo_info['type'] == 'division':
            # Show 4 team logos in a 2x2 grid
            logo_cols = st.columns(2)
            for i, url in enumerate(logo_info['urls'][:4]):
                with logo_cols[i % 2]:
                    st.image(url, width=28)
        else:
            # Single logo (team, conference, or league)
            st.image(logo_info['urls'][0], width=60)
    
    with col2:
        if year_start and year_end:
            if year_start == year_end:
                st.markdown(f"**{year_start}**")
            else:
                st.markdown(f"**{year_start}**<br>to<br>**{year_end}**", unsafe_allow_html=True)
    
    with col3:
        # Show criteria
        criteria_text = format_criteria_display(criteria)
        st.markdown(f"*{criteria_text}*")
        
        if qualifier_display:
            st.markdown(f"""
            <div style="background: #0e4429; padding: 5px 10px; border-radius: 5px; 
                        font-size: 0.8rem; margin-top: 5px;">
                {qualifier_display.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        # Get all player names for selectbox
        all_players = get_all_player_names()
        
        # Use selectbox with search capability
        player_input = st.selectbox(
            "Select player",
            options=[""] + all_players,
            key=f"player_select_{row_index}",
            label_visibility="collapsed",
            index=0
        )
        
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
        
        if st.button("Submit", key=f"submit_{row_index}", type="primary"):
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
            st.experimental_rerun()
            return
    
    # Validate submission
    is_valid, player_data, error_msg = validate_player_submission(
        df, player_name, year, stat_category, criteria
    )
    
    if not is_valid:
        st.error(error_msg)
        st.experimental_rerun()
        return
    
    # Score the submission
    score_data = score_submission(df, player_data, stat_category, criteria)
    
    # Update session state
    st.session_state.submissions[row_index] = player_data
    st.session_state.scores[row_index] = score_data
    
    # Show success message
    tier = score_data['tier']
    st.success(f"✓ {player_data['player']} ({year}) - {score_data['score']:,.0f} pts - {TIER_EMOJIS.get(tier, '')} {tier.upper()}")
    
    st.experimental_rerun()


def render_footer():
    """Render footer with Easy Mode toggle and How to Play"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        easy_mode = st.checkbox("Easy Mode", value=st.session_state.easy_mode, key="easy_mode_toggle")
        if easy_mode != st.session_state.easy_mode:
            st.session_state.easy_mode = easy_mode
    
    with col2:
        if st.button("❓ How to Play"):
            st.session_state.show_how_to_play = True
    
    with col3:
        # Check if game is complete
        if all(s is not None for s in st.session_state.submissions):
            if st.button("📤 Share Score", type="primary"):
                share_score()


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
                st.experimental_rerun()


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
        st.markdown("")
    
    render_footer()
    render_how_to_play()


if __name__ == "__main__":
    main()