"""Game logic module for NFL StatPad Game"""
from .puzzle_generator import get_daily_puzzle, generate_puzzle, save_override
from .validator import validate_player_submission, find_player_best_year, search_players
from .scorer import score_submission, get_top_5_for_criteria, calculate_total_score, generate_share_text