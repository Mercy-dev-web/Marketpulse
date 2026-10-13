# MarketPulse 📈

**Marketing Intelligence & Campaign Analytics**

MarketPulse is an open-source marketing analytics application that helps businesses understand campaign performance and make more informed, data-driven marketing decisions.

## Features

- Upload campaign data using CSV files
- Calculate click-through rate (CTR)
- Calculate conversion rate
- Calculate cost per lead
- Calculate return on ad spend (ROAS)
- Compare campaign spending and revenue
- Generate rule-based marketing insights
- Download analyzed campaign results

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/marketpulse.git
cd marketpulse
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

## CSV Format

Your campaign CSV must contain these columns:

`Campaign, Spend, Impressions, Clicks, Leads, Sales, Revenue`

Spend and revenue should use the same currency for meaningful comparisons.

## Important Notes

- The included sample campaign figures are fictional.
- ROAS measures attributed revenue relative to advertising spend. It does not measure profit.
- Recommendations are descriptive and should be evaluated alongside campaign goals, margins and lead quality.

## Roadmap

- [x] Initial campaign analytics dashboard
- [x] CSV upload and downloadable analysis
- [ ] More robust data validation and automated tests
- [ ] Open-weight AI explanations
- [ ] Additional campaign visualizations
- [ ] Contributor documentation

## Contributing

Contributions, suggestions, bug reports and improvements are welcome. Please open an issue to discuss substantial changes before submitting a pull request.

## License

MIT License (planned; add a LICENSE file before distributing the project under this license).

