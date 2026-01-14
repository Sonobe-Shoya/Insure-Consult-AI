import React, { useState, useEffect } from 'react';
import { ConsultantAnalysis, FinancialData } from '../types';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from 'recharts';
import { 
  ShieldCheck, TrendingUp, DollarSign, BrainCircuit, RefreshCw, BookOpen, ExternalLink,
  Car, Bike, Home, Building2, Factory, HardHat, Stethoscope, Heart, Lock, Wrench, Briefcase, Activity, FileText, Plane, Umbrella,
  AlertTriangle, Target, Lightbulb, Search
} from 'lucide-react';

interface Props {
  data: ConsultantAnalysis;
  financialData: FinancialData;
  onReset: () => void;
}

// 商品名キーワードと画像パス/URLの対応マップ
// httpから始まる場合は外部URL、それ以外は /images/ フォルダ内のファイルとして扱います
const PRODUCT_IMAGES: { [key: string]: string } = {
  // 自動車・交通
  "ユーサイド": "https://www.nisshinfire.co.jp/service/pdf/YOUSIDE2601.pdf",
  "ドライビング": "https://www.nisshinfire.co.jp/service/pdf/ds24plus2101.pdf",
  "バイク": "https://www.nisshinfire.co.jp/service/pdf/bike1901.pdf",
  "自賠責": "https://www.nisshinfire.co.jp/service/pdf/jibaiseki.pdf",
  
  // 住まい・火災・地震
  "住宅安心": "https://www.nisshinfire.co.jp/service/pdf/jutaku2410.pdf",
  "お家ドクター": "https://www.nisshinfire.co.jp/service/pdf/ouchidr2410.pdf",
  "お部屋を借りる": "https://www.nisshinfire.co.jp/service/pdf/oheya_01.pdf",
  "マンション": "https://www.nisshinfire.co.jp/service/pdf/mandoku2410.pdf",
  "地震": "https://www.nisshinfire.co.jp/service/pdf/jishin2210.pdf",

  // ケガ・病気・旅行
  "自転車": "https://www.nisshinfire.co.jp/service/pdf/joyesj2310.pdf",
  "スポーツ": "https://www.nisshinfire.co.jp/service/pdf/joyess2410.pdf",
  "キッズ": "https://www.nisshinfire.co.jp/service/pdf/joyekids2410.pdf",
  "ジョイエ": "https://www.nisshinfire.co.jp/service/pdf/joye2410.pdf",
  "日常生活傷害": "https://www.nisshinfire.co.jp/service/pdf/nichijo2410.pdf",
  "キズいえ～る": "https://www.nisshinfire.co.jp/service/pdf/kizu2310.pdf",
  "働けない": "https://www.nisshinfire.co.jp/service/pdf/hatarakenaitoki2301.pdf",
  "海外旅行": "https://www.nisshinfire.co.jp/service/pdf/kaigai2310.pdf",
  "国内旅行": "https://www.nisshinfire.co.jp/service/pdf/kokunai2106.pdf",

  // ビジネス・企業向け
  "ビジネスプロパティ": "https://www.nisshinfire.co.jp/service/pdf/businessproperty2410.pdf",
  "労災あんしん": "https://www.nisshinfire.co.jp/service/pdf/rousaianshin2509.pdf",
  "Mono": "https://www.nisshinfire.co.jp/service/pdf/mono2310.pdf",
  "ビジサポ": "https://www.nisshinfire.co.jp/service/pdf/busisup2601.pdf",
  "サイバー": "https://www.nisshinfire.co.jp/service/pdf/cyber2601.pdf",
  "工事": "https://www.nisshinfire.co.jp/service/pdf/kouji2506.pdf",
};

