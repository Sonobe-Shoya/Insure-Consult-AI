
import { GoogleGenAI, Type, Schema } from "@google/genai";
import { FinancialData, ConsultantAnalysis } from "../types";

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey: apiKey });

const analysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    profitability: {
      type: Type.OBJECT,
      properties: {
        score: { type: Type.NUMBER, description: "100点満点のスコア" },
        title: { type: Type.STRING },
        summary: { type: Type.STRING },
        details: { type: Type.STRING },
      },
      required: ["score", "title", "summary", "details"],
    },
    safety: {
      type: Type.OBJECT,
      properties: {
        score: { type: Type.NUMBER },
        title: { type: Type.STRING },
        summary: { type: Type.STRING },
        details: { type: Type.STRING },
      },
      required: ["score", "title", "summary", "details"],
    },
    growth: {
      type: Type.OBJECT,
      properties: {
        score: { type: Type.NUMBER },
        title: { type: Type.STRING },
        summary: { type: Type.STRING },
        details: { type: Type.STRING },
      },
      required: ["score", "title", "summary", "details"],
    },
    overallSummary: { type: Type.STRING },
    businessChallenges: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING },
          description: { type: Type.STRING },
          basis: { type: Type.STRING },
        },
        required: ["title", "description", "basis"],
      },
    },
    recommendations: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          productName: { type: Type.STRING },
          reasoning: { type: Type.STRING },
          salesTalk: { type: Type.STRING },
        },
        required: ["productName", "reasoning", "salesTalk"],
      },
    },
  },
  required: ["profitability", "safety", "growth", "overallSummary", "businessChallenges", "recommendations"],
};

const formatValue = (val: number | null): string | number => {
  return val === null ? "不明（開示なし）" : val;
};

export const analyzeFinancials = async (data: FinancialData): Promise<ConsultantAnalysis> => {
  if (!apiKey) {
    throw new Error("API Key is missing.");
  }

  const prompt = `
    あなたはトップクラスの経営コンサルタントであり、日新火災海上保険株式会社の熟練した営業担当者です。
    以下の「${data.industry}」業界の企業の財務データを分析してください。

    財務データ:
    - 売上高: ${formatValue(data.revenue)}
    - 前期売上高: ${formatValue(data.prevRevenue)}
    - 営業利益: ${formatValue(data.operatingProfit)}
    - 当期純利益: ${formatValue(data.netIncome)}
    - 流動資産: ${formatValue(data.currentAssets)}
    - 流動負債: ${formatValue(data.currentLiabilities)}
    - 総資産: ${formatValue(data.totalAssets)}
    - 純資産 (自己資本): ${formatValue(data.totalEquity)}

    【タスク】
    1. 主要な財務指標を計算し、「収益性」「安全性」「成長性」を0-100でスコアリングしてください。
    2. 財務データに基づき、この企業が直面している「経営課題」を3つ特定してください。
    3. 以下の【取扱商品リスト】の中から、この企業に最適な保険商品を3つ選定し推奨してください。

    【取扱商品リスト】
    - ビジネスプロパティ（企業財産総合保険）
    - 労災あんしん保険（業務災害総合保険）
    - Mono保険（財産補償保険）
    - ビジサポ（統合賠償責任保険）
    - サイバー・情報漏えい保険
    - 工事の保険
    - ユーサイド（新総合自動車保険）
    - ドライビングサポート２４プラス
    - 働けないときの保険（所得補償保険）
    - ジョイエ傷害保険
    - 住宅安心保険 / お家ドクター火災保険
    - マンションドクター火災保険

    出力はJSON形式で、すべて日本語で記述してください。
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        temperature: 0.2, 
      },
    });

    const text = response.text;
    if (!text) throw new Error("AIからの応答がありません");
    
    return JSON.parse(text) as ConsultantAnalysis;
  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    throw error;
  }
};
