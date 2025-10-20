# Example Cursor Background Agent Prompt

This is an example of the type of prompt that will be generated for Cursor background agents.

## Usage Instructions

1. **Open Cursor** and press `Ctrl+Shift+B` (or `⌘B` on Mac)
2. **Click "New Background Agent"**
3. **Copy the contents** of any generated prompt file from the `cursor_tasks/` directory
4. **Paste into the agent prompt field**
5. **The agent will create a new branch** and implement the trading strategy

## Generated Files

All generated prompts are saved in the `cursor_tasks/` directory with timestamps and strategy names.

## Prerequisites

- **Disable Privacy Mode** in Cursor settings
- **Enable usage-based spending** (minimum $10 funding)
- **Connect GitHub repository** with read-write privileges
- **Configure environment** with `.cursor/environment.json`

## Example Workflow

```bash
# Run analysis and generate prompt
python main.py --tickers AAPL MSFT --strategy momentum

# Test API connections
python main.py --test

# Check account status
python main.py --status
```

The system will automatically generate comprehensive prompts that include:
- Real-time financial data analysis
- Technical and fundamental analysis
- Market sentiment and news
- Complete trading strategy implementation requirements
- Risk management specifications
- Testing and validation requirements