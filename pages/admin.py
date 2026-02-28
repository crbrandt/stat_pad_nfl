"""
Admin page for NFL StatPad Game
Allows setting custom puzzles for specific dates
"""
import streamlit as st
import json
from datetime import date, datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STAT_CATEGORIES, NFL_TEAMS, DIVISIONS, CONFERENCES, STAT_QUALIFIERS, get_compatible_qualifiers
from game.puzzle_generator import (
    save_override, load_overrides, get_puzzle_date, 
    update_puzzle_row, get_current_puzzle_for_editing, format_criteria_display
)

st.set_page_config(
    page_title="NFL StatPad - Admin",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ NFL StatPad Admin")
st.markdown("Create custom puzzles for specific dates")

# Password protection (simple)
password = st.text_input("Admin Password", type="password")
if password != "statpad2024":  # Change this password!
    st.warning("Enter admin password to continue")
    st.stop()

st.success("✓ Authenticated")

# Date selection
st.header("1. Select Date")
puzzle_date = st.date_input(
    "Puzzle Date",
    value=date.today(),
    min_value=date.today(),
    max_value=date.today() + timedelta(days=365)
)

# Stat category selection
st.header("2. Select Stat Category")
stat_options = {k: f"{v['display_name']} ({v['type']})" for k, v in STAT_CATEGORIES.items()}
stat_category = st.selectbox(
    "Stat to Maximize",
    options=list(stat_options.keys()),
    format_func=lambda x: stat_options[x]
)

stat_info = STAT_CATEGORIES[stat_category]

# Row criteria
st.header("3. Configure Row Criteria")

# Get compatible qualifiers for the selected stat category
compatible_qualifiers = get_compatible_qualifiers(stat_category)

# Build qualifier options with display names
qualifier_options = {"none": "No Qualifier"}
for q_key in compatible_qualifiers:
    q_info = STAT_QUALIFIERS.get(q_key, {})
    q_display = q_info.get('display', q_key)
    q_type = q_info.get('qualifier_type', 'same_season')
    type_label = " (Career)" if q_type == 'career' else ""
    qualifier_options[q_key] = f"{q_display}{type_label}"

rows = []
for i in range(5):
    st.subheader(f"Row {i + 1}")
    
    # First row: Criteria type selection
    col1, col2 = st.columns(2)
    
    with col1:
        criteria_type = st.selectbox(
            "Criteria Type",
            options=["team", "division", "conference", "position", "qualifier_only"],
            format_func=lambda x: {
                "team": "🏟️ Team",
                "division": "📍 Division", 
                "conference": "🏈 Conference",
                "position": "👤 Position",
                "qualifier_only": "📊 Qualifier Only (Any Team)"
            }.get(x, x),
            key=f"criteria_type_{i}"
        )
    
    with col2:
        if criteria_type == "team":
            team_options = {k: v['name'] for k, v in NFL_TEAMS.items()}
            criteria_value = st.selectbox(
                "Team",
                options=list(team_options.keys()),
                format_func=lambda x: team_options[x],
                key=f"team_{i}"
            )
        elif criteria_type == "division":
            criteria_value = st.selectbox(
                "Division",
                options=DIVISIONS,
                key=f"division_{i}"
            )
        elif criteria_type == "conference":
            criteria_value = st.selectbox(
                "Conference",
                options=CONFERENCES,
                key=f"conference_{i}"
            )
        elif criteria_type == "position":
            criteria_value = st.selectbox(
                "Position",
                options=stat_info['eligible_positions'],
                key=f"position_{i}"
            )
        else:
            criteria_value = None
            st.info("Qualifier-only row (no team restriction)")
    
    # Second row: Year range and qualifier
    col3, col4, col5 = st.columns(3)
    
    with col3:
        year_start = st.number_input(
            "Year Start",
            min_value=1999,
            max_value=2024,
            value=2015,
            key=f"year_start_{i}"
        )
    
    with col4:
        year_end = st.number_input(
            "Year End",
            min_value=1999,
            max_value=2024,
            value=2024,
            key=f"year_end_{i}"
        )
    
    with col5:
        selected_qualifier = st.selectbox(
            "Qualifier",
            options=list(qualifier_options.keys()),
            format_func=lambda x: qualifier_options[x],
            key=f"qualifier_{i}"
        )
    
    # Build row criteria
    row_criteria = {
        'team': None,
        'year_start': year_start,
        'year_end': year_end,
        'position': None,
        'division': None,
        'conference': None,
        'qualifier': None,
        'qualifier_type': None,
        'qualifier_display': None,
    }
    
    if criteria_type == "team":
        row_criteria['team'] = criteria_value
    elif criteria_type == "division":
        row_criteria['division'] = criteria_value
    elif criteria_type == "conference":
        row_criteria['conference'] = criteria_value
    elif criteria_type == "position":
        row_criteria['position'] = criteria_value
    
    # Add qualifier if selected
    if selected_qualifier != "none":
        q_info = STAT_QUALIFIERS.get(selected_qualifier, {})
        row_criteria['qualifier'] = selected_qualifier
        row_criteria['qualifier_type'] = q_info.get('qualifier_type', 'same_season')
        row_criteria['qualifier_display'] = q_info.get('display', selected_qualifier)
    
    rows.append(row_criteria)
    
    st.markdown("---")

# Preview
st.header("4. Preview Puzzle")

puzzle_config = {
    'date': puzzle_date.isoformat(),
    'stat_category': stat_category,
    'stat_display': stat_info['display_name'],
    'stat_type': stat_info['type'],
    'stat_description': stat_info['description'],
    'rows': rows,
}

st.json(puzzle_config)

# Save
st.header("5. Save Override")

if st.button("💾 Save Puzzle Override", type="primary"):
    save_override(puzzle_date, puzzle_config)
    st.success(f"✓ Puzzle saved for {puzzle_date}")
    st.balloons()

# View existing overrides
st.header("📋 Existing Overrides")

overrides = load_overrides()
if overrides:
    for date_str, config in overrides.items():
        with st.expander(f"{date_str} - {config.get('stat_display', 'Unknown')}"):
            st.json(config)
            if st.button(f"Delete {date_str}", key=f"delete_{date_str}"):
                del overrides[date_str]
                with open(os.path.join(os.path.dirname(__file__), '..', 'game', 'puzzle_overrides.json'), 'w') as f:
                    json.dump(overrides, f, indent=2)
                st.success(f"Deleted override for {date_str}")
                st.rerun()
else:
    st.info("No overrides configured")


# Individual Row Editing Section
st.header("✏️ Edit Individual Row (Today's Puzzle)")
st.markdown("Edit a single row without changing the rest of the puzzle")

# Get current puzzle for today
today = get_puzzle_date()
current_puzzle = get_current_puzzle_for_editing(today)

st.subheader(f"Current Puzzle: {current_puzzle['stat_display']} ({current_puzzle['stat_type']})")

# Show current rows with edit buttons
for row_idx, row in enumerate(current_puzzle['rows']):
    col_display, col_edit = st.columns([3, 1])
    
    with col_display:
        criteria_text = format_criteria_display(row)
        qualifier_text = f" | Qualifier: {row.get('qualifier_display', 'None')}" if row.get('qualifier') else ""
        st.markdown(f"**Row {row_idx + 1}:** {criteria_text}{qualifier_text}")
    
    with col_edit:
        if st.button(f"Edit Row {row_idx + 1}", key=f"edit_row_{row_idx}"):
            st.session_state[f'editing_row_{row_idx}'] = True

# Edit forms for each row
for row_idx in range(5):
    if st.session_state.get(f'editing_row_{row_idx}', False):
        st.markdown("---")
        st.subheader(f"✏️ Editing Row {row_idx + 1}")
        
        current_row = current_puzzle['rows'][row_idx]
        
        # Get compatible qualifiers for current stat category
        edit_compatible_qualifiers = get_compatible_qualifiers(current_puzzle['stat_category'])
        edit_qualifier_options = {"none": "No Qualifier"}
        for q_key in edit_compatible_qualifiers:
            q_info = STAT_QUALIFIERS.get(q_key, {})
            q_display = q_info.get('display', q_key)
            q_type = q_info.get('qualifier_type', 'same_season')
            type_label = " (Career)" if q_type == 'career' else ""
            edit_qualifier_options[q_key] = f"{q_display}{type_label}"
        
        # Determine current criteria type
        if current_row.get('team'):
            default_type = "team"
        elif current_row.get('division'):
            default_type = "division"
        elif current_row.get('conference'):
            default_type = "conference"
        elif current_row.get('position'):
            default_type = "position"
        else:
            default_type = "qualifier_only"
        
        col1, col2 = st.columns(2)
        
        with col1:
            edit_criteria_type = st.selectbox(
                "Criteria Type",
                options=["team", "division", "conference", "position", "qualifier_only"],
                format_func=lambda x: {
                    "team": "🏟️ Team",
                    "division": "📍 Division", 
                    "conference": "🏈 Conference",
                    "position": "👤 Position",
                    "qualifier_only": "📊 Qualifier Only"
                }.get(x, x),
                index=["team", "division", "conference", "position", "qualifier_only"].index(default_type),
                key=f"edit_criteria_type_{row_idx}"
            )
        
        with col2:
            if edit_criteria_type == "team":
                team_options = {k: v['name'] for k, v in NFL_TEAMS.items()}
                default_team = current_row.get('team', list(NFL_TEAMS.keys())[0])
                edit_criteria_value = st.selectbox(
                    "Team",
                    options=list(team_options.keys()),
                    format_func=lambda x: team_options[x],
                    index=list(team_options.keys()).index(default_team) if default_team in team_options else 0,
                    key=f"edit_team_{row_idx}"
                )
            elif edit_criteria_type == "division":
                default_div = current_row.get('division', DIVISIONS[0])
                edit_criteria_value = st.selectbox(
                    "Division",
                    options=DIVISIONS,
                    index=DIVISIONS.index(default_div) if default_div in DIVISIONS else 0,
                    key=f"edit_division_{row_idx}"
                )
            elif edit_criteria_type == "conference":
                default_conf = current_row.get('conference', CONFERENCES[0])
                edit_criteria_value = st.selectbox(
                    "Conference",
                    options=CONFERENCES,
                    index=CONFERENCES.index(default_conf) if default_conf in CONFERENCES else 0,
                    key=f"edit_conference_{row_idx}"
                )
            elif edit_criteria_type == "position":
                current_stat_info = STAT_CATEGORIES[current_puzzle['stat_category']]
                default_pos = current_row.get('position', current_stat_info['eligible_positions'][0])
                edit_criteria_value = st.selectbox(
                    "Position",
                    options=current_stat_info['eligible_positions'],
                    index=current_stat_info['eligible_positions'].index(default_pos) if default_pos in current_stat_info['eligible_positions'] else 0,
                    key=f"edit_position_{row_idx}"
                )
            else:
                edit_criteria_value = None
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            edit_year_start = st.number_input(
                "Year Start",
                min_value=1999,
                max_value=2024,
                value=current_row.get('year_start', 2015),
                key=f"edit_year_start_{row_idx}"
            )
        
        with col4:
            edit_year_end = st.number_input(
                "Year End",
                min_value=1999,
                max_value=2024,
                value=current_row.get('year_end', 2024),
                key=f"edit_year_end_{row_idx}"
            )
        
        with col5:
            current_qualifier = current_row.get('qualifier', 'none') or 'none'
            edit_selected_qualifier = st.selectbox(
                "Qualifier",
                options=list(edit_qualifier_options.keys()),
                format_func=lambda x: edit_qualifier_options[x],
                index=list(edit_qualifier_options.keys()).index(current_qualifier) if current_qualifier in edit_qualifier_options else 0,
                key=f"edit_qualifier_{row_idx}"
            )
        
        # Save/Cancel buttons
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.button(f"💾 Save Row {row_idx + 1}", key=f"save_row_{row_idx}", type="primary"):
                # Build new criteria
                new_criteria = {
                    'team': None,
                    'year_start': edit_year_start,
                    'year_end': edit_year_end,
                    'position': None,
                    'division': None,
                    'conference': None,
                    'qualifier': None,
                    'qualifier_type': None,
                    'qualifier_display': None,
                }
                
                if edit_criteria_type == "team":
                    new_criteria['team'] = edit_criteria_value
                elif edit_criteria_type == "division":
                    new_criteria['division'] = edit_criteria_value
                elif edit_criteria_type == "conference":
                    new_criteria['conference'] = edit_criteria_value
                elif edit_criteria_type == "position":
                    new_criteria['position'] = edit_criteria_value
                
                if edit_selected_qualifier != "none":
                    q_info = STAT_QUALIFIERS.get(edit_selected_qualifier, {})
                    new_criteria['qualifier'] = edit_selected_qualifier
                    new_criteria['qualifier_type'] = q_info.get('qualifier_type', 'same_season')
                    new_criteria['qualifier_display'] = q_info.get('display', edit_selected_qualifier)
                
                # Update just this row
                update_puzzle_row(today, row_idx, new_criteria)
                st.session_state[f'editing_row_{row_idx}'] = False
                st.success(f"✓ Row {row_idx + 1} updated!")
                st.rerun()
        
        with col_cancel:
            if st.button(f"Cancel", key=f"cancel_row_{row_idx}"):
                st.session_state[f'editing_row_{row_idx}'] = False
                st.rerun()
