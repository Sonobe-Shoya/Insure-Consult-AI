import React, { useState } from 'react';
import { FinancialData, ConsultantAnalysis } from './types';
import { analyzeFinancials } from './services/geminiService';
import FinancialInputForm from './components/FinancialInputForm';
import AnalysisDashboard from './components/AnalysisDashboard';
import { Briefcase, Info, Lock } from 'lucide-react';

const App: React.FC = () => {
  const [step, setStep] = useState<'input' | 'analyzing' | 'result'>('input');
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<ConsultantAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalysis = async (data: FinancialData) => {
    setFinancialData(data);
    setStep('analyzing');
    setError(null);

    try {
      const result = await analyzeFinancials(data);
      setAnalysisResult(result);
      setStep('result');
    } catch (err) {
      console.error(err);
      setError("AI分析中にエラーが発生しました。APIキーを確認するか、もう一度お試しください。");
      setStep('input');
    }
  };

  const handleReset = () => {
    setStep('input');
    setFinancialData(null);
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              InsureConsult <span className="text-blue-600">AI</span>
            </h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="text-sm text-slate-500 hidden md:block border-r border-slate-300 pr-6">
              経営コンサル型保険営業支援ツール
            </div>
            {/* 画像エラー回避のためテキストロゴに変更 */}
            <div className="flex flex-col items-end justify-center">
               <span className="font-bold text-slate-700 text-lg tracking-wider leading-none mb-1">日新火災</span>
               <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase leading-none">Tokio Marine Group</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow p-4 md:p-8">
        {error && (
          <div className="max-w-4xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3 text-red-700">
            <Info className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {step === 'input' && (
          <div className="animate-fade-in">
             <div className="text-center max-w-2xl mx-auto mb-10">
              <h2 className="text-3xl font-bold mb-4">財務データから、最適な提案を。</h2>
              <p className="text-slate-600">
                顧客の決算書（P/L、B/S）の数値を入力するだけで、
                <br className="hidden md:inline" />
                AIが「収益性・安全性・成長性」を分析し、コンサルティング視点での保険提案を作成します。
              </p>
            </div>
            <FinancialInputForm onSubmit={handleAnalysis} isLoading={false} />
          </div>
        )}

        {step === 'analyzing' && (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
            <div className="relative w-24 h-24 mb-8">
              <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-100 rounded-full"></div>
              <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-blue-600">
                <Briefcase className="w-8 h-8" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-slate-800 mb-2">財務分析を実行中...</h3>
            <p className="text-slate-500">
              数千の経営シナリオと照合し、最適な保険商品を検討しています。
            </p>
          </div>
        )}

        {step === 'result' && analysisResult && financialData && (
          <AnalysisDashboard 
            data={analysisResult} 
            financialData={financialData} 
            onReset={handleReset} 
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-8 border-t border-slate-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
          <div className="text-xs">
            <p className="font-semibold text-slate-300 mb-1">InsureConsult AI</p>
            <p>© 2024 Tokio Marine & Nichido Fire Insurance Co., Ltd. Group / Nisshin Fire</p>
            <p className="mt-2 text-slate-600">
              ※本ツールは営業支援目的のデモンストレーション用アプリケーションです。
            </p>
          </div>
          
          <div className="flex flex-col items-center md:items-end gap-2">
            <div className="flex items-center gap-2 text-xs bg-slate-800 px-3 py-1.5 rounded-full text-slate-400 border border-slate-700">
              <Lock className="w-3 h-3" />
              <span>Secure Data Processing</span>
            </div>
            <p className="text-[10px] text-slate-600 max-w-xs text-right">
              入力データは本セッションでの分析のみに使用され、<br/>AIモデルの学習データとして利用されることはありません。
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;