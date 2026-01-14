export interface FinancialData {
  companyName: string;
  // P/L (Profit and Loss) - User inputs in millions or thousands, but handled as numbers
  // null indicates "Unknown/Not Disclosed" rather than 0
  revenue: number | null; // 売上高
  prevRevenue: number | null; // 前期売上高 (for growth calc)
  operatingProfit: number | null; // 営業利益
  netIncome: number | null; // 当期純利益
  
  // B/S (Balance Sheet)
  currentAssets: number | null; // 流動資産
  currentLiabilities: number | null; // 流動負債
  totalAssets: number | null; // 総資産
  totalEquity: number | null; // 自己資本 (純資産)
  
  industry: string; // 業種
}

export interface AnalysisSection {
  score: number; // 1-100
  title: string;
  summary: string;
  details: string;
}

export interface BusinessChallenge {
  title: string;
  description: string;
  basis: string; // 根拠
}

export interface InsuranceRecommendation {
  productName: string;
  reasoning: string;
  salesTalk: string;
}

export interface ConsultantAnalysis {
  profitability: AnalysisSection;
  safety: AnalysisSection;
  growth: AnalysisSection;
  overallSummary: string;
  businessChallenges: BusinessChallenge[];
  recommendations: InsuranceRecommendation[];
}