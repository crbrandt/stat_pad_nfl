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
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Modern dark theme base - charcoal grey like original StatPad */
    .stApp {
        background-color: #2d2d2d !important;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        overflow-x: hidden !important;
    }
    
    /* Prevent horizontal scroll globally */
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    
    /* Constrain all horizontal blocks to viewport width */
    [data-testid="stHorizontalBlock"] {
        max-width: 100% !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Constrain all columns to not overflow */
    [data-testid="column"] {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Override Streamlit's default background */
    .main .block-container {
        background-color: #2d2d2d !important;
        padding: 1rem 1rem 2rem 1rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* Header styling - modern and compact */
    .game-header {
        text-align: center;
        padding: 12px 0;
        margin-bottom: 12px;
    }
    
    .game-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .game-title-accent {
        color: #f39c12;
    }
    
    /* Stats header - responsive with modern styling */
    .stats-header {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 16px;
        background: #3a3a3a;
        border-radius: 12px;
        margin-bottom: 5px;
        flex-wrap: wrap;
        gap: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
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
        background: #3a3a3a;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    
    .game-row-content {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    /* Mobile-friendly row card */
    .row-card {
        background: #3a3a3a;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
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
    
    /* Modern Streamlit button styling - touch friendly */
    .stButton > button {
        background-color: #b7a57a !important;
        color: #000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        min-height: 48px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #a89463 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Primary button variant (Submit buttons) */
    .stButton > button[kind="primary"] {
        background-color: #b7a57a !important;
        color: #000 !important;
    }
    
    /* Green "Add Player" button styling */
    /* Target buttons that contain "add player" text in the last column */
    [data-testid="column"]:last-child .stButton > button {
        background-color: #22c55e !important;
        color: #000 !important;
        height: 90px !important;
        min-height: 90px !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
    }
    
    [data-testid="column"]:last-child .stButton > button:hover {
        background-color: #16a34a !important;
    }
    
    /* Secondary/default buttons (How to Play, FAQ) */
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background-color: #4a4a4a !important;
        color: #fff !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        background-color: #5a5a5a !important;
    }
    
    /* Modal/Dialog styling */
    [data-testid="stModal"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
    }
    
    [data-testid="stModal"] > div {
        background-color: #2d2d2d !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #3a3a3a !important;
        border: 1px solid #555 !important;
        border-radius: 10px !important;
        min-height: 48px !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #3a3a3a !important;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        background-color: #3a3a3a !important;
        border: 1px solid #555 !important;
        border-radius: 10px !important;
        color: #fff !important;
        min-height: 48px !important;
        font-size: 1rem !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #fff !important;
        font-size: 0.9rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #3a3a3a !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-size: 0.9rem !important;
    }
    
    .streamlit-expanderContent {
        background-color: #333 !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Divider styling */
    hr {
        border-color: #444 !important;
        margin: 12px 0 !important;
    }
    
    /* Row cell styling - responsive */
    .row-cell {
        background: #3a3a3a;
        border-radius: 8px;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 80px;
        min-height: 80px;
    }
    
    .cell-logo {
        width: 50px;
        height: 50px;
        object-fit: contain;
    }
    
    .division-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2px;
        width: 50px;
        height: 50px;
    }
    
    .division-logo {
        width: 24px;
        height: 24px;
        object-fit: contain;
    }
    
    .year-single {
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .year-range-display {
        text-align: center;
    }
    
    .year-num {
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .year-to {
        font-size: 0.6rem;
        color: #888;
    }
    
    .qualifier-content {
        text-align: center;
    }
    
    .qualifier-label {
        font-size: 0.6rem;
        color: #888;
        text-transform: uppercase;
    }
    
    .qualifier-text {
        font-size: 0.85rem;
        font-weight: bold;
    }
    
    .qualifier-badge {
        color: #000;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.5rem;
        font-weight: bold;
        margin-top: 3px;
        display: inline-block;
    }
    
    .criteria-text {
        text-align: center;
        font-size: 0.8rem;
        color: #ccc;
    }
    
    /* CSS Grid-based game row - for mobile compatibility */
    .game-row-grid {
        display: grid;
        grid-template-columns: 1fr 0.8fr 2fr;
        gap: 8px;
        margin-bottom: 8px;
        width: 100%;
        box-sizing: border-box;
    }
    
    .grid-cell {
        background: #3a3a3a;
        border-radius: 8px;
        padding: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 70px;
    }
    
    .grid-logo {
        width: 45px;
        height: 45px;
        object-fit: contain;
    }
    
    .grid-division-logos {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3px;
        width: 45px;
        height: 45px;
    }
    
    .grid-div-logo {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }
    
    .grid-year-single {
        font-size: 1.2rem;
        font-weight: bold;
        color: #fff;
    }
    
    .grid-year-range {
        text-align: center;
    }
    
    .grid-year-num {
        font-size: 1rem;
        font-weight: bold;
        color: #fff;
    }
    
    .grid-year-to {
        font-size: 0.55rem;
        color: #888;
    }
    
    .grid-qualifier-content {
        text-align: center;
    }
    
    .grid-qualifier-label {
        font-size: 0.55rem;
        color: #888;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    
    .grid-qualifier-text {
        font-size: 0.8rem;
        font-weight: bold;
        color: #fff;
    }
    
    .grid-qualifier-badge {
        color: #000;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.45rem;
        font-weight: bold;
        margin-top: 4px;
        display: inline-block;
    }
    
    .grid-criteria-text {
        text-align: center;
        font-size: 0.75rem;
        color: #ccc;
    }
    
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
            width: 35px;
            height: 35px;
        }
        
        .year-value {
            font-size: 0.9rem;
        }
        
        .player-name {
            font-size: 0.9rem;
        }
        
        .stat-number {
            font-size: 1rem;
        }
        
        /* Constrain the main container to viewport width */
        .main .block-container {
            padding: 0.5rem !important;
            max-width: 100vw !important;
            width: 100% !important;
            overflow-x: hidden !important;
            box-sizing: border-box !important;
        }
        
        /* Constrain all elements inside main */
        .main [data-testid="stVerticalBlock"] {
            max-width: 100% !important;
            width: 100% !important;
        }
        
        /* FORCE horizontal layout on mobile - each column gets 25% width */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 3px !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Force columns to exactly 25% width each */
        [data-testid="column"] {
            min-width: 0 !important;
            width: calc(25% - 3px) !important;
            max-width: calc(25% - 3px) !important;
            flex: 0 0 calc(25% - 3px) !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }
        
        /* Compact the stats header on mobile */
        .stats-header {
            padding: 10px;
            gap: 5px;
        }
        
        .stat-box {
            min-width: 60px;
        }
        
        /* Smaller row cells on mobile */
        .row-cell {
            height: 60px;
            min-height: 60px;
            padding: 4px;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        
        .cell-logo {
            width: 35px;
            height: 35px;
        }
        
        .division-grid {
            width: 36px;
            height: 36px;
        }
        
        .division-logo {
            width: 17px;
            height: 17px;
        }
        
        .year-single {
            font-size: 1rem;
        }
        
        .year-num {
            font-size: 0.85rem;
        }
        
        .year-to {
            font-size: 0.5rem;
        }
        
        .qualifier-text {
            font-size: 0.7rem;
        }
        
        .qualifier-badge {
            font-size: 0.4rem;
            padding: 1px 4px;
        }
        
        .qualifier-label {
            font-size: 0.5rem;
        }
        
        .criteria-text {
            font-size: 0.65rem;
        }
        
        /* Make the green button smaller on mobile */
        [data-testid="column"]:last-child .stButton > button {
            height: 60px !important;
            min-height: 60px !important;
            font-size: 0.7rem !important;
            padding: 4px !important;
        }
    }
    
    /* Very small screens (phones) */
    @media (max-width: 480px) {
        .game-title {
            font-size: 1.2rem;
        }
        
        .stat-value {
            font-size: 1.2rem;
        }
        
        .stat-label {
            font-size: 0.5rem;
        }
        
        .completed-card {
            padding: 6px 8px;
        }
        
        .player-info-compact {
            font-size: 0.75rem;
        }
        
        /* Even more compact on very small screens */
        .team-logo, .row-logo {
            width: 25px !important;
            height: 25px !important;
        }
        
        .year-value {
            font-size: 0.7rem;
        }
        
        /* Tighter gaps */
        [data-testid="stHorizontalBlock"] {
            gap: 2px !important;
        }
        
        /* Even smaller row cells on very small screens */
        .row-cell {
            height: 50px;
            min-height: 50px;
            padding: 3px;
        }
        
        .cell-logo {
            width: 28px;
            height: 28px;
        }
        
        .division-grid {
            width: 30px;
            height: 30px;
        }
        
        .division-logo {
            width: 14px;
            height: 14px;
        }
        
        .year-single {
            font-size: 0.85rem;
        }
        
        .year-num {
            font-size: 0.7rem;
        }
        
        .qualifier-text {
            font-size: 0.6rem;
        }
        
        .qualifier-badge {
            font-size: 0.35rem;
            padding: 1px 3px;
        }
        
        .criteria-text {
            font-size: 0.55rem;
        }
        
        /* Smaller row cells on mobile */
        [data-testid="column"]:last-child .stButton > button {
            height: 50px !important;
            min-height: 50px !important;
            font-size: 0.6rem !important;
            padding: 2px !important;
        }
        
        /* Compact stats header */
        .stats-header {
            padding: 8px;
            gap: 3px;
        }
        
        .stat-box {
            min-width: 50px;
        }
    }
    
    /* Extra small screens (very narrow phones) */
    @media (max-width: 380px) {
        /* Force even tighter layout */
        [data-testid="stHorizontalBlock"] {
            gap: 1px !important;
        }
        
        .row-cell {
            height: 45px;
            min-height: 45px;
            padding: 2px;
            border-radius: 4px;
        }
        
        .cell-logo {
            width: 22px;
            height: 22px;
        }
        
        .division-grid {
            width: 24px;
            height: 24px;
        }
        
        .division-logo {
            width: 11px;
            height: 11px;
        }
        
        .year-single {
            font-size: 0.75rem;
        }
        
        .year-num {
            font-size: 0.6rem;
        }
        
        .year-to {
            font-size: 0.4rem;
        }
        
        .qualifier-text {
            font-size: 0.5rem;
        }
        
        .qualifier-badge {
            font-size: 0.3rem;
            padding: 1px 2px;
        }
        
        .criteria-text {
            font-size: 0.45rem;
        }
        
        [data-testid="column"]:last-child .stButton > button {
            height: 45px !important;
            min-height: 45px !important;
            font-size: 0.5rem !important;
            padding: 1px !important;
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
    
    # Modal state for player selection
    if 'active_modal_row' not in st.session_state:
        st.session_state.active_modal_row = None
    
    # Ensure expanded_rows has correct length
    if len(st.session_state.expanded_rows) < 5:
        st.session_state.expanded_rows = [False] * 5


def render_header():
    """Render the game header"""
    st.markdown("""
    <div class="game-header" style="border-bottom: none; padding-bottom: 0;">
        <h1 class="game-title"><span class="game-title-accent">StatPad</span> - NFL 🏈</h1>
    </div>
    """, unsafe_allow_html=True)


def render_easy_mode_toggle():
    """Render the Easy Mode toggle as a centered on/off switch beneath the stats header"""
    # Use CSS to center the toggle properly
    st.markdown('''
    <style>
    /* Center the Easy Mode toggle */
    [data-testid="stHorizontalBlock"]:has([data-testid="stToggle"]) {
        justify-content: center !important;
    }
    div[data-testid="stToggle"] {
        display: flex;
        justify-content: center;
    }
    </style>
    ''', unsafe_allow_html=True)
    
    # Render toggle with minimal margin
    easy_mode = st.toggle("Easy Mode", value=st.session_state.easy_mode, key="easy_mode_toggle")
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


def get_filtered_players_for_criteria(criteria: dict, stat_category: str) -> list:
    """Get player names filtered by criteria's eligible positions"""
    df = st.session_state.player_db
    stat_info = STAT_CATEGORIES.get(stat_category, {})
    
    # Determine eligible positions from qualifier or stat category
    qualifier_key = criteria.get('qualifier')
    if qualifier_key:
        qualifier_info = STAT_QUALIFIERS.get(qualifier_key, {})
        # Fantasy rank qualifiers have a specific position
        if qualifier_info.get('type') == 'fantasy_rank':
            eligible_positions = [qualifier_info.get('position')]
        else:
            eligible_positions = qualifier_info.get('eligible_positions', stat_info.get('eligible_positions', []))
    else:
        eligible_positions = stat_info.get('eligible_positions', [])
    
    # Filter players by position if we have eligible positions
    if eligible_positions and hasattr(df, 'filter'):
        import polars as pl
        filtered_df = df.filter(pl.col('position').is_in(eligible_positions))
        players = filtered_df.select('player').unique().to_series().to_list()
    elif eligible_positions:
        # Pandas fallback
        filtered_df = df[df['position'].isin(eligible_positions)]
        players = filtered_df['player'].unique().tolist()
    else:
        # No filtering
        players = get_all_player_names()
        return players
    
    return sorted([p for p in players if p is not None])


# Dialog function for player selection (centered modal)
@st.dialog("Add Player")
def show_player_dialog(row_index: int, criteria: dict, filtered_players: list, year_start: int, year_end: int):
    """Show centered dialog for player selection"""
    st.markdown("**Select a player to submit**")
    
    # Player search/select
    player_input = st.selectbox(
        "Player",
        options=[""] + filtered_players,
        key=f"dialog_player_{row_index}",
        index=0
    )
    
    # Year input (if not easy mode)
    if not st.session_state.easy_mode:
        year_input = st.number_input(
            "Year",
            min_value=year_start or 1999,
            max_value=year_end or 2024,
            value=year_end or 2024,
            key=f"dialog_year_{row_index}"
        )
    else:
        year_input = None
        st.info("Easy Mode: Best year will be auto-selected")
    
    # Submit button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit", key=f"dialog_submit_{row_index}", type="primary", use_container_width=True):
            if player_input:
                submit_player(row_index, player_input, year_input)
                st.rerun()
            else:
                st.error("Please select a player")


def render_input_row(row_index: int, criteria: dict, logo_info: dict, year_start: int, year_end: int, qualifier_display: str):
    """Render an input row for player submission - CSS Grid layout for mobile compatibility"""
    
    # Build logo HTML based on type (single, division, conference, league)
    if logo_info['type'] == 'division' and len(logo_info.get('urls', [])) == 4:
        logos = logo_info['urls']
        logo_html = f'''<div class="grid-division-logos">
            <img src="{logos[0]}" class="grid-div-logo">
            <img src="{logos[1]}" class="grid-div-logo">
            <img src="{logos[2]}" class="grid-div-logo">
            <img src="{logos[3]}" class="grid-div-logo">
        </div>'''
    else:
        logo_url = logo_info['urls'][0] if logo_info['urls'] else NFL_LOGO_URL
        logo_html = f'<img src="{logo_url}" class="grid-logo">'
    
    # Year display with "to" format
    if year_start and year_end:
        if year_start == year_end:
            year_html = f'<div class="grid-year-single">{year_start}</div>'
        else:
            year_html = f'''<div class="grid-year-range">
                <div class="grid-year-num">{year_start}</div>
                <div class="grid-year-to">to</div>
                <div class="grid-year-num">{year_end}</div>
            </div>'''
    else:
        year_html = ''
    
    # Qualifier display with label and career badge
    qualifier_key = criteria.get('qualifier')
    if qualifier_key:
        qualifier_info = STAT_QUALIFIERS.get(qualifier_key, {})
        qualifier_type = qualifier_info.get('qualifier_type', 'same_season')
        display_text = qualifier_info.get('display', qualifier_key)
        
        if qualifier_type == 'career':
            label_text = "CAREER"
            badge_text = "ANYTIME IN CAREER"
            badge_bg = "#b7a57a"
        else:
            label_text = ""
            badge_text = "SAME SEASON"
            badge_bg = "#4ade80"
        
        # Build qualifier HTML - single line to avoid rendering issues
        label_div = f'<div class="grid-qualifier-label">{label_text}</div>' if label_text else ''
        qualifier_html = f'<div class="grid-qualifier-content">{label_div}<div class="grid-qualifier-text">{display_text}</div><div class="grid-qualifier-badge" style="background:{badge_bg};">{badge_text}</div></div>'
    else:
        # No qualifier - show team/division/conference/position info
        criteria_parts = []
        if criteria.get('team'):
            team_info = NFL_TEAMS.get(criteria['team'], {})
            criteria_parts.append(team_info.get('name', criteria['team']))
        if criteria.get('division'):
            criteria_parts.append(criteria['division'])
        if criteria.get('conference'):
            criteria_parts.append(criteria['conference'])
        if criteria.get('position'):
            criteria_parts.append(criteria['position'])
        
        if criteria_parts:
            qualifier_html = f'<div class="grid-criteria-text">{", ".join(criteria_parts)}</div>'
        else:
            qualifier_html = ''
    
    # Render the entire row as a CSS Grid HTML element (first 3 cells)
    # The button will be rendered separately by Streamlit
    st.markdown(f'''
    <div class="game-row-grid">
        <div class="grid-cell grid-cell-logo">
            {logo_html}
        </div>
        <div class="grid-cell grid-cell-year">
            {year_html}
        </div>
        <div class="grid-cell grid-cell-qualifier">
            {qualifier_html}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Get filtered players for this row
    puzzle = st.session_state.puzzle
    stat_category = puzzle['stat_category']
    filtered_players = get_filtered_players_for_criteria(criteria, stat_category)
    
    # Green "➕ add player" button - rendered by Streamlit below the grid
    if st.button("➕ add player", key=f"add_player_btn_{row_index}", use_container_width=True):
        show_player_dialog(row_index, criteria, filtered_players, year_start, year_end)
    
    # Add spacing after the row
    st.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True)


def render_player_modal():
    """Render the player selection modal overlay"""
    if st.session_state.active_modal_row is None:
        return
    
    row_index = st.session_state.active_modal_row
    puzzle = st.session_state.puzzle
    criteria = puzzle['rows'][row_index]
    stat_category = puzzle['stat_category']
    year_start = criteria.get('year_start', 1999)
    year_end = criteria.get('year_end', 2024)
    
    # Get filtered players
    filtered_players = get_filtered_players_for_criteria(criteria, stat_category)
    
    # Modal container with dark overlay styling
    st.markdown("""
    <style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 9998;
    }
    .modal-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #2d2d2d;
        border-radius: 12px;
        padding: 20px;
        z-index: 9999;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .modal-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #fff;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create modal UI using Streamlit components
    st.markdown("---")
    st.markdown("### ADD PLAYER")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("✕ Close", key="close_modal"):
            st.session_state.active_modal_row = None
            st.rerun()
    
    # Player search/select
    player_input = st.selectbox(
        "Select a player",
        options=[""] + filtered_players,
        key=f"modal_player_select_{row_index}",
        index=0
    )
    
    # Year input (if not easy mode)
    if not st.session_state.easy_mode:
        year_input = st.number_input(
            "Year",
            min_value=year_start or 1999,
            max_value=year_end or 2024,
            value=year_end or 2024,
            key=f"modal_year_input_{row_index}"
        )
    else:
        year_input = None
    
    # Submit button
    if st.button("Submit", key=f"modal_submit_{row_index}", type="primary", use_container_width=True):
        if player_input:
            submit_player(row_index, player_input, year_input)
            st.session_state.active_modal_row = None
        else:
            st.error("Please select a player")
    
    st.markdown("---")


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
    """Render footer with How to Play and FAQ buttons - stacked vertically for mobile"""
    st.markdown("---")
    
    # Render buttons stacked vertically (full width) for better mobile compatibility
    if st.button("❓ How to Play", use_container_width=True, key="footer_how_to_play"):
        st.session_state.show_how_to_play = True
        st.session_state.show_faq = False
    
    if st.button("📊 FAQ", use_container_width=True, key="footer_faq"):
        st.session_state.show_faq = True
        st.session_state.show_how_to_play = False
    
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
                st.rerun()
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


def render_share_button():
    """Render Share Score button immediately after game completion"""
    if all(s is not None for s in st.session_state.submissions):
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        if st.button("📤 Share Score", type="primary", use_container_width=True, key="share_main"):
            share_score()


def main():
    """Main application entry point"""
    load_custom_css()
    init_session_state()
    
    render_header()
    render_stats_header()
    
    # Easy Mode toggle centered beneath the stats header
    render_easy_mode_toggle()
    
    st.markdown("---")
    
    # Render game rows
    for i in range(5):
        render_game_row(i)
    
    # Show modal if active
    render_player_modal()
    
    # Share button immediately after game rows
    render_share_button()
    
    render_footer()
    render_how_to_play()
    render_faq()


if __name__ == "__main__":
    main()