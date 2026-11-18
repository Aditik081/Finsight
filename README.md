
# FinSight AI – Financial News Intelligence Platform

FinSight AI is a full-stack financial intelligence platform that helps users analyze stock market information, explore company-related news, and understand market sentiment using AI-powered insights.

## Features

- **Company Search:** Search companies using their names or stock tickers.
- **Stock Information:** View stock prices and company profiles.
- **Financial News:** Get the latest company-related financial news.
- **Sentiment Analysis:** Classify news articles as Positive, Negative, or Neutral.
- **AI-Powered Insights:** Generate summaries and insights from recent financial news.
- **Sentiment Analytics:** Visualize news sentiment distribution through charts.

## Tech Stack

| Component           | Technologies                      |
| Frontend            | Angular 20, TypeScript, HTML, CSS |
| Backend             | Python, FastAPI                   |
| Database            | MongoDB                           |
| Data Visualization  | Chart.js                          |
| Stock & News API    | Finnhub                           |
| AI Integration      | Groq API                          |

## Architecture

1. Angular provides the interactive user interface.
2. FastAPI handles frontend requests through REST APIs.
3. Finnhub provides stock market data and financial news.
4. MongoDB stores company and news information.
5. Sentiment analysis classifies financial articles.
6. The AI module generates insights from recent news.
7. Results are displayed through charts and dashboard components.

## Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/Aditik081/Finsight.git
cd Finsight
```

### Backend Setup

```bash
cd backend
python -m venv venv
```

Activate the virtual environment and install the required dependencies.

Create a `.env` file inside the backend folder and add your API credentials:

```env
MONGO_URI=your_mongodb_connection_string
FINNHUB_API_KEY=your_finnhub_api_key
GROQ_API_KEY=your_groq_api_key
```

Run the backend:

```bash
uvicorn main:app --reload
```

Backend: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

Open another terminal:

```bash
cd frontend/finsight-frontend
npm install
ng serve
```

Open `http://localhost:4200` in your browser.

## Future Enhancements

- Advanced financial analytics.
- Improved sentiment trend visualizations.
- Expanded Indian and international market coverage.
- Enhanced AI-generated insights.

## Author

**Aditi Kumari**

GitHub: [@Aditik081](https://github.com/Aditik081)

---

*FinSight AI – Turning Financial News into Meaningful Insights.*
