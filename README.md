
<h1 align="center">🌾 AkiLimo: AI-Powered Climate & Market Intelligence for Smallholder Farmers</h1>

Welcome to **AkiLimo**, a climate-smart agricultural intelligence platform designed to help smallholder farmers in Kenya maximize profitability by linking yield prediction, terrain-aware logistics, and real-time market insights.

This project bridges the gap between climate resilience and market access, turning agricultural risk into opportunity.

---

## 🎯 Problem Statement

Smallholder farmers in Kenya face a **Double Tragedy**:

- **Climate Uncertainty:** Irregular rainfall, prolonged droughts, and soil degradation lead to poor planting decisions and crop failure.
- **Market Isolation:** Even with a good harvest, farmers lack real-time price visibility and face poor rural infrastructure, forcing them to sell locally at low prices.

> **Result:** Farmers lose up to **30%** of their crop to climate shocks and another **40%** of profit to inefficient logistics and market opacity.

AkiLimo addresses this by integrating AI-driven yield forecasting, geospatial logistics, and market intelligence into one actionable platform.

---

## 👥 Our Team

| Name                | Role & Expertise                                      |
|---------------------|------------------------------------------------------|
| Nyambura Gachahi    | Project Lead, Climate Scientist & Meteorology Tech    |
| Immaculate Munde    | Lead Frontend Developer & UI/UX Designer             |
| Mogaka Mokaya       | Lead Backend Developer & Data Science Lead           |
| Washington Adiado   | Full-Stack Developer & Product Testing               |
| Arnold Achiki       | Backend Developer & System Integration Specialist     |

---

## 🛠 Solution: The 3-Layer Profit Pipeline

1. **AI Yield Forecasting (Production Layer)**
	- **Inputs:** Farmer location, soil data (AfSIS), rainfall anomalies (CHIRPS)
	- **Tech:** Random Forest Regressor trained on historical yield data
	- **Output:** Predicted yield volume + drought/flood risk score

2. **Geospatial Logistics Engine (Connectivity Layer)**
	- **Inputs:** Terrain elevation, road ruggedness, distance to markets
	- **Tech:** GeoPandas + NetworkX for “Effort Distance” (terrain-aware routing)
	- **Output:** Transport cost per route, accounting for road conditions

3. **Real-Time Market Intelligence (Profit Layer)**
	- **Inputs:** Live price feeds from major hubs (Nairobi, Nakuru, Eldoret)
	- **Tech:** Net Profit Comparison Algorithm
	- **Output:** Actionable sell/move recommendations

**Example Output:**
> “Sell in Nakuru—though price is lower, transport is cheaper. Net profit increases by 15%.”

---

## 🧠 Core Innovation: Net Profit Comparison

We calculate true profitability using:

```math
Net\ Profit_i = (Y \times P_i) - [C_{fixed} + (D_i \times (1+R_i) \times F)]
```

Where:
- $Y$ = Predicted yield (kg)
- $P_i$ = Price per kg in the market
- $C_{fixed}$ = Fixed production costs
- $D_i$ = Distance to market (km)
- $R_i$ = Road difficulty factor (0.0 for tarmac → 1.0+ for rough terrain)
- $F$ = Base transport cost per km

---

## 🛠 Technologies Used

**Frontend:**
- Next.js 15 + Tailwind CSS – responsive, mobile-first farmer interface
- Map integration for geospatial visualization

**Backend:**
- Python FastAPI – high-performance API for ML & geospatial processing
- Scikit-learn – Random Forest models for yield prediction
- GeoPandas & NetworkX – terrain-aware routing and logistics

**Data Sources:**
- CHIRPS (rainfall)
- AfSIS (soil data)
- Live market price APIs
- OpenStreetMap (road/terrain data)

---

## 📦 How to Clone & Run This Project

**Branch:** `new-feature`

### Step 1: Clone the Repository

```bash
git clone https://github.com/mokayaj857/shamba1.git
cd shamba1
git checkout new-feature
```

### Step 2: Set Up Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the root directory and add:

```env
CHIRPS_API_KEY=your_key
MARKET_API_KEY=your_key
```

### Step 4: Run the Application

```bash
# Start backend:
uvicorn main:app --reload

# Start frontend (from frontend/ directory):
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) to use the app.

---

## 🌐 Deployment

- **Frontend:** Vercel
- **Backend:** Railway / AWS EC2
- **Database:** PostgreSQL with PostGIS extension
- **Live demo:** _Coming Soon_

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repo
2. Create a feature branch:
	```bash
	git checkout -b feature/your-feature
	```
3. Commit changes:
	```bash
	git commit -m "Add your feature"
	```
4. Push:
	```bash
	git push origin feature/your-feature
	```
5. Open a Pull Request to the `new-feature` branch

---

## 🙏 Acknowledgments

- AI4SU Hackathon for the challenge inspiration
- Open Data Initiatives (CHIRPS, AfSIS, OpenStreetMap)
- Farmers and Cooperatives Kenya for real-world insights

---

## 📬 Contact Us

| Name                | Role & Area                        | Email                           |
|---------------------|------------------------------------|---------------------------------|
| Nyambura Gachahi    | Project Lead, Climate Science      | gacchahi@gmail.com              |
| Immaculate Munde    | Lead Frontend, UI/UX               | immaculatemunde@gmail.com       |
| Mogaka Mokaya       | Lead Backend, Data Science         | mokayaj857@gmail.com            |
| Washington Adiado   | Full-stack Developer, Testing      | washingtonowade200@gmail.com    |
| Arnold Achiki       | Backend Integration                | achikiarnold@gmail.com          |
| **Team Inquiries**  | General                            | team@akilimo.tech               |

**GitHub:** [github.com/mokayaj857/shamba1](https://github.com/mokayaj857/shamba1)

---

<p align="center">Thank you for exploring AkiLimo; where climate resilience meets market opportunity. 🌱🚀</p>
