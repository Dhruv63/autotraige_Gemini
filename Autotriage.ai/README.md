# AutoTriage.AI


#alert since ollama runs locally the hosted model isn't showing any new output


> Let AI diagnose your support mess

AutoTriage.AI is an AI-powered system that automatically analyzes, categorizes, and provides solutions for customer support tickets.

## Features

- Automatic ticket analysis and categorization
- AI-driven solution recommendations
- Sentiment analysis
- Priority assessment
- Similar case matching
- Resolution time estimation
- Interactive web interface
- Command-line interface

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Dhruv63/Autotriage.ai.git
   cd Autotriage.ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Gemini API Key:
   - Get your API key from Google AI Studio
   - Create a file named `.env` in the main project directory
   - Add your API key to the `.env` file like this:
     ```
     GEMINI_API_KEY="YOUR_API_KEY_HERE"
     ```

## Usage

### Web Interface

Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

### Command Line Interface

Run the example script:
```bash
python example.py
```

Or use the support pipeline directly:
```bash
python run_support.py
```

## Project Structure

```
autotriage-ai/
├── streamlit_app.py          # Web interface
├── example.py                # Example usage
├── run_support.py            # CLI interface
├── requirements.txt          # Dependencies
└── support_ai/              # Main package
    ├── __init__.py
    ├── pipeline.py          # Main processing pipeline
    ├── analyzer.py          # Ticket analysis logic
    ├── data_loader.py       # Data loading utilities
    └── agents/              # AI agents
        ├── __init__.py
        ├── base.py          # Base agent class
        ├── extractor.py     # Issue extraction
        ├── summarizer.py    # Text summarization
        └── recommender.py   # Solution recommendation
```


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
