
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface Company {
  name: string;
  ticker: string;
  sector: string;
  description?: string;
  headquarters?: string;
  website?: string;
  currency?: string;
  exchange?: string;
  country?: string;
  logo?: string;
  marketCapitalization?: number;
  ipo?: string;
}

export interface Stock {
  c: number;
  d: number;
  dp: number;
  h: number;
  l: number;
  o: number;
  pc: number;
  t: number;
}

export interface AIInsights {
  ticker: string;
  ai_insights: string;
}

export interface SentimentDay {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
}

export interface SentimentTrendResponse {
  ticker: string;
  trend: SentimentDay[];
}

export interface SentimentTrendApiResponse {
  success: boolean;
  data: SentimentTrendResponse;
}

@Injectable({
  providedIn: 'root'
})
export class Api {

  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  getHealth() {
    return this.http.get(`${this.apiUrl}/health`);
  }

  getCompanies() {
    return this.http.get<Company[]>(`${this.apiUrl}/companies`);
  }

  searchCompany(query: string) {
    return this.http.get<Company[]>(
      `${this.apiUrl}/companies/search?query=${encodeURIComponent(query)}`
    );
  }

  getCompany(ticker: string) {
    return this.http.get<Company>(
      `${this.apiUrl}/companies/${encodeURIComponent(ticker)}`
    );
  }

  getCompanyProfile(ticker: string) {
    return this.http.get<Company>(
      `${this.apiUrl}/company-profile/${encodeURIComponent(ticker)}`
    );
  }

  getNews() {
    return this.http.get<any[]>(`${this.apiUrl}/news`);
  }

  getCompanyNews(ticker: string) {
    return this.http.get<any[]>(
      `${this.apiUrl}/news/${encodeURIComponent(ticker)}`
    );
  }

  getStock(ticker: string) {
    return this.http.get<Stock>(
      `${this.apiUrl}/stocks/${encodeURIComponent(ticker)}`
    );
  }

  getAIInsights(ticker: string) {
    return this.http.get<AIInsights>(
      `${this.apiUrl}/ai-insights/${encodeURIComponent(ticker)}`
    );
  }

  // Daily sentiment trend
  getSentimentTrend(ticker: string) {
    return this.http.get<SentimentTrendApiResponse>(
      `${this.apiUrl}/insights/trend/${encodeURIComponent(ticker)}`
    );
  }
}
