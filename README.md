# 🏈 NFL StatPad

A daily NFL trivia game inspired by [StatpadGame.com](https://www.statpadgame.com/). Pick 5 players to maximize a specific stat while meeting various criteria.

## 🎮 How to Play

1. Each day features a new stat category (Passing Yards, Rushing TDs, Receptions, etc.)
2. You have 5 rows, each with specific criteria (team, year range, position, division)
3. Submit a player + year that meets each row's requirements
4. Your score is the sum of that stat for all 5 players
5. Get ranked by percentile and earn tier badges!

## 🏆 Tiers

- 🟦 **Diamond** (100%) - Best possible answer!
- 🟨 **Gold** (90-99%) - Excellent choice
- ⬜ **Silver** (75-89%) - Good choice
- 🟫 **Bronze** (50-74%) - Decent choice
- ⬛ **Iron** (<50%) - Room for improvement

## 🚀 Features

- **Daily Puzzles**: New puzzle every day at midnight PST
- **Easy Mode**: Auto-selects the best year for any player
- **Tier System**: Visual feedback on how good your picks are
- **Top 5 Leaderboard**: See the best answers for each row
- **Share Score**: Wordle-style emoji sharing
- **Admin Override**: Set custom puzzles for specific dates

## 📊 Stats Available

### Passing
- Passing Yards, Passing TDs, Completions, Passer Rating

### Rushing
- Rushing Yards, Rushing TDs, Rushing Attempts

### Receiving
- Receiving Yards, Receiving TDs, Receptions

### Defense
- Sacks, Interceptions, Tackles, Forced Fumbles

## 🛠️ Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/crbrandt/stat_pad_nfl.git
cd stat_pad_nfl

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

## 📁 Project Structure

```
stat_pad_nfl/
├── app.py                    # Main Streamlit application
├── config.py                 # Game configuration
├── requirements.txt          # Python dependencies
├── data/
│   ├── __init__.py
│   ├── data_loader.py        # NFL data from Pro Football Reference
│   ├── image_fetcher.py      # Player headshots and team logos
│   └── cache/                # Cached data files
├── game/
│   ├── __init__.py
│   ├── puzzle_generator.py   # Daily puzzle generation
│   ├── validator.py          # Player submission validation
│   ├── scorer.py             # Scoring and percentile calculation
│   └── puzzle_overrides.json # Admin puzzle overrides
└── pages/
    └── admin.py              # Admin page for custom puzzles
```

## 🔧 Configuration

### Admin Access

Access the admin page at `/admin` to create custom puzzles.
Default password: `statpad2024` (change in `pages/admin.py`)

### Customizing Stats

Edit `config.py` to add or modify stat categories:

```python
STAT_CATEGORIES = {
    'your_stat': {
        'display_name': 'STAT',
        'type': 'CATEGORY',
        'eligible_positions': ['QB', 'RB'],
        'description': 'Your Stat Description'
    }
}
```

## 📈 Data Source

Player statistics are sourced from [Pro Football Reference](https://www.pro-football-reference.com/) via the `nfl_data_py` library.

Data coverage: 1999 - Present (Super Bowl Era focus)

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest new features
- Add new stat categories
- Improve the UI/UX

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

- Inspired by [StatpadGame.com](https://www.statpadgame.com/)
- Data from [Pro Football Reference](https://www.pro-football-reference.com/)
- Built with [Streamlit](https://streamlit.io/)