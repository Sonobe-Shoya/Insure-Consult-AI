import { ConsultantAnalysis, FinancialData } from "../types";

// PptxGenJS is loaded via script tag in index.html and available globally
declare const PptxGenJS: any;

export const generateProposalPptx = async (analysis: ConsultantAnalysis, financial: FinancialData) => {
  // PptxGenJSのインスタンス作成
  const pres = new PptxGenJS();

  // 基本設定
  pres.layout = "LAYOUT_16x9";
  pres.author = "InsureConsult AI";
  pres.company = "日新火災海上保険株式会社";
  pres.title = `${financial.companyName}様 経営分析・保険提案書`;

  // カラー定義
  const primaryColor = "0052CC"; // 日新ブルー/東京海上ブルー系
  const accentColor = "00A388"; // アクセントグリーン
  const lightBg = "F4F5F7"; // 背景グレー
  const white = "FFFFFF";

  // フォント設定（日本語対応のためメイリオ優先）
  const fontFace = "Meiryo UI";

  // ------------------------------------------
  // 1. タイトルスライド
  // ------------------------------------------
  const slide1 = pres.addSlide();
  slide1.background = { color: white };
  
  // 装飾バー
  slide1.addShape(pres.shapes.RECT, { x: 0, y: 0, w: "100%", h: 0.15, fill: primaryColor });
  slide1.addShape(pres.shapes.RECT, { x: 0, y: 0.15, w: "40%", h: 0.15, fill: accentColor });

  // メインタイトル
  slide1.addText("経営財務分析 & 保険コンサルティング提案書", {
    x: 0.5, y: 2.0, w: "90%", fontSize: 18, color: "666666", fontFace
  });
  
  slide1.addText(`${financial.companyName} 御中`, {
    x: 0.5, y: 2.5, w: "90%", fontSize: 44, bold: true, color: "333333", fontFace
  });
  
  // 日付と署名
  slide1.addText(`ご提案日: ${new Date().toLocaleDateString()}`, {
    x: 0.5, y: 5.0, w: "90%", fontSize: 16, color: "666666", fontFace
  });
  
  slide1.addText("日新火災海上保険株式会社", {
    x: 0.5, y: 6.0, w: "90%", fontSize: 20, bold: true, color: primaryColor, fontFace
  });
  slide1.addText("Tokio Marine Group", {
    x: 0.5, y: 6.4, w: "90%", fontSize: 12, color: "666666", fontFace
  });

  // ------------------------------------------
  // 2. 財務分析サマリー
  // ------------------------------------------
  const slide2 = pres.addSlide();
  
  // ヘッダー
  slide2.addShape(pres.shapes.RECT, { x: 0, y: 0, w: "100%", h: 0.8, fill: primaryColor });
  slide2.addText("財務分析診断結果", { x: 0.3, y: 0.15, fontSize: 24, bold: true, color: white, fontFace });

  // 3つの指標スコアボックス
  const drawScoreBox = (title: string, score: number, summary: string, xPos: number) => {
    // 背景カード
    slide2.addShape(pres.shapes.RECT, { 
      x: xPos, y: 1.2, w: 3.0, h: 4.0, 
      fill: lightBg, line: { color: "DDDDDD", width: 1 } 
    });
    
    // タイトル帯
    slide2.addShape(pres.shapes.RECT, { 
      x: xPos, y: 1.2, w: 3.0, h: 0.6, 
      fill: title === "安全性" ? accentColor : (title === "成長性" ? "F5A623" : primaryColor) // 安全性は緑、成長性はオレンジ、収益性は青
    });
    slide2.addText(title, { 
      x: xPos, y: 1.3, w: 3.0, align: "center", fontSize: 16, bold: true, color: white, fontFace 
    });

    // スコア
    slide2.addText(`${score}`, { 
      x: xPos, y: 2.0, w: 3.0, align: "center", fontSize: 40, bold: true, color: "333333", fontFace 
    });
    slide2.addText("点 / 100", { 
      x: xPos, y: 2.6, w: 3.0, align: "center", fontSize: 12, color: "666666", fontFace 
    });

    // コメント
    slide2.addText(summary, { 
      x: xPos + 0.15, y: 3.0, w: 2.7, h: 2.0, fontSize: 11, color: "333333", valign: "top", fontFace 
    });
  };

  drawScoreBox("収益性", analysis.profitability.score, analysis.profitability.details, 0.4);
  drawScoreBox("安全性", analysis.safety.score, analysis.safety.details, 3.66);
  drawScoreBox("成長性", analysis.growth.score, analysis.growth.details, 6.92);

  // 総合評価エリア
  slide2.addShape(pres.shapes.RECT, { x: 0.4, y: 5.5, w: 9.52, h: 1.5, fill: "E6F4F1", line: { color: accentColor } });
  slide2.addText("総合コンサルティング要約", { x: 0.5, y: 5.6, fontSize: 12, bold: true, color: accentColor, fontFace });
  slide2.addText(analysis.overallSummary, { x: 0.5, y: 5.9, w: 9.3, fontSize: 11, color: "333333", fontFace });

  // ------------------------------------------
  // 3. 提案スライド (各商品ごと)
  // ------------------------------------------
  analysis.recommendations.forEach((rec, index) => {
    const slide = pres.addSlide();
    
    // ヘッダー
    slide.addShape(pres.shapes.RECT, { x: 0, y: 0, w: "100%", h: 0.8, fill: white });
    slide.addShape(pres.shapes.RECT, { x: 0, y: 0.75, w: "100%", h: 0.05, fill: "CCCCCC" }); // 下線
    
    // 提案番号と商品名
    slide.addShape(pres.shapes.OVAL, { x: 0.3, y: 0.15, w: 0.5, h: 0.5, fill: primaryColor });
    slide.addText(`${index + 1}`, { x: 0.3, y: 0.15, w: 0.5, h: 0.5, align: "center", fontSize: 18, bold: true, color: white, fontFace });
    slide.addText(`ご提案: ${rec.productName}`, { 
      x: 0.9, y: 0.15, w: "90%", fontSize: 24, bold: true, color: primaryColor, fontFace 
    });

    // 左側：提案の根拠（財務視点）
    slide.addText("■ 財務データに基づく提案理由", { 
      x: 0.5, y: 1.2, fontSize: 16, bold: true, color: "333333", fontFace 
    });
    slide.addShape(pres.shapes.RECT, { x: 0.5, y: 1.6, w: 9.0, h: 2.0, fill: "F0F4FF", line: { color: "D0D7E2" }, rx: 5 });
    slide.addText(rec.reasoning, { 
      x: 0.7, y: 1.7, w: 8.6, fontSize: 14, color: "333333", fontFace, breakLine: true 
    });

    // 右側/下側：具体的なアプローチ（セールストーク）
    slide.addText("■ 具体的なアプローチ・効果", { 
      x: 0.5, y: 4.0, fontSize: 16, bold: true, color: "333333", fontFace 
    });
    slide.addShape(pres.shapes.RECT, { x: 0.5, y: 4.4, w: 9.0, h: 2.2, fill: white, line: { color: accentColor, width: 2 }, rx: 5 });
    slide.addText(rec.salesTalk, { 
      x: 0.7, y: 4.5, w: 8.6, fontSize: 14, color: "333333", italic: true, fontFace, breakLine: true 
    });

    // フッター
    slide.addText("InsureConsult AI Analysis", { x: 10, y: 7.0, w: 3, align: "right", fontSize: 10, color: "999999", fontFace });
  });

  // ------------------------------------------
  // 4. エンドスライド
  // ------------------------------------------
  const slideEnd = pres.addSlide();
  slideEnd.background = { color: "333333" };
  slideEnd.addText("ご検討のほど、よろしくお願い申し上げます。", { 
    x: 0, y: 2.8, w: "100%", align: "center", fontSize: 28, color: white, fontFace 
  });
  slideEnd.addText("本資料はAIによる財務分析に基づき作成された参考資料です。", { 
    x: 0, y: 6.5, w: "100%", align: "center", fontSize: 12, color: "999999", fontFace 
  });

  // ファイル保存 (ダウンロード開始)
  await pres.writeFile({ fileName: `${financial.companyName}_保険提案書.pptx` });
};