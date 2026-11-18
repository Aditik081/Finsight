
import {
  Component,
  OnInit,
  OnDestroy,
  inject,
  signal,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import {
  Api,
  Company,
  AIInsights,
  SentimentTrendResponse
} from './services/api';

import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {

  companies: Company[] = [];
  searchText: string = '';
  searchResults: Company[] = [];

  selectedCompany = signal<Company | null>(null);
  news = signal<any[]>([]);
  stock = signal<any>(null);

  stockLoading: boolean = false;
  stockError: string = '';

  aiInsights = signal<string>('');
  aiLoading: boolean = false;
  aiError: string = '';

  // Sentiment trend state
  sentimentTrend = signal<SentimentTrendResponse | null>(null);
  sentimentTrendLoading: boolean = false;
  sentimentTrendError: string = '';

  private chart: Chart | null = null;

  private api = inject(Api);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {

    this.api.getCompanies().subscribe({
      next: (data: Company[]) => {
        this.companies = data;
        console.log('Companies loaded:', this.companies);
      },
      error: (err) => {
        console.error('Companies fetch failed:', err);
      }
    });

  }

  searchCompany(): void {

    const query = this.searchText.trim();

    if (!query) {
      this.searchResults = [];
      return;
    }

    this.api.searchCompany(query).subscribe({
      next: (data: Company[]) => {
        this.searchResults = data;
      },
      error: (err) => {
        console.error('Company search failed:', err);
        this.searchResults = [];
      }
    });

  }

  openCompany(ticker: string): void {

    console.log('Selected ticker:', ticker);

    // Reset previous company data
    this.selectedCompany.set(null);
    this.stock.set(null);
    this.news.set([]);

    this.aiInsights.set('');
    this.aiError = '';
    this.aiLoading = true;

    this.sentimentTrend.set(null);
    this.sentimentTrendLoading = true;
    this.sentimentTrendError = '';

    this.destroyChart();

    this.stockLoading = true;
    this.stockError = '';

    // 1. Company details
    this.api.getCompany(ticker).subscribe({

      next: (data: Company) => {
        console.log('Company details:', data);
        this.selectedCompany.set(data);
      },

      error: (err) => {
        console.error('Company details failed:', err);
        this.stockError = 'Unable to load company details.';
      }

    });

    // 2. Stock data
    this.api.getStock(ticker).subscribe({

      next: (data) => {

        console.log('Stock data:', data);

        this.stock.set(data);
        this.stockLoading = false;

        if (!data || data.c == null || data.c === 0) {
          this.stockError = 'Stock price is currently unavailable.';
        }

      },

      error: (err) => {

        console.error('Stock fetch failed:', err);

        this.stock.set(null);
        this.stockLoading = false;
        this.stockError = 'Unable to load stock data.';

      }

    });

    // 3. Company news
    this.api.getCompanyNews(ticker).subscribe({

      next: (data) => {

        console.log('Company news:', data);
        this.news.set(data);

      },

      error: (err) => {

        console.error('News fetch failed:', err);
        this.news.set([]);

      }

    });

    // 4. AI insights
    this.api.getAIInsights(ticker).subscribe({

      next: (data: AIInsights) => {

        console.log('AI Insights:', data);

        this.aiInsights.set(data.ai_insights);
        this.aiLoading = false;

      },

      error: (err) => {

        console.error('AI Insights fetch failed:', err);

        this.aiInsights.set('');
        this.aiLoading = false;
        this.aiError = 'Unable to generate AI insights.';

      }

    });

    // 5. Daily sentiment trend
    this.api.getSentimentTrend(ticker).subscribe({

      next: (response) => {

        console.log('Sentiment trend:', response);

        this.sentimentTrend.set(response.data);
        this.sentimentTrendLoading = false;

        // Update Angular view before accessing canvas
        this.cdr.detectChanges();

        this.renderSentimentChart();

      },

      error: (err) => {

        console.error('Sentiment trend fetch failed:', err);

        this.sentimentTrend.set(null);
        this.sentimentTrendLoading = false;
        this.sentimentTrendError =
          'Unable to load sentiment trend.';

      }

    });

  }

  // Create line chart
  private renderSentimentChart(): void {

    this.destroyChart();

    const canvas = document.getElementById(
      'sentimentChart'
    ) as HTMLCanvasElement | null;

    const trendData = this.sentimentTrend();

    if (!canvas || !trendData || trendData.trend.length === 0) {
      return;
    }

    const labels = trendData.trend.map(
      item => item.date
    );

    const positiveData = trendData.trend.map(
      item => item.positive
    );

    const negativeData = trendData.trend.map(
      item => item.negative
    );

    const neutralData = trendData.trend.map(
      item => item.neutral
    );

    this.chart = new Chart(canvas, {

      type: 'line',

      data: {

        labels: labels,

        datasets: [

          {
            label: 'Positive News',
            data: positiveData,
            borderColor: '#16a36a',
            backgroundColor: 'rgba(22, 163, 106, 0.12)',
            borderWidth: 3,
            tension: 0.35,
            fill: false
          },

          {
            label: 'Negative News',
            data: negativeData,
            borderColor: '#e04444',
            backgroundColor: 'rgba(224, 68, 68, 0.12)',
            borderWidth: 3,
            tension: 0.35,
            fill: false
          },

          {
            label: 'Neutral News',
            data: neutralData,
            borderColor: '#d69b25',
            backgroundColor: 'rgba(214, 155, 37, 0.12)',
            borderWidth: 3,
            tension: 0.35,
            fill: false
          }

        ]

      },

      options: {

        responsive: true,
        maintainAspectRatio: false,

        plugins: {

          legend: {
            display: true,
            position: 'top'
          },

          tooltip: {
            enabled: true
          }

        },

        scales: {

          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            },
            title: {
              display: true,
              text: 'Number of news articles'
            }
          },

          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }

        }

      }

    });

  }

  private destroyChart(): void {

    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

  }

  ngOnDestroy(): void {
    this.destroyChart();
  }

}
