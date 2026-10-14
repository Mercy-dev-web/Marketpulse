# MarketPulse 📈

**AI-assisted Marketing Intelligence & Campaign Analytics**

MarketPulse helps small businesses explore campaign performance, understand marketing metrics, and turn campaign data into practical next steps.

## Features

- Upload campaign datasets in CSV, XLSX, or XLS format
- Calculate click-through rate (CTR), conversion rate, cost per conversion, and return on ad spend (ROAS) when the required columns are available
- Compare campaign and channel performance
- Explore charts and rule-based marketing insights
- Ask the AI Marketing Assistant questions about the uploaded campaign data
- Generate a prioritized AI Campaign Action Plan with metric-based evidence, suggested tests, and success measures
- Export analyzed results

## Technology stack

- Python
- Streamlit
- Pandas and NumPy
- Plotly
- Groq API with the open-weight `openai/gpt-oss-20b` model for AI responses

## Run locally

1. Clone the repository:

   ```bash
   git clone https://github.com/Mercy-dev-web/Marketpulse.git
   cd Marketpulse
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Groq API key to Streamlit secrets. For local development, create `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

   Do not commit your API key or share it publicly.

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The AI Marketing Assistant requires a valid Groq API key. The analytics pages use Python-based calculations; the AI assistant is a separate feature that generates explanations and recommendations.

## Using your own data

Upload a CSV or Excel campaign file through the app. MarketPulse maps supported column names and calculates metrics when the necessary source fields are present. Available metrics depend on the columns in your file.

For meaningful ROAS comparisons, spend and revenue should use the same currency. Check that campaign names, channel names, spend, revenue, clicks, impressions, and conversion fields are consistent before interpreting results.

## AI and data handling

When you use the AI Marketing Assistant, your question and aggregated campaign/channel metrics are sent to Groq to generate a response. Do not upload or include personal information, customer-level records, credentials, or confidential business data unless you have permission to share it with that service.

AI recommendations are decision support, not guarantees. Review the supporting metrics and consider business goals, margins, attribution quality, and lead quality before changing spend.

## Important notes

- Sample campaign figures, where used, are fictional.
- ROAS is attributed revenue divided by advertising spend; it is not the same as profit.
- Recommendations depend on the quality and completeness of the uploaded data.

## Roadmap

- [x] Campaign analytics dashboard
- [x] Campaign data upload and downloadable results
- [x] AI Marketing Assistant
- [x] One-click AI Campaign Action Plan
- [ ] More robust data validation and automated tests
- [ ] Additional campaign visualizations
- [ ] Contributor documentation

## Contributing

Ideas, bug reports, documentation improvements, and code contributions are welcome. Please open an issue to discuss substantial changes before submitting a pull request.

## License

No license has been added yet. Until a license is included in the repository, do not assume the code is available for reuse under an open-source license.