// パンフレット表紙を表示するコンポーネント
// 画像URL(jpg/png)なら画像を表示。PDFや画像エラーならCSS描画＋リンク機能を提供。
const BrochureCover: React.FC<{ productName: string }> = ({ productName }) => {
  const [imageError, setImageError] = useState(false);
  
  // 商品名に対応する画像キーを特定
  const imageKey = Object.keys(PRODUCT_IMAGES).find(key => productName.includes(key));
  const rawPath = imageKey ? PRODUCT_IMAGES[imageKey] : null;

  // URLの判定
  const isExternal = rawPath?.startsWith('http') || rawPath?.startsWith('https');
  const isPdf = rawPath?.toLowerCase().endsWith('.pdf');
  
  // 最終的なソースパスの決定
  const src = isExternal ? rawPath : (rawPath ? `/images/${rawPath}` : null);

  useEffect(() => {
    setImageError(false);
  }, [productName]);

  // CSSで表紙を描画する関数（共通利用）
  const renderCssCover = (overlayContent?: React.ReactNode) => {
    let config = {
      bg: "bg-white",
      headerColor: "bg-slate-200",
      titleColor: "text-slate-800",
      icon: <BookOpen className="w-12 h-12 text-slate-400" />,
      category: "保険商品"
    };

    // 商品名キーワードに基づくスタイル設定
    if (productName.includes("ユーサイド")) {
      config = {
        bg: "bg-gradient-to-b from-white to-blue-50",
        headerColor: "bg-blue-600",
        titleColor: "text-blue-700",
        icon: <div className="relative"><Heart className="w-14 h-14 text-yellow-400 fill-yellow-400 absolute -top-3 -right-3 opacity-60" /><Car className="w-12 h-12 text-blue-600 relative z-10" /></div>,
        category: "自動車保険"
      };
    } else if (productName.includes("ドライビング")) {
      config = {
        bg: "bg-white",
        headerColor: "bg-emerald-500",
        titleColor: "text-emerald-700",
        icon: <Activity className="w-12 h-12 text-emerald-600" />,
        category: "ドラレコ特約"
      };
    } else if (productName.includes("バイク")) {
      config = {
        bg: "bg-slate-50",
        headerColor: "bg-blue-500",
        titleColor: "text-blue-800",
        icon: <Bike className="w-12 h-12 text-blue-600" />,
        category: "バイク保険"
      };
    } else if (productName.includes("自賠責")) {
      config = {
        bg: "bg-yellow-50",
        headerColor: "bg-yellow-500",
        titleColor: "text-yellow-800",
        icon: <Car className="w-12 h-12 text-yellow-600" />,
        category: "自賠責"
      };
    } else if (productName.includes("住宅安心") || productName.includes("お家ドクター")) {
      config = {
        bg: "bg-blue-50",
        headerColor: "bg-cyan-500",
        titleColor: "text-cyan-800",
        icon: <Home className="w-12 h-12 text-cyan-600" />,
        category: "火災保険"
      };
    } else if (productName.includes("借りる") || productName.includes("賃貸")) {
      config = {
        bg: "bg-green-50",
        headerColor: "bg-green-500",
        titleColor: "text-green-800",
        icon: <Home className="w-12 h-12 text-green-600" />,
        category: "家財保険"
      };
    } else if (productName.includes("マンション")) {
      config = {
        bg: "bg-white",
        headerColor: "bg-red-500",
        titleColor: "text-red-600",
        icon: <Building2 className="w-12 h-12 text-red-500" />,
        category: "マンション管理"
      };
    } else if (productName.includes("ビジネスプロパティ")) {
      config = {
        bg: "bg-gradient-to-br from-white to-sky-50",
        headerColor: "bg-sky-700",
        titleColor: "text-sky-900",
        icon: <Factory className="w-12 h-12 text-sky-800" />,
        category: "企業財産総合保険"
      };
    } else if (productName.includes("労災あんしん")) {
      config = {
        bg: "bg-lime-50",
        headerColor: "bg-lime-600",
        titleColor: "text-lime-800",
        icon: <HardHat className="w-12 h-12 text-lime-600" />,
        category: "業務災害補償"
      };
    } else if (productName.includes("Mono")) {
      config = {
        bg: "bg-white",
        headerColor: "bg-orange-500",
        titleColor: "text-orange-800",
        icon: <Briefcase className="w-12 h-12 text-orange-600" />,
        category: "財産補償"
      };
    } else if (productName.includes("ビジサポ")) {
      config = {
        bg: "bg-white",
        headerColor: "bg-orange-500",
        titleColor: "text-orange-600",
        icon: <ShieldCheck className="w-12 h-12 text-orange-500" />,
        category: "賠償責任保険"
      };
    } else if (productName.includes("サイバー")) {
      config = {
        bg: "bg-slate-900",
        headerColor: "bg-indigo-500",
        titleColor: "text-indigo-300",
        icon: <Lock className="w-12 h-12 text-indigo-400" />,
        category: "情報漏えい"
      };
    } else if (productName.includes("工事")) {
      config = {
        bg: "bg-yellow-50",
        headerColor: "bg-yellow-500",
        titleColor: "text-yellow-800",
        icon: <Wrench className="w-12 h-12 text-yellow-600" />,
        category: "工事保険"
      };
    } else if (productName.includes("働けない")) {
      config = {
        bg: "bg-pink-50",
        headerColor: "bg-pink-500",
        titleColor: "text-pink-700",
        icon: <Stethoscope className="w-12 h-12 text-pink-600" />,
        category: "所得補償"
      };
    } else if (productName.includes("ジョイエ") || productName.includes("傷害") || productName.includes("キズ")) {
      config = {
        bg: "bg-teal-50",
        headerColor: "bg-teal-500",
        titleColor: "text-teal-700",
        icon: <Activity className="w-12 h-12 text-teal-600" />,
        category: "傷害保険"
      };
    } else if (productName.includes("地震")) {
      config = {
        bg: "bg-orange-50",
        headerColor: "bg-orange-400",
        titleColor: "text-orange-800",
        icon: <Activity className="w-12 h-12 text-orange-500" />,
        category: "地震保険"
      };
    } else if (productName.includes("旅行")) {
      config = {
        bg: "bg-sky-50",
        headerColor: "bg-sky-500",
        titleColor: "text-sky-800",
        icon: <Plane className="w-12 h-12 text-sky-600" />,
        category: "旅行保険"
      };
    }

    return (
      <div className={`w-full h-full flex flex-col ${config.bg} relative group`}>
         {/* ヘッダー帯 */}
         <div className={`h-12 w-full ${config.headerColor} flex items-center justify-between px-3 shrink-0`}>
            <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-white font-bold text-[10px]">
              N
            </div>
            <span className="text-[9px] text-white/90 font-medium tracking-wider">日新火災</span>
         </div>
         
         {/* メインエリア */}
         <div className="flex-1 p-3 flex flex-col items-center justify-center text-center">
           <div className="mb-3 p-3 bg-white/60 rounded-full shadow-sm">{config.icon}</div>
           <h3 className={`text-base font-bold leading-tight mb-2 ${config.titleColor} line-clamp-3`}>
             {productName}
           </h3>
           <span className="text-[9px] uppercase font-bold text-slate-500 bg-slate-200/50 px-2 py-1 rounded">
             {config.category}
           </span>
         </div>
         
         {/* フッター装飾 */}
         <div className="h-2 w-full bg-slate-200/50 mt-auto shrink-0"></div>

         {/* オーバーレイ (リンクやPDF表示用) */}
         {overlayContent}
      </div>
    );
  };

  // コンテナの基本クラス
  const containerClass = "w-full max-w-[200px] aspect-[210/297] rounded-r-lg rounded-l-sm shadow-md overflow-hidden mx-auto transition-transform hover:scale-105 duration-300 border-l-4 border-slate-300 relative select-none";

  // CASE 1: PDFの場合
  // CSS表紙を表示し、クリックするとPDFへ飛ぶリンクにする
  if (isPdf && src) {
    return (
      <a 
        href={src} 
        target="_blank" 
        rel="noopener noreferrer"
        className={`${containerClass} block cursor-pointer hover:shadow-xl`}
        title="PDFパンフレットを開く"
      >
        {renderCssCover(
          <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/10 transition-all flex items-center justify-center">
             <div className="bg-white/90 text-red-600 px-3 py-1.5 rounded-full shadow-lg transform translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 flex items-center gap-1.5 text-xs font-bold">
               <FileText className="w-3.5 h-3.5" /> PDFを開く
             </div>
          </div>
        )}
      </a>
    );
  }

  // CASE 2: 画像URLがあり、かつエラーになっていない場合
  if (src && !imageError) {
    return (
      <div className={`${containerClass} bg-slate-100 border border-slate-200`}>
        <img 
          src={src} 
          alt={productName}
          className="w-full h-full object-cover"
          onError={() => setImageError(true)}
        />
        {/* ホバー時のオーバーレイ */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors pointer-events-none" />
      </div>
    );
  }

  // CASE 3: 画像がない、またはエラーになった場合 (CSSフォールバック)
  return (
    <div className={containerClass}>
      {renderCssCover()}
    </div>
  );
};

const ScoreCard: React.FC<{ title: string; score: number; icon: React.ReactNode; color: string; description: string }> = ({ title, score, icon, color, description }) => (
  <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col h-full">
    <div className={`flex items-center gap-3 mb-3 ${color}`}>
      <div className="p-2 rounded-lg bg-opacity-10 bg-current">
        {icon}
      </div>
      <h3 className="font-bold text-lg text-slate-800">{title}</h3>
    </div>
    <div className="flex items-end gap-2 mb-2">
      <span className={`text-4xl font-bold ${color}`}>{score}</span>
      <span className="text-slate-400 text-sm mb-1">/ 100</span>
    </div>
    <p className="text-sm text-slate-600 mt-auto">{description}</p>
  </div>
);

const ChallengeCard: React.FC<{ challenge: ConsultantAnalysis['businessChallenges'][0]; index: number }> = ({ challenge, index }) => (
  <div className="bg-white p-5 rounded-lg shadow-sm border-l-4 border-amber-500 hover:shadow-md transition-shadow">
    <div className="flex items-start gap-3 mb-3">
      <div className="mt-1 min-w-[24px] h-6 flex items-center justify-center bg-amber-100 text-amber-700 rounded-full text-xs font-bold">
        {index + 1}
      </div>
      <h4 className="text-lg font-bold text-slate-800 leading-tight">{challenge.title}</h4>
    </div>
    
    <div className="mb-4">
      <p className="text-slate-600 text-sm leading-relaxed">{challenge.description}</p>
    </div>
    
    <div className="bg-slate-50 p-3 rounded text-sm text-slate-700 flex items-start gap-2">
      <Search className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
      <div>
        <span className="font-bold text-xs text-slate-500 block mb-1">根拠 (財務データ)</span>
        {challenge.basis}
      </div>
    </div>
  </div>
);

const RecommendationCard: React.FC<{ rec: ConsultantAnalysis['recommendations'][0]; index: number }> = ({ rec, index }) => {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden border-t-4 border-indigo-500 hover:shadow-lg transition duration-300">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start gap-3 mb-6">
          <span className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm mt-1">
            {index + 1}
          </span>
          <h4 className="text-xl font-bold text-slate-800 leading-tight">{rec.productName}</h4>
        </div>
        
        <div className="flex flex-col md:flex-row gap-6">
          {/* Left Column: Brochure Image */}
          <div className="w-full md:w-1/3 flex-shrink-0 flex flex-col items-center">
            <BrochureCover productName={rec.productName} />
            <p className="text-xs text-slate-400 mt-3 flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              パンフレット
            </p>
          </div>

          {/* Right Column: Content */}
          <div className="w-full md:w-2/3 space-y-5">
            <div>
              <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1">
                <BrainCircuit className="w-3 h-3" /> 提案の根拠 (財務視点)
              </h5>
              <p className="text-slate-700 bg-slate-50 p-3 rounded-lg text-sm leading-relaxed border border-slate-100">
                {rec.reasoning}
              </p>
            </div>
            
            <div>
              <h5 className="text-xs font-bold text-indigo-600 uppercase tracking-wide mb-2 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> セールストーク (話法)
              </h5>
              <div className="relative bg-indigo-50 p-4 rounded-lg rounded-tl-none border border-indigo-100">
                <p className="text-slate-800 italic font-medium leading-relaxed text-sm">
                  "{rec.salesTalk}"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AnalysisDashboard: React.FC<Props> = ({ data, financialData, onReset }) => {
  const chartData = [
    { subject: '収益性', A: data.profitability.score, fullMark: 100 },
    { subject: '安全性', A: data.safety.score, fullMark: 100 },
    { subject: '成長性', A: data.growth.score, fullMark: 100 },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-12">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">{financialData.companyName} 様 診断レポート</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs font-medium">
              {financialData.industry}
            </span>
            <p className="text-slate-500 text-sm">AI経営コンサルタントによる分析結果</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition shadow-sm font-medium text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            新しい分析を始める
          </button>
        </div>
      </div>

      {/* Top Section: Overview & Radar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Executive Summary */}
        <div className="lg:col-span-2 bg-slate-900 text-white p-8 rounded-2xl shadow-xl flex flex-col justify-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600 rounded-full blur-3xl opacity-20 -mr-16 -mt-16"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-white bg-opacity-10 rounded-lg">
                <BrainCircuit className="w-6 h-6 text-blue-300" />
              </div>
              <h3 className="text-xl font-bold">総合コンサルティング要約</h3>
            </div>
            <p className="text-lg leading-relaxed text-slate-200 font-light">
              {data.overallSummary}
            </p>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="bg-white p-4 rounded-2xl shadow-md flex flex-col items-center justify-center min-h-[300px] border border-slate-100">
          <h4 className="text-sm font-bold text-slate-500 mb-2 uppercase tracking-wider">財務バランススコア</h4>
          <div className="w-full h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 13, fontWeight: 'bold' }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Score"
                  dataKey="A"
                  stroke="#2563eb"
                  strokeWidth={3}
                  fill="#3b82f6"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3 Pillars Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ScoreCard 
          title="収益性" 
          score={data.profitability.score} 
          icon={<DollarSign className="w-6 h-6" />} 
          color="text-blue-600"
          description={data.profitability.details}
        />
        <ScoreCard 
          title="安全性" 
          score={data.safety.score} 
          icon={<ShieldCheck className="w-6 h-6" />} 
          color="text-emerald-600"
          description={data.safety.details}
        />
        <ScoreCard 
          title="成長性" 
          score={data.growth.score} 
          icon={<TrendingUp className="w-6 h-6" />} 
          color="text-amber-600"
          description={data.growth.details}
        />
      </div>

      {/* New Section: Future Challenges */}
      {data.businessChallenges && data.businessChallenges.length > 0 && (
        <div className="mt-8">
           <div className="flex items-center gap-3 mb-6">
            <span className="bg-amber-500 text-white p-2.5 rounded-xl shadow-md">
               <Target className="w-6 h-6" />
            </span>
            <div>
              <h3 className="text-2xl font-bold text-slate-900">今後の経営課題とリスク</h3>
              <p className="text-slate-500 text-sm mt-0.5">財務データから予測される、取り組むべき優先事項</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {data.businessChallenges.map((challenge, index) => (
              <ChallengeCard key={index} challenge={challenge} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Recommendations Section */}
      <div className="mt-12">
        <div className="flex items-center gap-3 mb-8">
          <span className="bg-indigo-600 text-white p-2.5 rounded-xl shadow-md">
             <BookOpen className="w-6 h-6" />
          </span>
          <div>
            <h3 className="text-2xl font-bold text-slate-900">提案すべき保険商品とアプローチ</h3>
            <p className="text-slate-500 text-sm mt-0.5">財務課題を解決するための最適な日新火災商品</p>
          </div>
        </div>
        
        <div className="flex flex-col gap-8">
          {data.recommendations.map((rec, index) => (
            <RecommendationCard key={index} rec={rec} index={index} />
          ))}
        </div>
      </div>

    </div>
  );
};

export default AnalysisDashboard;