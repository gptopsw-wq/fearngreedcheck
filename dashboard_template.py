# -*- coding: utf-8 -*-

def generate_html(data):
    """
    Generates a beautiful, responsive, and animated HTML dashboard
    comparing US and Korea Fear & Greed Index side-by-side.
    """
    import json
    data_json = json.dumps(data, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>한-미 공포 탐욕 지수 비교 대시보드</title>
    <!-- Google Fonts: Inter & Noto Sans KR -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #131a2c;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            /* Status Colors */
            --color-ex-fear: #ef4444;     /* Crimson */
            --color-fear: #f97316;        /* Orange */
            --color-neutral: #eab308;     /* Amber/Yellow */
            --color-greed: #84cc16;       /* Lime */
            --color-ex-greed: #22c55e;    /* Emerald */
            
            /* Font size overrides */
            --font-main: 'Inter', 'Noto Sans KR', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-main);
            line-height: 1.6;
            padding: 24px;
            min-height: 100vh;
        }}

        header {{
            max-width: 1400px;
            margin: 0 auto 24px auto;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
        }}

        .header-title h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .header-title p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .header-meta {{
            text-align: right;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .header-meta strong {{
            color: var(--text-secondary);
        }}

        main {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        /* Grid Layouts */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
        }}

        @media (max-width: 1024px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Card styling */
        .card {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: transparent;
        }}

        .card.us-card::before {{
            background: linear-gradient(90deg, #3b82f6, #06b6d4);
        }}

        .card.kr-card::before {{
            background: linear-gradient(90deg, #f97316, #ef4444);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            gap: 16px;
        }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .flag {{
            font-size: 1.3rem;
        }}

        .card-subtitle {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        /* Tab Switcher for Chart */
        .tab-container {{
            display: flex;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 2px;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 6px 14px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-family: var(--font-main);
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            background: var(--bg-card);
            color: var(--text-primary);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}

        /* Gauge Area */
        .gauge-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 10px 0 24px 0;
            position: relative;
        }}

        .gauge-svg {{
            width: 280px;
            height: 170px;
        }}

        .gauge-bg-arc {{
            fill: none;
            stroke: #1e293b;
            stroke-width: 14;
            stroke-linecap: round;
        }}

        .gauge-fill-arc {{
            fill: none;
            stroke-width: 14;
            stroke-linecap: round;
            stroke-dasharray: 251.2;
            stroke-dashoffset: 251.2; /* Will be set dynamically */
            transition: stroke-dashoffset 1.5s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}

        .gauge-needle {{
            transform-origin: 100px 110px;
            transform: rotate(-90deg); /* Will be set dynamically */
            transition: transform 1.5s cubic-bezier(0.25, 0.8, 0.25, 1);
            stroke: #f1f5f9;
            stroke-width: 3.5;
            stroke-linecap: round;
        }}

        .gauge-center-pin {{
            fill: #f1f5f9;
            stroke: var(--bg-secondary);
            stroke-width: 2;
        }}

        .gauge-labels {{
            display: flex;
            justify-content: space-between;
            width: 240px;
            margin-top: -15px;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-muted);
        }}

        .score-display {{
            text-align: center;
            margin-top: 10px;
        }}

        .score-value {{
            font-size: 3.2rem;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -1px;
            color: var(--text-primary);
        }}

        .score-regime {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            padding: 2px 10px;
            border-radius: 9999px;
            background-color: rgba(255, 255, 255, 0.05);
        }}

        /* History Table in Card */
        .history-box {{
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
            margin-top: 10px;
        }}

        .history-box h4 {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 12px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .history-grid-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            text-align: center;
        }}

        .history-item {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px 4px;
        }}

        .history-item-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}

        .history-item-val {{
            font-size: 1.1rem;
            font-weight: 700;
        }}

        .history-item-desc {{
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        /* Regime styles */
        .regime-extreme-fear {{ color: var(--color-ex-fear); }}
        .regime-fear {{ color: var(--color-fear); }}
        .regime-neutral {{ color: var(--color-neutral); }}
        .regime-greed {{ color: var(--color-greed); }}
        .regime-extreme-greed {{ color: var(--color-ex-greed); }}

        .bg-regime-extreme-fear {{ background-color: rgba(239, 68, 68, 0.1) !important; border-color: rgba(239, 68, 68, 0.2) !important; }}
        .bg-regime-fear {{ background-color: rgba(249, 115, 22, 0.1) !important; border-color: rgba(249, 115, 22, 0.2) !important; }}
        .bg-regime-neutral {{ background-color: rgba(234, 179, 8, 0.1) !important; border-color: rgba(234, 179, 8, 0.2) !important; }}
        .bg-regime-greed {{ background-color: rgba(132, 204, 22, 0.1) !important; border-color: rgba(132, 204, 22, 0.2) !important; }}
        .bg-regime-extreme-greed {{ background-color: rgba(34, 197, 94, 0.1) !important; border-color: rgba(34, 197, 94, 0.2) !important; }}

        /* Detailed Component Progress bars */
        .component-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .component-item {{
            display: grid;
            grid-template-columns: 120px 1fr 50px 80px;
            align-items: center;
            gap: 16px;
            font-size: 0.85rem;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }}

        .component-item:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .comp-name {{
            font-weight: 500;
            color: var(--text-primary);
        }}

        .comp-progress-container {{
            background-color: #1e293b;
            height: 8px;
            border-radius: 9999px;
            overflow: hidden;
            position: relative;
        }}

        .comp-progress-bar {{
            height: 100%;
            border-radius: 9999px;
            width: 0; /* Animated in JS */
            transition: width 1.2s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}

        .comp-score {{
            font-weight: 700;
            text-align: right;
            font-family: 'Inter', sans-serif;
        }}

        .comp-regime {{
            font-weight: 600;
            text-align: right;
            font-size: 0.8rem;
        }}

        /* Timeline Chart */
        .timeline-card {{
            width: 100%;
        }}

        .chart-container {{
            position: relative;
            height: 760px;
            width: 100%;
            margin-top: 15px;
        }}

        .chart-footnote {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 16px;
            line-height: 1.5;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.01);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}

        /* KR Analysis Card styling */
        .analysis-card {{
            grid-column: span 2;
        }}

        @media (max-width: 1024px) {{
            .analysis-card {{
                grid-column: span 1;
            }}
        }}

        .analysis-summary {{
            font-size: 1.05rem;
            font-weight: 500;
            color: var(--text-primary);
            padding: 14px;
            border-left: 4px solid var(--color-fear);
            background: rgba(255, 255, 255, 0.02);
            border-radius: 0 12px 12px 0;
            margin-bottom: 20px;
            white-space: pre-line;
        }}

        .analysis-details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 768px) {{
            .analysis-details-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .analysis-section {{
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 16px;
        }}

        .analysis-section h4 {{
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .analysis-section ul {{
            padding-left: 20px;
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .analysis-section li {{
            line-height: 1.4;
        }}

        /* Footer Info */
        .footer-info {{
            max-width: 1400px;
            margin: 24px auto 0 auto;
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .footer-info a {{
            color: var(--text-secondary);
            text-decoration: none;
        }}

        .footer-info a:hover {{
            text-decoration: underline;
        }}

        .indicator-scale-legend {{
            display: flex;
            gap: 12px;
            font-size: 0.7rem;
            justify-content: center;
            margin-bottom: 8px;
        }}

        .legend-chip {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .legend-color {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-title">
            <h1>한-미 공포 탐욕 지수 비교 대시보드</h1>
            <p>미국 S&P 500 시장과 한국 KOSPI 시장의 투자 심리 분석</p>
        </div>
        <div class="header-meta">
            마지막 업데이트: <strong>{data['timestamp']}</strong> (KST)<br>
            데이터 출처: <strong>CNN Business, GitHub Archive & KOSPI FGI (FDR)</strong>
        </div>
    </header>

    <main>
        <!-- Top Section: Gauges -->
        <div class="grid-2">
            <!-- US Card -->
            <div class="card us-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">
                            <span class="flag">🇺🇸</span> 미국 시장 공포 탐욕 지수
                        </div>
                        <div class="card-subtitle">CNN Business Fear & Greed Index (S&P 500)</div>
                    </div>
                </div>
                
                <div class="gauge-container">
                    <svg viewBox="0 0 200 120" class="gauge-svg">
                        <defs>
                            <linearGradient id="us-gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="var(--color-ex-fear)" />
                                <stop offset="25%" stop-color="var(--color-fear)" />
                                <stop offset="50%" stop-color="var(--color-neutral)" />
                                <stop offset="75%" stop-color="var(--color-greed)" />
                                <stop offset="100%" stop-color="var(--color-ex-greed)" />
                            </linearGradient>
                        </defs>
                        <path d="M 20 110 A 80 80 0 0 1 180 110" class="gauge-bg-arc" />
                        <path id="us-gauge-fill" d="M 20 110 A 80 80 0 0 1 180 110" class="gauge-fill-arc" stroke="url(#us-gauge-grad)" />
                        <line id="us-needle" x1="100" y1="110" x2="100" y2="40" class="gauge-needle" />
                        <circle cx="100" cy="110" r="5" class="gauge-center-pin" />
                    </svg>
                    <div class="gauge-labels">
                        <span>극단적 공포</span>
                        <span>중립</span>
                        <span>극단적 탐욕</span>
                    </div>
                    
                    <div class="score-display">
                        <div class="score-value">{data['us_current']['score']:.1f}</div>
                        <div id="us-regime" class="score-regime">로드 중...</div>
                    </div>
                </div>
                
                <div class="history-box">
                    <h4>이전 지수 변화</h4>
                    <div class="history-grid-row">
                        <div class="history-item">
                            <div class="history-item-label">어제 종가</div>
                            <div class="history-item-val">{data['us_current']['previous_close']:.0f}</div>
                            <div class="history-item-desc" id="us-hist-1d"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">1주일 전</div>
                            <div class="history-item-val">{data['us_current']['previous_1_week']:.0f}</div>
                            <div class="history-item-desc" id="us-hist-1w"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">1개월 전</div>
                            <div class="history-item-val">{data['us_current']['previous_1_month']:.0f}</div>
                            <div class="history-item-desc" id="us-hist-1m"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">1년 전</div>
                            <div class="history-item-val">{data['us_current']['previous_1_year']:.0f}</div>
                            <div class="history-item-desc" id="us-hist-1y"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- KR Card -->
            <div class="card kr-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">
                            <span class="flag">🇰🇷</span> 한국 시장 공포 탐욕 지수
                        </div>
                        <div class="card-subtitle">KOSPI Fear & Greed Index (KOSPI)</div>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-align: right;">
                        기준일: {data['kr_current']['date']}
                    </div>
                </div>
                
                <div class="gauge-container">
                    <svg viewBox="0 0 200 120" class="gauge-svg">
                        <defs>
                            <linearGradient id="kr-gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="var(--color-ex-fear)" />
                                <stop offset="25%" stop-color="var(--color-fear)" />
                                <stop offset="50%" stop-color="var(--color-neutral)" />
                                <stop offset="75%" stop-color="var(--color-greed)" />
                                <stop offset="100%" stop-color="var(--color-ex-greed)" />
                            </linearGradient>
                        </defs>
                        <path d="M 20 110 A 80 80 0 0 1 180 110" class="gauge-bg-arc" />
                        <path id="kr-gauge-fill" d="M 20 110 A 80 80 0 0 1 180 110" class="gauge-fill-arc" stroke="url(#kr-gauge-grad)" />
                        <line id="kr-needle" x1="100" y1="110" x2="100" y2="40" class="gauge-needle" />
                        <circle cx="100" cy="110" r="5" class="gauge-center-pin" />
                    </svg>
                    <div class="gauge-labels">
                        <span>극단적 공포</span>
                        <span>중립</span>
                        <span>극단적 탐욕</span>
                    </div>
                    
                    <div class="score-display">
                        <div class="score-value">{data['kr_current']['score']:.1f}</div>
                        <div id="kr-regime" class="score-regime">로드 중...</div>
                    </div>
                </div>
                
                <div class="history-box">
                    <h4>이전 지수 변화</h4>
                    <div class="history-grid-row">
                        <div class="history-item">
                            <div class="history-item-label">이전 영업일</div>
                            <div class="history-item-val">{data['kr_current']['previous_close']:.1f}</div>
                            <div class="history-item-desc" id="kr-hist-1d"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">1주일 전</div>
                            <div class="history-item-val">{data['kr_current']['previous_1_week']:.1f}</div>
                            <div class="history-item-desc" id="kr-hist-1w"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">1개월 전</div>
                            <div class="history-item-val">{data['kr_current']['previous_1_month']:.1f}</div>
                            <div class="history-item-desc" id="kr-hist-1m"></div>
                        </div>
                        <div class="history-item">
                            <div class="history-item-label">3개월 전</div>
                            <div class="history-item-val">{data['kr_current']['previous_3_month']:.1f}</div>
                            <div class="history-item-desc" id="kr-hist-3m"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Timeline Section -->
        <div class="card timeline-card">
            <div class="card-header">
                <div>
                    <div class="card-title">한-미 공포 탐욕 지수 역사적 추이 비교</div>
                    <div class="card-subtitle">시장 정서 동향 비교 (미국 S&P 500 FGI vs 한국 KOSPI FGI)</div>
                </div>
                <div class="tab-container">
                    <button id="tab-3m" class="tab-btn active" onclick="switchTimeline('3m')">최근 3개월 (일별)</button>
                    <button id="tab-10y" class="tab-btn" onclick="switchTimeline('10y')">최근 10년 (주별)</button>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="timelineChart"></canvas>
            </div>
            <div id="chart-desc" class="chart-footnote">
                두 국가 지수의 일일 공포 탐욕 지수 이력을 동기화하여 비교합니다.
            </div>
        </div>

        <!-- Details Grid -->
        <div class="grid-2">
            <!-- US Components -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">🇺🇸 미국 지수 구성 지표 현황</div>
                        <div class="card-subtitle">7개 주요 시장 정서 지표 세부 점수</div>
                    </div>
                </div>
                <div class="component-list" id="us-components-list">
                    <!-- Dynamic -->
                </div>
            </div>

            <!-- KR Components -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">🇰🇷 한국 지수 구성 지표 현황</div>
                        <div class="card-subtitle">8개 주요 시장 정서 지표 세부 점수</div>
                    </div>
                </div>
                <div class="component-list" id="kr-components-list">
                    <!-- Dynamic -->
                </div>
            </div>

            <!-- KR AI analysis summary -->
            <div class="card analysis-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">💡 한국 증시 투자 정서 AI 요약 (KOSPI FGI 제공)</div>
                        <div class="card-subtitle">최근 시장 동향 및 위협/기회 분석</div>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">
                        분석 신뢰도: {data['kr_analysis']['confidence'] * 100:.0f}%
                    </div>
                </div>
                
                <div class="analysis-summary">
                    {data['kr_analysis']['summary']}
                </div>
                
                <div class="analysis-details-grid">
                    <div class="analysis-section">
                        <h4 style="color: var(--color-ex-fear);">⚠️ 위협 요인 (Risks)</h4>
                        <ul id="kr-risks">
                            <!-- Dynamic -->
                        </ul>
                    </div>
                    <div class="analysis-section">
                        <h4 style="color: var(--color-ex-greed);">✨ 지지 요인 (Claims)</h4>
                        <ul id="kr-claims">
                            <!-- Dynamic -->
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <div class="footer-info">
        <div>
            <div class="indicator-scale-legend">
                <div class="legend-chip"><div class="legend-color" style="background-color: var(--color-ex-fear)"></div><span>극단적 공포 (0-24)</span></div>
                <div class="legend-chip"><div class="legend-color" style="background-color: var(--color-fear)"></div><span>공포 (25-44)</span></div>
                <div class="legend-chip"><div class="legend-color" style="background-color: var(--color-neutral)"></div><span>중립 (45-55)</span></div>
                <div class="legend-chip"><div class="legend-color" style="background-color: var(--color-greed)"></div><span>탐욕 (56-75)</span></div>
                <div class="legend-chip"><div class="legend-color" style="background-color: var(--color-ex-greed)"></div><span>극단적 탐욕 (76-100)</span></div>
            </div>
            본 대시보드는 CNN Business 및 KOSPI FGI의 실시간 데이터를 집계하여 개인 투자 용도로 제공합니다.
        </div>
        <div>
            <a href="https://edition.cnn.com/markets/fear-and-greed" target="_blank">CNN F&G</a> | 
            <a href="https://kospifgi.com" target="_blank">KOSPI FGI</a>
        </div>
    </div>

    <script>
        const dashboardData = {data_json};
        let timelineChart = null;
        
        // Helper to translate and format regime descriptions
        function getRegime(score) {{
            if (score < 25) return {{ name: '극단적 공포', class: 'regime-extreme-fear', bgClass: 'bg-regime-extreme-fear' }};
            if (score < 45) return {{ name: '공포', class: 'regime-fear', bgClass: 'bg-regime-fear' }};
            if (score <= 55) return {{ name: '중립', class: 'regime-neutral', bgClass: 'bg-regime-neutral' }};
            if (score <= 75) return {{ name: '탐욕', class: 'regime-greed', bgClass: 'bg-regime-greed' }};
            return {{ name: '극단적 탐욕', class: 'regime-extreme-greed', bgClass: 'bg-regime-extreme-greed' }};
        }}

        function getRegimeFromKey(key) {{
            const mapping = {{
                'extreme_fear': {{ name: '극단적 공포', class: 'regime-extreme-fear', bgClass: 'bg-regime-extreme-fear' }},
                'fear': {{ name: '공포', class: 'regime-fear', bgClass: 'bg-regime-fear' }},
                'neutral': {{ name: '중립', class: 'regime-neutral', bgClass: 'bg-regime-neutral' }},
                'greed': {{ name: '탐욕', class: 'regime-greed', bgClass: 'bg-regime-greed' }},
                'extreme_greed': {{ name: '극단적 탐욕', class: 'regime-extreme-greed', bgClass: 'bg-regime-extreme-greed' }}
            }};
            return mapping[key.toLowerCase().replace(' ', '_').replace('-', '_')] || {{ name: key, class: 'regime-neutral', bgClass: 'bg-regime-neutral' }};
        }}

        // Initialize Gauges
        function setupGauges() {{
            const usScore = dashboardData.us_current.score;
            const krScore = dashboardData.kr_current.score;
            
            // US Gauge
            const usRegime = getRegimeFromKey(dashboardData.us_current.rating);
            const usRegimeEl = document.getElementById('us-regime');
            usRegimeEl.innerText = usRegime.name;
            usRegimeEl.className = 'score-regime ' + usRegime.class + ' ' + usRegime.bgClass;
            
            // Set gauge fill stroke dashoffset (circumference is 251.2)
            const usFillOffset = 251.2 - (usScore / 100) * 251.2;
            document.getElementById('us-gauge-fill').style.strokeDashoffset = usFillOffset;
            // Set needle rotation (starts at -90deg for score 0, ends at 90deg for score 100)
            const usNeedleRot = -90 + (usScore * 1.8);
            document.getElementById('us-needle').style.transform = `rotate(${{usNeedleRot}}deg)`;

            // KR Gauge
            const krRegime = getRegimeFromKey(dashboardData.kr_current.rating);
            const krRegimeEl = document.getElementById('kr-regime');
            krRegimeEl.innerText = krRegime.name;
            krRegimeEl.className = 'score-regime ' + krRegime.class + ' ' + krRegime.bgClass;
            
            const krFillOffset = 251.2 - (krScore / 100) * 251.2;
            document.getElementById('kr-gauge-fill').style.strokeDashoffset = krFillOffset;
            const krNeedleRot = -90 + (krScore * 1.8);
            document.getElementById('kr-needle').style.transform = `rotate(${{krNeedleRot}}deg)`;
            
            // Setup history desc text
            document.getElementById('us-hist-1d').innerText = getRegime(dashboardData.us_current.previous_close).name;
            document.getElementById('us-hist-1w').innerText = getRegime(dashboardData.us_current.previous_1_week).name;
            document.getElementById('us-hist-1m').innerText = getRegime(dashboardData.us_current.previous_1_month).name;
            document.getElementById('us-hist-1y').innerText = getRegime(dashboardData.us_current.previous_1_year).name;

            document.getElementById('kr-hist-1d').innerText = getRegime(dashboardData.kr_current.previous_close).name;
            document.getElementById('kr-hist-1w').innerText = getRegime(dashboardData.kr_current.previous_1_week).name;
            document.getElementById('kr-hist-1m').innerText = getRegime(dashboardData.kr_current.previous_1_month).name;
            document.getElementById('kr-hist-3m').innerText = getRegime(dashboardData.kr_current.previous_3_month).name;
        }}

        // Setup subcomponents list
        function setupComponents() {{
            // US
            const usList = document.getElementById('us-components-list');
            dashboardData.us_components.forEach(comp => {{
                const regimeInfo = getRegime(comp.score);
                const item = document.createElement('div');
                item.className = 'component-item';
                item.innerHTML = `
                    <span class="comp-name">${{comp.name}}</span>
                    <div class="comp-progress-container">
                        <div class="comp-progress-bar" style="background-color: var(--color-${{regimeInfo.class.replace('regime-', '')}});"></div>
                    </div>
                    <span class="comp-score">${{comp.score.toFixed(0)}}</span>
                    <span class="comp-regime ${{regimeInfo.class}}">${{regimeInfo.name}}</span>
                `;
                usList.appendChild(item);
                // Trigger animation
                setTimeout(() => {{
                    item.querySelector('.comp-progress-bar').style.width = comp.score + '%';
                }}, 100);
            }});

            // KR
            const krList = document.getElementById('kr-components-list');
            dashboardData.kr_components.forEach(comp => {{
                const regimeInfo = getRegime(comp.score);
                const item = document.createElement('div');
                item.className = 'component-item';
                item.innerHTML = `
                    <span class="comp-name">${{comp.name}}</span>
                    <div class="comp-progress-container">
                        <div class="comp-progress-bar" style="background-color: var(--color-${{regimeInfo.class.replace('regime-', '')}});"></div>
                    </div>
                    <span class="comp-score">${{comp.score.toFixed(0)}}</span>
                    <span class="comp-regime ${{regimeInfo.class}}">${{regimeInfo.name}}</span>
                `;
                krList.appendChild(item);
                // Trigger animation
                setTimeout(() => {{
                    item.querySelector('.comp-progress-bar').style.width = comp.score + '%';
                }}, 100);
            }});
        }}

        // Setup AI Analysis Risks & Claims
        function setupAiAnalysis() {{
            const risksList = document.getElementById('kr-risks');
            dashboardData.kr_analysis.risks.forEach(risk => {{
                const li = document.createElement('li');
                li.innerText = risk;
                risksList.appendChild(li);
            }});

            const claimsList = document.getElementById('kr-claims');
            dashboardData.kr_analysis.claims.forEach(claim => {{
                const li = document.createElement('li');
                li.innerText = claim;
                claimsList.appendChild(li);
            }});
        }}

        // Setup Chart.js Timeline comparison
        function setupTimelineChart() {{
            const ctx = document.getElementById('timelineChart').getContext('2d');
            
            // Gradient fills
            const usGradient = ctx.createLinearGradient(0, 0, 0, 350);
            usGradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
            usGradient.addColorStop(1, 'rgba(59, 130, 246, 0.00)');

            const krGradient = ctx.createLinearGradient(0, 0, 0, 350);
            krGradient.addColorStop(0, 'rgba(249, 115, 22, 0.25)');
            krGradient.addColorStop(1, 'rgba(249, 115, 22, 0.00)');

            timelineChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dashboardData.history_dates,
                    datasets: [
                        {{
                            label: '미국 FGI (S&P 500)',
                            data: dashboardData.us_history_scores,
                            borderColor: '#3b82f6',
                            borderWidth: 2.5,
                            backgroundColor: usGradient,
                            fill: true,
                            tension: 0.2,
                            pointRadius: 0,
                            pointHoverRadius: 5,
                            pointHoverBackgroundColor: '#3b82f6',
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 2
                        }},
                        {{
                            label: '한국 FGI (KOSPI)',
                            data: dashboardData.kr_history_scores,
                            borderColor: '#f97316',
                            borderWidth: 2.5,
                            backgroundColor: krGradient,
                            fill: true,
                            tension: 0.2,
                            pointRadius: 0,
                            pointHoverRadius: 5,
                            pointHoverBackgroundColor: '#f97316',
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 2
                        }},
                        {{
                            label: `미국 10년 평균 (${{dashboardData.us_history_10y_avg}})`,
                            data: [], // Starts empty for 3m view
                            borderColor: 'rgba(59, 130, 246, 0.4)',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            fill: false,
                            pointRadius: 0,
                            pointHoverRadius: 0
                        }},
                        {{
                            label: `한국 10년 평균 (${{dashboardData.kr_history_10y_avg}})`,
                            data: [], // Starts empty for 3m view
                            borderColor: 'rgba(249, 115, 22, 0.4)',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            fill: false,
                            pointRadius: 0,
                            pointHoverRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.05)',
                                borderColor: 'rgba(255, 255, 255, 0.1)'
                            }},
                            ticks: {{
                                color: '#94a3b8',
                                font: {{
                                    family: 'Inter',
                                    size: 11
                                }},
                                maxTicksLimit: 12
                            }}
                        }},
                        y: {{
                            min: 0,
                            max: 100,
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.05)',
                                borderColor: 'rgba(255, 255, 255, 0.1)'
                            }},
                            ticks: {{
                                color: '#94a3b8',
                                font: {{
                                    family: 'Inter',
                                    size: 11
                                }},
                                stepSize: 20
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'top',
                            labels: {{
                                color: '#f8fafc',
                                font: {{
                                    family: 'Inter',
                                    weight: 500,
                                    size: 12
                                }},
                                boxWidth: 12,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: '#1e293b',
                            titleColor: '#f8fafc',
                            bodyColor: '#94a3b8',
                            borderColor: '#334155',
                            borderWidth: 1,
                            padding: 12,
                            titleFont: {{
                                family: 'Inter',
                                weight: 600
                            }},
                            bodyFont: {{
                                family: 'Inter',
                                size: 12
                            }},
                            callbacks: {{
                                labelColor: function(context) {{
                                    return {{
                                        borderColor: context.dataset.borderColor,
                                        backgroundColor: context.dataset.borderColor
                                    }};
                                }},
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    if (context.parsed.y !== null) {{
                                        label += context.parsed.y.toFixed(1);
                                    }}
                                    return label;
                                }}
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    id: 'crosshair',
                    afterInit: (chart) => {{
                        chart.crosshair = {{
                            x: 0,
                            y: 0,
                            draw: false
                        }};
                    }},
                    afterEvent: (chart, args) => {{
                        const {{type}} = args.event;
                        const {{top, bottom, left, right}} = chart.chartArea;
                        const x = args.event.x;
                        const y = args.event.y;
                        
                        const isInside = x >= left && x <= right && y >= top && y <= bottom;
                        
                        if (type === 'mousemove' && isInside) {{
                            chart.crosshair.x = x;
                            chart.crosshair.y = y;
                            chart.crosshair.draw = true;
                            args.changed = true;
                        }} else if (type === 'mouseout' || !isInside) {{
                            chart.crosshair.draw = false;
                            args.changed = true;
                        }}
                    }},
                    afterDraw: (chart) => {{
                        if (!chart.crosshair || !chart.crosshair.draw) return;
                        const {{ctx, chartArea: {{top, bottom, left, right}}}} = chart;
                        const {{x, y}} = chart.crosshair;
                        
                        ctx.save();
                        ctx.beginPath();
                        ctx.lineWidth = 1;
                        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
                        ctx.setLineDash([4, 4]);
                        
                        // Vertical line
                        ctx.moveTo(x, top);
                        ctx.lineTo(x, bottom);
                        
                        // Horizontal line
                        ctx.moveTo(left, y);
                        ctx.lineTo(right, y);
                        ctx.stroke();
                        
                        // Draw Y value pill on Y-axis
                        const yValue = chart.scales.y.getValueForPixel(y);
                        if (yValue !== undefined) {{
                            ctx.beginPath();
                            ctx.setLineDash([]);
                            ctx.fillStyle = '#1e293b';
                            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                            ctx.lineWidth = 1;
                            
                            const text = yValue.toFixed(1);
                            ctx.font = '500 11px Inter, Noto Sans KR';
                            const textWidth = ctx.measureText(text).width;
                            const paddingX = 6;
                            
                            const rectX = left - textWidth - paddingX * 2 - 4;
                            const rectY = y - 8;
                            const rectW = textWidth + paddingX * 2;
                            const rectH = 16;
                            
                            if (ctx.roundRect) {{
                                ctx.roundRect(rectX, rectY, rectW, rectH, 4);
                            }} else {{
                                ctx.rect(rectX, rectY, rectW, rectH);
                            }}
                            ctx.fill();
                            ctx.stroke();
                            
                            ctx.fillStyle = '#f8fafc';
                            ctx.fillText(text, rectX + paddingX, y + 4);
                        }}
                        
                        ctx.restore();
                    }}
                }}]
            }});
        }}

        // Handle swapping chart between 3M (daily) and 10Y (weekly)
        function switchTimeline(preset) {{
            if (!timelineChart) return;
            
            // Toggle active tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById('tab-' + preset).classList.add('active');
            
            const descEl = document.getElementById('chart-desc');
            const usAvgVal = dashboardData.us_history_10y_avg;
            const krAvgVal = dashboardData.kr_history_10y_avg;

            if (preset === '3m') {{
                timelineChart.data.labels = dashboardData.history_dates;
                timelineChart.data.datasets[0].data = dashboardData.us_history_scores;
                timelineChart.data.datasets[0].label = '미국 FGI (S&P 500)';
                timelineChart.data.datasets[1].data = dashboardData.kr_history_scores;
                timelineChart.data.datasets[1].label = '한국 FGI (KOSPI)';
                
                // Hide averages on 3m view
                timelineChart.data.datasets[2].data = [];
                timelineChart.data.datasets[3].data = [];
                
                timelineChart.options.scales.x.ticks.maxTicksLimit = 12;
                descEl.innerHTML = "두 국가 지수의 <strong>일일 공포 탐욕 지수 공식 이력</strong>을 동기화하여 비교합니다. (최근 약 3개월)";
            }} else {{
                timelineChart.data.labels = dashboardData.history_10y_dates;
                timelineChart.data.datasets[0].data = dashboardData.us_history_10y_scores;
                timelineChart.data.datasets[0].label = '미국 FGI (S&P 500 - 공식)';
                timelineChart.data.datasets[1].data = dashboardData.kr_history_10y_scores;
                timelineChart.data.datasets[1].label = '한국 FGI (KOSPI - 프록시)';
                
                // Fill averages for 10y view
                const len = dashboardData.history_10y_dates.length;
                timelineChart.data.datasets[2].data = Array(len).fill(usAvgVal);
                timelineChart.data.datasets[3].data = Array(len).fill(krAvgVal);
                
                timelineChart.options.scales.x.ticks.maxTicksLimit = 15;
                descEl.innerHTML = `※ <strong>최근 10년 (주별)</strong>: 미국 지수는 공식 기록(GitHub Archive, 10년 평균: <strong>${{usAvgVal}}</strong>)이며, 한국 지수는 KOSPI FGI 사이트에서 장기 이력을 제공하지 않으므로 <strong>자체 계산한 4요인 공포 탐욕 프록시 지수</strong>(10년 평균: <strong>${{krAvgVal}}</strong>, 실제 지수와 상관관계 r ≈ 0.87)를 시각화하였습니다. 점선은 각 지수의 10년 역사적 평균선입니다.`;
            }}
            
            timelineChart.update();
        }}

        window.onload = function() {{
            setupGauges();
            setupComponents();
            setupAiAnalysis();
            setupTimelineChart();
        }};
    </script>
</body>
</html>
"""
    return html
