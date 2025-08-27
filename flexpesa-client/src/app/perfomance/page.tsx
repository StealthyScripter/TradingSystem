'use client'
import Header from "@/components/Header";
import PortfolioCard from "@/components/PortfolioCard";
import { useState } from "react";
import { Plus } from "lucide-react";

// Type definitions
export interface BenchmarkComparison {
  name: string;
  performance: number; // positive means outperform, negative means underperform
}

export interface RiskMetric {
  beta: number;
  volatility: number;
  alpha: number;
  expenseRatio: number;
  sortinoRatio: number;
  valueAtRisk: number;
}

export interface PortfolioData {
  id: string;
  name: string;
  type: string;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  benchmarkComparisons: BenchmarkComparison[];
  riskMetrics: RiskMetric;
  totalValue: number;
  lastUpdated: string;
}

export default function PerformancePage() {
  const [portfolios, setPortfolios] = useState<PortfolioData[]>(mockPortfolios);
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddPortfolio = () => {
    setShowAddForm(true);
    // In real implementation, this would open a modal or navigate to add form
    console.log("Opening add portfolio form...");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header />

        {/* Page Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            {/* Add Portfolio Button */}
            <button
              onClick={handleAddPortfolio}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <Plus size={20} />
              Add Portfolio
            </button>
          </div>
        </div>

        {/* Portfolio Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {portfolios.map((portfolio) => (
            <PortfolioCard
              key={portfolio.id}
              portfolio={portfolio}
            />
          ))}
        </div>

        {/* Summary Stats */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Portfolio Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                ${mockPortfolios.reduce((sum, p) => sum + p.totalValue, 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Total Portfolio Value</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {portfolios.length}
              </div>
              <div className="text-sm text-gray-600">Active Portfolios</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {(mockPortfolios.reduce((sum, p) => sum + p.totalReturn, 0) / portfolios.length).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Avg Total Return</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {(mockPortfolios.reduce((sum, p) => sum + p.sharpeRatio, 0) / portfolios.length).toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Avg Sharpe Ratio</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Mock data for demonstration
const mockPortfolios: PortfolioData[] = [
  {
    id: "1",
    name: "Tech Growth Portfolio",
    type: "Growth",
    totalReturn: 12.4,
    annualizedReturn: 8.7,
    sharpeRatio: 1.23,
    maxDrawdown: -18.2,
    totalValue: 145600,
    lastUpdated: "2025-08-27",
    benchmarkComparisons: [
      { name: "S&P 500", performance: 2.1 },
      { name: "NASDAQ 100", performance: -1.3 },
      { name: "Total Stock Market", performance: 3.4 },
      { name: "60/40 Portfolio", performance: 5.7 }
    ],
    riskMetrics: {
      beta: 1.15,
      volatility: 16.8,
      alpha: 2.3,
      expenseRatio: 0.68,
      sortinoRatio: 0.89,
      valueAtRisk: -4820
    }
  },
  {
    id: "2",
    name: "Balanced Portfolio",
    type: "Balanced",
    totalReturn: 8.2,
    annualizedReturn: 6.5,
    sharpeRatio: 0.98,
    maxDrawdown: -12.1,
    totalValue: 89400,
    lastUpdated: "2025-08-27",
    benchmarkComparisons: [
      { name: "S&P 500", performance: -1.8 },
      { name: "NASDAQ 100", performance: -4.2 },
      { name: "Total Stock Market", performance: -0.6 },
      { name: "60/40 Portfolio", performance: 1.2 }
    ],
    riskMetrics: {
      beta: 0.85,
      volatility: 11.2,
      alpha: 0.8,
      expenseRatio: 0.45,
      sortinoRatio: 1.12,
      valueAtRisk: -2150
    }
  },
  {
    id: "3",
    name: "Conservative Portfolio",
    type: "Conservative",
    totalReturn: 5.8,
    annualizedReturn: 4.2,
    sharpeRatio: 0.76,
    maxDrawdown: -6.4,
    totalValue: 67800,
    lastUpdated: "2025-08-27",
    benchmarkComparisons: [
      { name: "S&P 500", performance: -4.2 },
      { name: "NASDAQ 100", performance: -7.1 },
      { name: "Total Stock Market", performance: -3.2 },
      { name: "60/40 Portfolio", performance: -1.8 }
    ],
    riskMetrics: {
      beta: 0.42,
      volatility: 7.8,
      alpha: 1.1,
      expenseRatio: 0.32,
      sortinoRatio: 0.91,
      valueAtRisk: -980
    }
  },
  {
    id: "4",
    name: "Index Portfolio",
    type: "Index",
    totalReturn: 10.1,
    annualizedReturn: 7.3,
    sharpeRatio: 1.05,
    maxDrawdown: -14.7,
    totalValue: 123200,
    lastUpdated: "2025-08-27",
    benchmarkComparisons: [
      { name: "S&P 500", performance: 0.1 },
      { name: "NASDAQ 100", performance: -2.8 },
      { name: "Total Stock Market", performance: 1.1 },
      { name: "60/40 Portfolio", performance: 3.1 }
    ],
    riskMetrics: {
      beta: 1.02,
      volatility: 13.5,
      alpha: 0.2,
      expenseRatio: 0.08,
      sortinoRatio: 1.18,
      valueAtRisk: -3200
    }
  }
];
