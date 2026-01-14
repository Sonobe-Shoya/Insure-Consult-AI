
import React, { useState } from 'react';
import { FinancialData } from '../types';
import { Calculator, ArrowRight, Building2, HelpCircle, ShieldCheck, Lock, Loader2 } from 'lucide-react';

interface Props {
  onSubmit: (data: FinancialData) => void;
  isLoading: boolean;
}

const initialData: FinancialData = {
  companyName: '',
  revenue: null,
  prevRevenue: null,
  operatingProfit: null,
  netIncome: null,
  currentAssets: null,
  currentLiabilities: null,
  totalAssets: null,
  totalEquity: null,
  industry: '製造業',
};

const FinancialInputForm: React.FC<Props> = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState<FinancialData>(initialData);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name === 'companyName' || name === 'industry') {
      setFormData(prev => ({ ...prev, [name]: value }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value === '' ? null : Number(value)
      }));
    }
  };

  const loadDemoData = () => {
    setFormData({
      companyName: '株式会社 サンプルテック',
      revenue: 50000,
      prevRevenue: 42000,
      operatingProfit: 2500,
      netIncome: 1500,
      currentAssets: 12000,
      currentLiabilities: 15000,
      totalAssets: 30000,
      totalEquity: 8000,
      industry: 'IT・ソフトウェア',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
      <div className="bg-slate-900 p-6 text-white flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Calculator className="w-6 h-6" />
            財務データ入力
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            顧客企業の財務情報を入力してください。AIが即座に分析レポートを生成します。
          </p>
        </div>
        <button 
          type="button"
          onClick={loadDemoData}
          className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded transition border border-slate-600"
        >
          デモデータを入力
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-8">
        
        {/* Company Info */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">企業名 <span className="text-red-500">*</span></label>
            <input
              required
              type="text"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              placeholder="例: 株式会社〇〇"
              className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition bg-slate-50/30 font-medium"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">業種 <span className="text-red-500">*</span></label>
            <select
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition bg-slate-50/30 font-bold text-slate-700"
            >
              <option value="製造業">製造業</option>
              <option value="運送業">運送業</option>
              <option value="学校法人">学校法人</option>
              <option value="マンション管理組合">マンション管理組合</option>
              <option value="建設業">建設業</option>
              <option value="小売・卸売">小売・卸売</option>
              <option value="サービス業">サービス業</option>
              <option value="IT・ソフトウェア">IT・ソフトウェア</option>
              <option value="不動産">不動産</option>
              <option value="医療・福祉">医療・福祉</option>
              <option value="その他">その他</option>
            </select>
          </div>
        </div>

        <div className="mb-8 bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-start gap-3 text-sm text-blue-800">
          <HelpCircle className="w-5 h-5 mt-0.5 flex-shrink-0 text-blue-600" />
          <p className="font-medium leading-relaxed">
            決算書（損益計算書・貸借対照表）に基づき数値を入力してください。
            <br className="hidden md:inline" />
            不明な項目や非開示の項目は空欄のままで構いません。AIが可能な範囲で推測・分析を行います。
          </p>
        </div>

        {/* Financial Sections */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* P/L Section */}
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-300 pb-2">
              <Building2 className="w-4 h-4 text-blue-600" /> 損益計算書 (P/L)
            </h3>
            <div className="space-y-4">
              {[
                { label: '売上高', name: 'revenue' },
                { label: '前期売上高', name: 'prevRevenue' },
                { label: '営業利益', name: 'operatingProfit' },
                { label: '当期純利益', name: 'netIncome' }
              ].map((field) => (
                <div key={field.name}>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {field.label}
                  </label>
                  <input
                    type="number"
                    name={field.name}
                    value={(formData as any)[field.name] ?? ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-right font-mono focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-inner"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* B/S Assets Section */}
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-300 pb-2">
              <Building2 className="w-4 h-4 text-emerald-600" /> 資産の部 (B/S)
            </h3>
            <div className="space-y-4">
              {[
                { label: '流動資産', name: 'currentAssets' },
                { label: '総資産', name: 'totalAssets' }
              ].map((field) => (
                <div key={field.name}>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {field.label}
                  </label>
                  <input
                    type="number"
                    name={field.name}
                    value={(formData as any)[field.name] ?? ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-right font-mono focus:outline-none focus:ring-2 focus:ring-emerald-400 shadow-inner"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* B/S Liabilities Section */}
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-300 pb-2">
              <Building2 className="w-4 h-4 text-amber-600" /> 負債・純資産 (B/S)
            </h3>
            <div className="space-y-4">
              {[
                { label: '流動負債', name: 'currentLiabilities' },
                { label: '純資産 (自己資本)', name: 'totalEquity' }
              ].map((field) => (
                <div key={field.name}>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {field.label}
                  </label>
                  <input
                    type="number"
                    name={field.name}
                    value={(formData as any)[field.name] ?? ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-right font-mono focus:outline-none focus:ring-2 focus:ring-amber-400 shadow-inner"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center bg-slate-50 p-6 rounded-2xl border border-slate-200 gap-6">
          <div className="flex items-start gap-4">
            <div className="bg-emerald-100 p-2 rounded-lg text-emerald-700">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-800 text-sm">セキュア診断モード</h4>
              <p className="text-[11px] text-slate-500 mt-1 font-medium leading-relaxed">
                入力データはAI診断のために一時的に処理され、学習データには利用されません。<br />
                送信ボタンをクリックすると、暗号化通信を介して解析が開始されます。
              </p>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !formData.companyName}
            className={`
              w-full md:w-auto flex items-center justify-center gap-4 px-12 py-5 rounded-2xl text-xl font-bold text-white shadow-2xl
              transition transform active:scale-95
              ${(isLoading || !formData.companyName) ? 'bg-slate-300 cursor-not-allowed shadow-none' : 'bg-blue-600 hover:bg-blue-500 hover:-translate-y-1'}
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                診断中...
              </>
            ) : (
              <>
                診断レポートを作成 <ArrowRight className="w-6 h-6" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FinancialInputForm;
