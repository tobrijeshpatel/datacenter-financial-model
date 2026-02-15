# Data Center Financial Model - Interactive Streamlit App

An interactive financial modeling tool for analyzing data center unit economics with real-time P&L calculations, cash flow projections, and payback analysis.

## 🌟 Features

- **Interactive Dashboard**: Adjust 20+ key variables and see instant results
- **Comprehensive P&L Analysis**: Revenue waterfall, cost breakdown, and margin analysis
- **Cash Flow Projection**: Multi-year projections with visual payback period
- **Executive Summary**: Key metrics, insights, and performance indicators
- **Export Capability**: Download P&L and cash flow data as CSV

## 📊 Key Variables You Can Adjust

### Capacity & Investment
- Data center capacity (GW)
- Capital cost per GW
- GPU & network equipment allocation

### Revenue
- Revenue rate per GW
- Utilization rate

### Operating Costs
- Power cost per kWh
- PUE (Power Usage Effectiveness)
- Various operational expenses (SG&A, maintenance, staffing, etc.)

### Financial Assumptions
- Depreciation schedules
- Tax rate
- Projection period

## 🚀 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Community Cloud](https://streamlit.io/cloud)**
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set main file path: `datacenter_model_app.py`
   - Click "Deploy"

3. **Your app will be live** at `https://[your-app-name].streamlit.app`

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/datacenter-financial-model.git
cd datacenter-financial-model

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run datacenter_model_app.py
```

The app will open in your browser at `http://localhost:8501`

### Option 3: Docker Deployment

```bash
# Build the Docker image
docker build -t datacenter-model .

# Run the container
docker run -p 8501:8501 datacenter-model
```

## 📁 Project Structure

```
datacenter-financial-model/
│
├── datacenter_model_app.py    # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── Dockerfile                 # Docker configuration (optional)
└── .gitignore                # Git ignore file
```

## 💡 Usage Tips

1. **Start with defaults**: The model comes pre-loaded with realistic assumptions
2. **Sensitivity analysis**: Change one variable at a time to understand impact
3. **Compare scenarios**: Take screenshots or export CSVs to compare different configurations
4. **Focus on key metrics**: 
   - EBIT margin should be >20% for healthy operations
   - Payback period <7 years is generally attractive
   - Power costs typically represent 30-50% of opex

## 📈 Model Logic

### Revenue
```
Revenue = Revenue per GW × Utilization × Capacity
```

### Power Costs
The model accounts for three power consumption scenarios:
- Active power (when capacity is utilized)
- Idle power (unused capacity baseline)
- Baseline power (always-on infrastructure)

All scaled by PUE (Power Usage Effectiveness)

### Cash Flow
```
Operating Cash Flow = EBIT × (1 - Tax Rate) + Depreciation
Cumulative Cash Flow tracks payback period
```

### Payback Period
Calculated as the year when cumulative cash flow turns positive

## 🛠️ Customization

You can easily customize this model by:

1. **Adding new cost categories**: Edit the P&L calculation function
2. **Changing visualization**: Modify the Plotly charts
3. **Adding scenarios**: Create preset scenario buttons
4. **Including debt**: Add interest calculations
5. **Advanced metrics**: Calculate NPV, IRR with different discount rates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this for your own analysis and projects.

## 🙋 Support

For questions or issues:
- Open an issue on GitHub
- Check the Streamlit documentation: https://docs.streamlit.io

## 🔮 Future Enhancements

- [ ] Scenario comparison (side-by-side analysis)
- [ ] Monte Carlo simulation for risk analysis
- [ ] Multi-site modeling
- [ ] Debt financing options
- [ ] Renewable energy integration modeling
- [ ] Custom export to PowerPoint/PDF reports

---

**Built with ❤️ using Streamlit**

*This model is for analytical purposes only and should not be used as the sole basis for investment decisions.*
