import asyncio
import json
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import base64

# ─── CONFIG ──────────────────────────────────────────────────────────────────
TURBO_URLS = [
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # First tab
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # Second tab
]

# Global variable to store pages for dashboard updates
pages = []
# Enhanced data storage for turbo analytics
trading_data = {
    "session_start": datetime.now().isoformat(),
    "turbos": {
        "long": {"prices": [], "bids": [], "asks": [], "spreads": [], "analytics": {}},
        "short": {"prices": [], "bids": [], "asks": [], "spreads": [], "analytics": {}}
    },
    "underlying": [],
    "strategy_signals": [],
    "arbitrage_opportunities": [],
    "volatility_events": [],
    "patterns": []
}
# ────────────────────────────────────────────────────────────────────────────

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        
        # Initialize variables
        global pages
        pages = []
        
        print("🚀 Creating ULTIMATE Turbo Strategy Analytics Dashboard...")
        
        # Create dashboard page first
        dashboard_page = await ctx.new_page()
        
        # ULTIMATE Turbo Analytics Dashboard with EVERYTHING for strategy development
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Ultimate Turbo Strategy Analytics</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 8px;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1a2e 50%, #16213e 100%);
            color: white; min-height: 100vh; font-size: 12px;
        }
        .dashboard { max-width: 2000px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 15px; }
        .header h1 { font-size: 1.8em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); color: #00ff88; }
        .header p { margin: 3px 0; opacity: 0.9; color: #88ccff; }
        
        .controls { 
            display: flex; justify-content: center; gap: 12px; margin-bottom: 15px; flex-wrap: wrap;
            background: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px;
        }
        .btn { 
            padding: 6px 14px; border: none; border-radius: 18px; font-size: 11px; 
            font-weight: bold; cursor: pointer; transition: all 0.3s ease; 
            text-transform: uppercase; letter-spacing: 0.5px; 
        }
        .btn-reset { background: linear-gradient(45deg, #ff6b6b, #ff8e53); color: white; }
        .btn-toggle { background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; }
        .btn-analyze { background: linear-gradient(45deg, #667eea, #764ba2); color: white; }
        .btn-strategy { background: linear-gradient(45deg, #f093fb, #f5576c); color: white; }
        
        .main-grid { display: grid; grid-template-columns: 1fr 1fr 350px; gap: 12px; margin-bottom: 12px; }
        
        /* TURBO ANALYTICS PANELS */
        .turbo-panel { 
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); 
            border-radius: 15px; padding: 12px; border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .turbo-title { 
            font-size: 1.1em; font-weight: bold; margin-bottom: 10px; text-align: center;
            padding: 8px; border-radius: 10px; text-transform: uppercase; letter-spacing: 1px;
        }
        .long-title { background: linear-gradient(45deg, #00ff88, #00cc66); color: #000; }
        .short-title { background: linear-gradient(45deg, #ff4444, #cc0000); color: #fff; }
        
        .analytics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
        .metric-card { 
            background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 8px; text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric-title { font-size: 0.7em; opacity: 0.8; margin-bottom: 3px; text-transform: uppercase; }
        .metric-value { font-size: 1.1em; font-weight: bold; margin-bottom: 3px; }
        .metric-change { font-size: 0.7em; padding: 2px 6px; border-radius: 10px; }
        
        .bid-ask-display { 
            display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 10px;
        }
        .ba-card { 
            background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 6px; text-align: center;
        }
        .bid-card { border-left: 3px solid #ff4444; }
        .ask-card { border-left: 3px solid #00ff88; }
        .spread-card { border-left: 3px solid #ffaa00; }
        
        .turbo-chart { height: 200px; margin-bottom: 10px; }
        
        /* STRATEGY PANEL */
        .strategy-panel { 
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); 
            border-radius: 15px; padding: 12px; border: 1px solid rgba(249, 115, 22, 0.5);
        }
        .strategy-section { margin-bottom: 15px; }
        .strategy-title { 
            font-size: 0.9em; font-weight: bold; margin-bottom: 8px; 
            color: #f97316; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .signal-item { 
            display: flex; justify-content: space-between; margin: 4px 0; 
            padding: 4px 8px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; font-size: 0.8em;
            border-left: 3px solid transparent;
        }
        .signal-bullish { border-left-color: #00ff88; background: rgba(0, 255, 136, 0.1); }
        .signal-bearish { border-left-color: #ff4444; background: rgba(255, 68, 68, 0.1); }
        .signal-neutral { border-left-color: #888; background: rgba(136, 136, 136, 0.1); }
        
        .arbitrage-alert { 
            background: linear-gradient(45deg, #ff6b6b, #ffa500); 
            color: white; padding: 8px; border-radius: 8px; margin: 5px 0;
            font-weight: bold; text-align: center; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        /* COMPARATIVE ANALYTICS */
        .comparison-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
        .comparison-card { 
            background: rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px; text-align: center;
            border: 1px solid rgba(132, 204, 22, 0.3);
        }
        
        /* CHARTS SECTION */
        .charts-section { display: grid; grid-template-columns: 2fr 1fr; gap: 12px; margin-bottom: 12px; }
        .main-chart { 
            background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); 
            border-radius: 15px; padding: 12px; height: 350px;
        }
        .mini-charts { display: flex; flex-direction: column; gap: 8px; }
        .mini-chart { 
            background: rgba(255, 255, 255, 0.08); border-radius: 10px; 
            padding: 8px; height: 110px; flex: 1;
        }
        
        /* DATA STREAM */
        .data-panels { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
        .data-panel { 
            background: rgba(255, 255, 255, 0.08); border-radius: 12px; 
            padding: 12px; height: 200px; overflow-y: auto;
        }
        .data-item { 
            margin: 2px 0; padding: 3px 6px; background: rgba(255, 255, 255, 0.05); 
            border-radius: 4px; font-size: 0.7em; border-left: 2px solid #60a5fa;
        }
        
        .positive { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .negative { background: rgba(255, 68, 68, 0.2); color: #ff4444; }
        .neutral { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }
        
        .connection-status { 
            position: fixed; top: 10px; right: 10px; padding: 6px 12px; border-radius: 20px; 
            font-weight: bold; backdrop-filter: blur(10px); font-size: 0.8em; z-index: 1000;
            background: rgba(0, 255, 136, 0.2); color: #00ff88; border: 1px solid #00ff88;
        }
        
        .volatility-bar { 
            width: 100%; height: 6px; background: rgba(255, 255, 255, 0.1); 
            border-radius: 3px; overflow: hidden; margin-top: 3px;
        }
        .vol-fill { 
            height: 100%; border-radius: 3px; transition: all 0.3s ease;
            background: linear-gradient(90deg, #00ff88 0%, #ffaa00 50%, #ff4444 100%);
        }
        
        .momentum-indicator { 
            display: inline-block; padding: 2px 6px; border-radius: 8px; 
            font-size: 0.65em; margin: 1px; font-weight: bold;
        }
        .momentum-strong-up { background: rgba(0, 255, 136, 0.3); color: #00ff88; }
        .momentum-weak-up { background: rgba(132, 204, 22, 0.3); color: #84cc16; }
        .momentum-strong-down { background: rgba(255, 68, 68, 0.3); color: #ff4444; }
        .momentum-weak-down { background: rgba(239, 68, 54, 0.3); color: #ef4444; }
        .momentum-flat { background: rgba(156, 163, 175, 0.3); color: #9ca3af; }
        
        .strategy-confidence { 
            width: 100%; height: 20px; background: rgba(255, 255, 255, 0.1); 
            border-radius: 10px; overflow: hidden; margin: 5px 0;
        }
        .confidence-fill { 
            height: 100%; border-radius: 10px; transition: all 0.5s ease;
            background: linear-gradient(90deg, #ff4444 0%, #ffaa00 50%, #00ff88 100%);
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 ULTIMATE TURBO STRATEGY ANALYTICS</h1>
            <p>Real-time turbo analysis, arbitrage detection, and algorithmic strategy development</p>
        </div>
        
        <div class="connection-status">
            <span id="statusText">🟢 Live Analytics</span>
        </div>
        
        <div class="controls">
            <button class="btn btn-reset" onclick="resetBaseline()">🔄 Reset</button>
            <button class="btn btn-toggle" onclick="togglePause()" id="pauseBtn">⏸️ Pause</button>
            <button class="btn btn-analyze" onclick="runDeepAnalysis()">🧠 Deep Analysis</button>
            <button class="btn btn-strategy" onclick="generateSignals()">📈 Generate Signals</button>
            <button class="btn btn-toggle" onclick="exportStrategicData()">💾 Export Strategy Data</button>
            <button class="btn btn-strategy" onclick="detectArbitrage()">💰 Find Arbitrage</button>
        </div>
        
        <!-- MAIN ANALYTICS GRID -->
        <div class="main-grid">
            <!-- LONG TURBO ANALYTICS -->
            <div class="turbo-panel">
                <div class="turbo-title long-title">🟢 LONG TURBO ANALYTICS</div>
                
                <div class="bid-ask-display">
                    <div class="ba-card bid-card">
                        <div class="metric-title">Current Bid</div>
                        <div class="metric-value" id="longBid">-</div>
                    </div>
                    <div class="ba-card ask-card">
                        <div class="metric-title">Current Ask</div>
                        <div class="metric-value" id="longAsk">-</div>
                    </div>
                    <div class="ba-card spread-card">
                        <div class="metric-title">Spread</div>
                        <div class="metric-value" id="longSpread">-</div>
                    </div>
                </div>
                
                <div class="analytics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Price</div>
                        <div class="metric-value" id="longPrice">-</div>
                        <div class="metric-change neutral" id="longChange">+0.00%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Volatility</div>
                        <div class="metric-value" id="longVolatility">-</div>
                        <div class="volatility-bar"><div class="vol-fill" id="longVolBar" style="width: 0%"></div></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Momentum</div>
                        <div class="metric-value" id="longMomentum">-</div>
                        <span class="momentum-indicator momentum-flat" id="longMomentumInd">FLAT</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">RSI</div>
                        <div class="metric-value" id="longRSI">-</div>
                        <div class="metric-change neutral" id="longRSISignal">NEUTRAL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">SMA Trend</div>
                        <div class="metric-value" id="longSMA">-</div>
                        <div class="metric-change neutral" id="longTrend">NEUTRAL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Volume Pressure</div>
                        <div class="metric-value" id="longVolumePressure">-</div>
                        <div class="metric-change neutral" id="longPressureDir">BALANCED</div>
                    </div>
                </div>
                
                <canvas id="longChart" class="turbo-chart" width="400" height="200"></canvas>
            </div>
            
            <!-- SHORT TURBO ANALYTICS -->
            <div class="turbo-panel">
                <div class="turbo-title short-title">🔴 SHORT TURBO ANALYTICS</div>
                
                <div class="bid-ask-display">
                    <div class="ba-card bid-card">
                        <div class="metric-title">Current Bid</div>
                        <div class="metric-value" id="shortBid">-</div>
                    </div>
                    <div class="ba-card ask-card">
                        <div class="metric-title">Current Ask</div>
                        <div class="metric-value" id="shortAsk">-</div>
                    </div>
                    <div class="ba-card spread-card">
                        <div class="metric-title">Spread</div>
                        <div class="metric-value" id="shortSpread">-</div>
                    </div>
                </div>
                
                <div class="analytics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Price</div>
                        <div class="metric-value" id="shortPrice">-</div>
                        <div class="metric-change neutral" id="shortChange">+0.00%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Volatility</div>
                        <div class="metric-value" id="shortVolatility">-</div>
                        <div class="volatility-bar"><div class="vol-fill" id="shortVolBar" style="width: 0%"></div></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Momentum</div>
                        <div class="metric-value" id="shortMomentum">-</div>
                        <span class="momentum-indicator momentum-flat" id="shortMomentumInd">FLAT</span>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">RSI</div>
                        <div class="metric-value" id="shortRSI">-</div>
                        <div class="metric-change neutral" id="shortRSISignal">NEUTRAL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">SMA Trend</div>
                        <div class="metric-value" id="shortSMA">-</div>
                        <div class="metric-change neutral" id="shortTrend">NEUTRAL</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Volume Pressure</div>
                        <div class="metric-value" id="shortVolumePressure">-</div>
                        <div class="metric-change neutral" id="shortPressureDir">BALANCED</div>
                    </div>
                </div>
                
                <canvas id="shortChart" class="turbo-chart" width="400" height="200"></canvas>
            </div>
            
            <!-- STRATEGY SIGNALS PANEL -->
            <div class="strategy-panel">
                <div class="turbo-title" style="background: linear-gradient(45deg, #f97316, #ea580c); color: white;">📊 STRATEGY SIGNALS</div>
                
                <div id="arbitrageAlert" class="arbitrage-alert" style="display: none;">
                    🚨 ARBITRAGE OPPORTUNITY DETECTED!
                </div>
                
                <div class="strategy-section">
                    <div class="strategy-title">🎯 Current Signals</div>
                    <div id="currentSignals">
                        <div class="signal-item signal-neutral">
                            <span>System:</span><span>Initializing...</span>
                        </div>
                    </div>
                </div>
                
                <div class="strategy-section">
                    <div class="strategy-title">💰 Arbitrage Monitor</div>
                    <div id="arbitrageOpportunities">
                        <div class="signal-item">
                            <span>Long vs Short:</span><span id="longShortArb">Monitoring...</span>
                        </div>
                        <div class="signal-item">
                            <span>Spread Efficiency:</span><span id="spreadEfficiency">Calculating...</span>
                        </div>
                    </div>
                </div>
                
                <div class="strategy-section">
                    <div class="strategy-title">📈 Momentum Strategies</div>
                    <div id="momentumStrategies">
                        <div class="signal-item">
                            <span>Breakout Signal:</span><span id="breakoutSignal">Waiting...</span>
                        </div>
                        <div class="signal-item">
                            <span>Mean Reversion:</span><span id="meanReversionSignal">Analyzing...</span>
                        </div>
                    </div>
                </div>
                
                <div class="strategy-section">
                    <div class="strategy-title">🧠 AI Confidence</div>
                    <div class="strategy-confidence">
                        <div class="confidence-fill" id="strategyConfidence" style="width: 0%"></div>
                    </div>
                    <div style="text-align: center; font-size: 0.8em; margin-top: 5px;">
                        <span id="confidenceText">Building confidence...</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- COMPARATIVE ANALYTICS -->
        <div class="comparison-grid">
            <div class="comparison-card">
                <div class="metric-title">Long/Short Ratio</div>
                <div class="metric-value" id="longShortRatio">-</div>
                <div class="metric-change neutral" id="ratioTrend">STABLE</div>
            </div>
            <div class="comparison-card">
                <div class="metric-title">Correlation</div>
                <div class="metric-value" id="correlation">-</div>
                <div class="metric-change neutral" id="correlationStrength">WEAK</div>
            </div>
            <div class="comparison-card">
                <div class="metric-title">Spread Divergence</div>
                <div class="metric-value" id="spreadDivergence">-</div>
                <div class="metric-change neutral" id="divergenceSignal">NORMAL</div>
            </div>
            <div class="comparison-card">
                <div class="metric-title">Volatility Ratio</div>
                <div class="metric-value" id="volatilityRatio">-</div>
                <div class="metric-change neutral" id="volRatioSignal">BALANCED</div>
            </div>
        </div>
        
        <!-- CHARTS SECTION -->
        <div class="charts-section">
            <div class="main-chart">
                <h3 style="margin: 0 0 10px 0; color: #60a5fa;">📊 Comparative Turbo Analysis</h3>
                <canvas id="mainChart" style="width: 100%; height: 280px;"></canvas>
            </div>
            <div class="mini-charts">
                <div class="mini-chart">
                    <h4 style="margin: 0 0 5px 0; font-size: 0.8em; color: #84cc16;">Spread Analysis</h4>
                    <canvas id="spreadChart" style="width: 100%; height: 70px;"></canvas>
                </div>
                <div class="mini-chart">
                    <h4 style="margin: 0 0 5px 0; font-size: 0.8em; color: #f59e0b;">Volatility</h4>
                    <canvas id="volatilityChart" style="width: 100%; height: 70px;"></canvas>
                </div>
                <div class="mini-chart">
                    <h4 style="margin: 0 0 5px 0; font-size: 0.8em; color: #a855f7;">Momentum</h4>
                    <canvas id="momentumChart" style="width: 100%; height: 70px;"></canvas>
                </div>
            </div>
        </div>
        
        <!-- DATA STREAM PANELS -->
        <div class="data-panels">
            <div class="data-panel">
                <h3 style="margin: 0 0 8px 0; color: #60a5fa; font-size: 0.9em;">📊 Live Turbo Data</h3>
                <div id="turboDataStream"></div>
            </div>
            <div class="data-panel">
                <h3 style="margin: 0 0 8px 0; color: #a855f7; font-size: 0.9em;">🧠 Strategy Events</h3>
                <div id="strategyEvents"></div>
            </div>
            <div class="data-panel">
                <h3 style="margin: 0 0 8px 0; color: #f59e0b; font-size: 0.9em;">💰 Trading Opportunities</h3>
                <div id="tradingOpportunities"></div>
            </div>
        </div>
    </div>

    <script>
        console.log('🚀 Ultimate Turbo Strategy Analytics loading...');
        
        // Global variables for turbo-specific analytics
        let turboData = {
            long: { 
                prices: [], bids: [], asks: [], spreads: [],
                sma5: [], sma20: [], ema10: [], rsi: [], momentum: [],
                volatility: [], volume: [], lastPrice: null, lastBid: null, lastAsk: null
            },
            short: { 
                prices: [], bids: [], asks: [], spreads: [],
                sma5: [], sma20: [], ema10: [], rsi: [], momentum: [],
                volatility: [], volume: [], lastPrice: null, lastBid: null, lastAsk: null
            }
        };
        
        let underlying = { prices: [], lastPrice: null };
        let baseline = { long: null, short: null, underlying: null };
        let isPaused = false;
        let updateCount = 0;
        let maxDataPoints = 500;
        
        // Strategy and signal tracking
        let signals = [];
        let arbitrageOpportunities = [];
        let strategyConfidence = 0;
        
        // Chart objects
        let charts = {};
        
        // Initialize all charts
        function initCharts() {
            console.log('📊 Initializing turbo strategy charts...');
            
            // Long turbo chart
            charts.long = new Chart(document.getElementById('longChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Price', data: [], borderColor: '#00ff88', backgroundColor: 'rgba(0, 255, 136, 0.1)', borderWidth: 2, fill: false },
                        { label: 'Bid', data: [], borderColor: '#ff4444', backgroundColor: 'rgba(255, 68, 68, 0.1)', borderWidth: 1, fill: false },
                        { label: 'Ask', data: [], borderColor: '#00cc66', backgroundColor: 'rgba(0, 204, 102, 0.1)', borderWidth: 1, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: 'white', font: { size: 9 } } } }, scales: { x: { ticks: { color: 'white', maxTicksLimit: 5 }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, y: { ticks: { color: 'white' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } } } }
            });
            
            // Short turbo chart
            charts.short = new Chart(document.getElementById('shortChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Price', data: [], borderColor: '#ff4444', backgroundColor: 'rgba(255, 68, 68, 0.1)', borderWidth: 2, fill: false },
                        { label: 'Bid', data: [], borderColor: '#cc0000', backgroundColor: 'rgba(204, 0, 0, 0.1)', borderWidth: 1, fill: false },
                        { label: 'Ask', data: [], borderColor: '#ff6666', backgroundColor: 'rgba(255, 102, 102, 0.1)', borderWidth: 1, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: 'white', font: { size: 9 } } } }, scales: { x: { ticks: { color: 'white', maxTicksLimit: 5 }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, y: { ticks: { color: 'white' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } } } }
            });
            
            // Main comparative chart
            charts.main = new Chart(document.getElementById('mainChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Long Turbo', data: [], borderColor: '#00ff88', borderWidth: 3, fill: false },
                        { label: 'Short Turbo', data: [], borderColor: '#ff4444', borderWidth: 3, fill: false },
                        { label: 'Underlying', data: [], borderColor: '#3b82f6', borderWidth: 2, fill: false, yAxisID: 'y1' }
                    ]
                },
                options: { 
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: 'white', font: { size: 10 } } } },
                    scales: { 
                        x: { ticks: { color: 'white', maxTicksLimit: 8 }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                        y: { type: 'linear', display: true, position: 'left', ticks: { color: 'white' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                        y1: { type: 'linear', display: true, position: 'right', ticks: { color: 'white' }, grid: { drawOnChartArea: false } }
                    }
                }
            });
            
            // Spread chart
            charts.spread = new Chart(document.getElementById('spreadChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Long Spread', data: [], borderColor: '#84cc16', borderWidth: 2, fill: false },
                        { label: 'Short Spread', data: [], borderColor: '#f59e0b', borderWidth: 2, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { ticks: { color: 'white', font: { size: 8 } } } } }
            });
            
            // Volatility chart
            charts.volatility = new Chart(document.getElementById('volatilityChart').getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Long Vol', data: [], backgroundColor: 'rgba(0, 255, 136, 0.6)', borderWidth: 0 },
                        { label: 'Short Vol', data: [], backgroundColor: 'rgba(255, 68, 68, 0.6)', borderWidth: 0 }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { ticks: { color: 'white', font: { size: 8 } } } } }
            });
            
            // Momentum chart
            charts.momentum = new Chart(document.getElementById('momentumChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Long Mom', data: [], borderColor: '#a855f7', borderWidth: 2, fill: false },
                        { label: 'Short Mom', data: [], borderColor: '#ec4899', borderWidth: 2, fill: false }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { ticks: { color: 'white', font: { size: 8 } } } } }
            });
            
            console.log('✅ All turbo strategy charts initialized');
        }
        
        // TURBO ANALYTICS FUNCTIONS
        
        function calculateTurboSMA(data, period) {
            if (data.length < period) return null;
            const slice = data.slice(-period);
            return slice.reduce((sum, val) => sum + val, 0) / period;
        }
        
        function calculateTurboEMA(data, period) {
            if (data.length < period) return null;
            const k = 2 / (period + 1);
            let ema = data[0];
            for (let i = 1; i < data.length; i++) {
                ema = data[i] * k + ema * (1 - k);
            }
            return ema;
        }
        
        function calculateTurboRSI(data, period = 14) {
            if (data.length < period + 1) return null;
            
            let gains = 0, losses = 0;
            for (let i = data.length - period; i < data.length; i++) {
                const change = data[i] - data[i - 1];
                if (change > 0) gains += change;
                else losses -= change;
            }
            
            const avgGain = gains / period;
            const avgLoss = losses / period;
            if (avgLoss === 0) return 100;
            const rs = avgGain / avgLoss;
            return 100 - (100 / (1 + rs));
        }
        
        function calculateTurboVolatility(data, period = 20) {
            if (data.length < period) return null;
            const slice = data.slice(-period);
            const mean = slice.reduce((sum, val) => sum + val, 0) / period;
            const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
            return Math.sqrt(variance);
        }
        
        function calculateTurboMomentum(data, period = 10) {
            if (data.length < period + 1) return null;
            const current = data[data.length - 1];
            const previous = data[data.length - 1 - period];
            return ((current - previous) / previous) * 100;
        }
        
        function calculateSpread(bid, ask) {
            if (!bid || !ask || bid === 0) return null;
            return ((ask - bid) / bid) * 100;
        }
        
        function calculateVolumePressure(bid, ask, lastBid, lastAsk) {
            if (!bid || !ask || !lastBid || !lastAsk) return 0;
            
            const bidChange = bid - lastBid;
            const askChange = ask - lastAsk;
            
            // Positive pressure = buying pressure, negative = selling pressure
            return (bidChange - askChange) * 100;
        }
        
        // UPDATE TURBO ANALYTICS
        function updateTurboAnalytics(type) {
            const data = turboData[type];
            if (data.prices.length < 2) return;
            
            // Calculate all indicators
            const sma5 = calculateTurboSMA(data.prices, 5);
            const sma20 = calculateTurboSMA(data.prices, 20);
            const ema10 = calculateTurboEMA(data.prices, 10);
            const rsi = calculateTurboRSI(data.prices);
            const volatility = calculateTurboVolatility(data.prices);
            const momentum = calculateTurboMomentum(data.prices);
            
            // Store calculated values
            if (sma5) data.sma5.push(sma5);
            if (sma20) data.sma20.push(sma20);
            if (ema10) data.ema10.push(ema10);
            if (rsi) data.rsi.push(rsi);
            if (volatility) data.volatility.push(volatility);
            if (momentum) data.momentum.push(momentum);
            
            // Update UI
            const prefix = type.charAt(0).toUpperCase() + type.slice(1);
            
            document.getElementById(type + 'SMA').textContent = sma5 ? sma5.toFixed(3) : '-';
            document.getElementById(type + 'RSI').textContent = rsi ? rsi.toFixed(1) : '-';
            document.getElementById(type + 'Volatility').textContent = volatility ? (volatility * 100).toFixed(3) + '%' : '-';
            document.getElementById(type + 'Momentum').textContent = momentum ? momentum.toFixed(2) + '%' : '-';
            
            // Update trend signals
            updateTrendSignals(type, sma5, sma20, rsi, momentum);
            
            // Update volatility bar
            if (volatility) {
                const volPercent = Math.min(volatility * 1000, 100);
                document.getElementById(type + 'VolBar').style.width = volPercent + '%';
            }
            
            // Calculate volume pressure
            if (data.bids.length > 1 && data.asks.length > 1) {
                const currentBid = data.bids[data.bids.length - 1];
                const currentAsk = data.asks[data.asks.length - 1];
                const prevBid = data.bids[data.bids.length - 2];
                const prevAsk = data.asks[data.asks.length - 2];
                
                const pressure = calculateVolumePressure(currentBid, currentAsk, prevBid, prevAsk);
                document.getElementById(type + 'VolumePressure').textContent = pressure.toFixed(2);
                
                const pressureEl = document.getElementById(type + 'PressureDir');
                if (pressure > 5) {
                    pressureEl.textContent = 'BUYING';
                    pressureEl.className = 'metric-change positive';
                } else if (pressure < -5) {
                    pressureEl.textContent = 'SELLING';
                    pressureEl.className = 'metric-change negative';
                } else {
                    pressureEl.textContent = 'BALANCED';
                    pressureEl.className = 'metric-change neutral';
                }
            }
            
            // Update charts
            updateTurboChart(type);
        }
        
        function updateTrendSignals(type, sma5, sma20, rsi, momentum) {
            // Trend signal based on SMA crossover
            const trendEl = document.getElementById(type + 'Trend');
            if (sma5 && sma20) {
                if (sma5 > sma20 * 1.001) { // 0.1% threshold
                    trendEl.textContent = 'BULLISH';
                    trendEl.className = 'metric-change positive';
                } else if (sma5 < sma20 * 0.999) {
                    trendEl.textContent = 'BEARISH';
                    trendEl.className = 'metric-change negative';
                } else {
                    trendEl.textContent = 'NEUTRAL';
                    trendEl.className = 'metric-change neutral';
                }
            }
            
            // RSI signal
            const rsiSignalEl = document.getElementById(type + 'RSISignal');
            if (rsi) {
                if (rsi > 70) {
                    rsiSignalEl.textContent = 'OVERBOUGHT';
                    rsiSignalEl.className = 'metric-change negative';
                } else if (rsi < 30) {
                    rsiSignalEl.textContent = 'OVERSOLD';
                    rsiSignalEl.className = 'metric-change positive';
                } else {
                    rsiSignalEl.textContent = 'NEUTRAL';
                    rsiSignalEl.className = 'metric-change neutral';
                }
            }
            
            // Momentum indicator
            const momentumIndEl = document.getElementById(type + 'MomentumInd');
            if (momentum) {
                if (momentum > 2) {
                    momentumIndEl.textContent = 'STRONG UP';
                    momentumIndEl.className = 'momentum-indicator momentum-strong-up';
                } else if (momentum > 0.5) {
                    momentumIndEl.textContent = 'WEAK UP';
                    momentumIndEl.className = 'momentum-indicator momentum-weak-up';
                } else if (momentum < -2) {
                    momentumIndEl.textContent = 'STRONG DOWN';
                    momentumIndEl.className = 'momentum-indicator momentum-strong-down';
                } else if (momentum < -0.5) {
                    momentumIndEl.textContent = 'WEAK DOWN';
                    momentumIndEl.className = 'momentum-indicator momentum-weak-down';
                } else {
                    momentumIndEl.textContent = 'FLAT';
                    momentumIndEl.className = 'momentum-indicator momentum-flat';
                }
            }
        }
        
        function updateTurboChart(type) {
            const chart = charts[type];
            const data = turboData[type];
            
            if (!chart || data.prices.length === 0) return;
            
            const recentData = Math.min(data.prices.length, 50);
            const labels = Array.from({length: recentData}, (_, i) => (i + 1).toString());
            
            chart.data.labels = labels;
            chart.data.datasets[0].data = data.prices.slice(-recentData);
            chart.data.datasets[1].data = data.bids.slice(-recentData);
            chart.data.datasets[2].data = data.asks.slice(-recentData);
            
            chart.update('none');
        }
        
        function updateMainChart() {
            if (!charts.main) return;
            
            const maxPoints = 30;
            const longPrices = turboData.long.prices.slice(-maxPoints);
            const shortPrices = turboData.short.prices.slice(-maxPoints);
            const underlyingPrices = underlying.prices.slice(-maxPoints);
            
            const labels = Array.from({length: Math.max(longPrices.length, shortPrices.length)}, (_, i) => (i + 1).toString());
            
            charts.main.data.labels = labels;
            charts.main.data.datasets[0].data = longPrices;
            charts.main.data.datasets[1].data = shortPrices;
            charts.main.data.datasets[2].data = underlyingPrices;
            
            charts.main.update('none');
        }
        
        function updateMiniCharts() {
            // Update spread chart
            if (charts.spread && turboData.long.spreads.length > 0) {
                const maxPoints = 20;
                const labels = Array.from({length: maxPoints}, (_, i) => (i + 1).toString());
                charts.spread.data.labels = labels;
                charts.spread.data.datasets[0].data = turboData.long.spreads.slice(-maxPoints);
                charts.spread.data.datasets[1].data = turboData.short.spreads.slice(-maxPoints);
                charts.spread.update('none');
            }
            
            // Update volatility chart
            if (charts.volatility && turboData.long.volatility.length > 0) {
                const maxPoints = 20;
                const labels = Array.from({length: maxPoints}, (_, i) => (i + 1).toString());
                charts.volatility.data.labels = labels;
                charts.volatility.data.datasets[0].data = turboData.long.volatility.slice(-maxPoints).map(v => v * 1000);
                charts.volatility.data.datasets[1].data = turboData.short.volatility.slice(-maxPoints).map(v => v * 1000);
                charts.volatility.update('none');
            }
            
            // Update momentum chart
            if (charts.momentum && turboData.long.momentum.length > 0) {
                const maxPoints = 20;
                const labels = Array.from({length: maxPoints}, (_, i) => (i + 1).toString());
                charts.momentum.data.labels = labels;
                charts.momentum.data.datasets[0].data = turboData.long.momentum.slice(-maxPoints);
                charts.momentum.data.datasets[1].data = turboData.short.momentum.slice(-maxPoints);
                charts.momentum.update('none');
            }
        }
        
        // COMPARATIVE ANALYTICS
        function updateComparativeAnalytics() {
            if (turboData.long.prices.length === 0 || turboData.short.prices.length === 0) return;
            
            const longPrice = turboData.long.lastPrice;
            const shortPrice = turboData.short.lastPrice;
            
            if (!longPrice || !shortPrice) return;
            
            // Long/Short ratio
            const ratio = longPrice / shortPrice;
            document.getElementById('longShortRatio').textContent = ratio.toFixed(4);
            
            // Correlation
            const correlation = calculateCorrelation(turboData.long.prices, turboData.short.prices);
            if (correlation !== null) {
                document.getElementById('correlation').textContent = correlation.toFixed(3);
                
                const corrStrengthEl = document.getElementById('correlationStrength');
                if (Math.abs(correlation) > 0.8) {
                    corrStrengthEl.textContent = 'VERY STRONG';
                    corrStrengthEl.className = 'metric-change positive';
                } else if (Math.abs(correlation) > 0.6) {
                    corrStrengthEl.textContent = 'STRONG';
                    corrStrengthEl.className = 'metric-change positive';
                } else if (Math.abs(correlation) > 0.3) {
                    corrStrengthEl.textContent = 'MODERATE';
                    corrStrengthEl.className = 'metric-change neutral';
                } else {
                    corrStrengthEl.textContent = 'WEAK';
                    corrStrengthEl.className = 'metric-change negative';
                }
            }
            
            // Spread divergence
            const longSpread = turboData.long.spreads.length > 0 ? turboData.long.spreads[turboData.long.spreads.length - 1] : 0;
            const shortSpread = turboData.short.spreads.length > 0 ? turboData.short.spreads[turboData.short.spreads.length - 1] : 0;
            
            if (longSpread && shortSpread) {
                const spreadDiff = Math.abs(longSpread - shortSpread);
                document.getElementById('spreadDivergence').textContent = spreadDiff.toFixed(3) + '%';
                
                const divergenceEl = document.getElementById('divergenceSignal');
                if (spreadDiff > 0.5) {
                    divergenceEl.textContent = 'HIGH DIVERGENCE';
                    divergenceEl.className = 'metric-change negative';
                } else if (spreadDiff > 0.2) {
                    divergenceEl.textContent = 'MODERATE';
                    divergenceEl.className = 'metric-change neutral';
                } else {
                    divergenceEl.textContent = 'LOW';
                    divergenceEl.className = 'metric-change positive';
                }
            }
            
            // Volatility ratio
            const longVol = turboData.long.volatility.length > 0 ? turboData.long.volatility[turboData.long.volatility.length - 1] : 0;
            const shortVol = turboData.short.volatility.length > 0 ? turboData.short.volatility[turboData.short.volatility.length - 1] : 0;
            
            if (longVol && shortVol) {
                const volRatio = longVol / shortVol;
                document.getElementById('volatilityRatio').textContent = volRatio.toFixed(3);
                
                const volRatioEl = document.getElementById('volRatioSignal');
                if (volRatio > 1.2 || volRatio < 0.8) {
                    volRatioEl.textContent = 'IMBALANCED';
                    volRatioEl.className = 'metric-change negative';
                } else {
                    volRatioEl.textContent = 'BALANCED';
                    volRatioEl.className = 'metric-change positive';
                }
            }
        }
        
        function calculateCorrelation(x, y) {
            const minLength = Math.min(x.length, y.length);
            if (minLength < 5) return null;
            
            const xSlice = x.slice(-minLength);
            const ySlice = y.slice(-minLength);
            
            const n = minLength;
            const sumX = xSlice.reduce((a, b) => a + b, 0);
            const sumY = ySlice.reduce((a, b) => a + b, 0);
            const sumXY = xSlice.reduce((sum, xi, i) => sum + xi * ySlice[i], 0);
            const sumX2 = xSlice.reduce((sum, xi) => sum + xi * xi, 0);
            const sumY2 = ySlice.reduce((sum, yi) => sum + yi * yi, 0);
            
            const numerator = n * sumXY - sumX * sumY;
            const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
            
            return denominator === 0 ? 0 : numerator / denominator;
        }
        
        // STRATEGY AND SIGNAL GENERATION
        function generateTradingSignals() {
            const newSignals = [];
            
            // RSI divergence signals
            if (turboData.long.rsi.length > 0 && turboData.short.rsi.length > 0) {
                const longRSI = turboData.long.rsi[turboData.long.rsi.length - 1];
                const shortRSI = turboData.short.rsi[turboData.short.rsi.length - 1];
                
                if (longRSI < 30 && shortRSI > 70) {
                    newSignals.push({
                        type: 'RSI_DIVERGENCE',
                        signal: 'LONG_OVERSOLD_SHORT_OVERBOUGHT',
                        strength: 'HIGH',
                        confidence: 85,
                        timestamp: Date.now()
                    });
                }
            }
            
            // Momentum breakout signals
            if (turboData.long.momentum.length > 0 && turboData.short.momentum.length > 0) {
                const longMom = turboData.long.momentum[turboData.long.momentum.length - 1];
                const shortMom = turboData.short.momentum[turboData.short.momentum.length - 1];
                
                if (longMom > 3 && shortMom < -3) {
                    newSignals.push({
                        type: 'MOMENTUM_DIVERGENCE',
                        signal: 'STRONG_LONG_MOMENTUM',
                        strength: 'HIGH',
                        confidence: 90,
                        timestamp: Date.now()
                    });
                }
            }
            
            // Spread arbitrage signals
            if (turboData.long.spreads.length > 0 && turboData.short.spreads.length > 0) {
                const longSpread = turboData.long.spreads[turboData.long.spreads.length - 1];
                const shortSpread = turboData.short.spreads[turboData.short.spreads.length - 1];
                
                if (Math.abs(longSpread - shortSpread) > 0.3) {
                    newSignals.push({
                        type: 'SPREAD_ARBITRAGE',
                        signal: longSpread > shortSpread ? 'LONG_EXPENSIVE' : 'SHORT_EXPENSIVE',
                        strength: 'MEDIUM',
                        confidence: 70,
                        timestamp: Date.now()
                    });
                }
            }
            
            // Update signals array
            signals = [...newSignals, ...signals].slice(0, 10);
            
            // Update UI
            updateSignalsDisplay();
            
            // Update strategy confidence
            updateStrategyConfidence();
        }
        
        function updateSignalsDisplay() {
            const container = document.getElementById('currentSignals');
            
            if (signals.length === 0) {
                container.innerHTML = '<div class="signal-item signal-neutral"><span>No signals</span><span>Monitoring...</span></div>';
                return;
            }
            
            container.innerHTML = signals.slice(0, 5).map(signal => {
                const signalClass = signal.confidence > 80 ? 'signal-bullish' : signal.confidence > 60 ? 'signal-neutral' : 'signal-bearish';
                return `
                    <div class="signal-item ${signalClass}">
                        <span>${signal.type}:</span>
                        <span>${signal.confidence}% - ${signal.signal}</span>
                    </div>
                `;
            }).join('');
        }
        
        function updateStrategyConfidence() {
            // Calculate overall confidence based on signal strength and consistency
            let totalConfidence = 0;
            let signalCount = 0;
            
            signals.forEach(signal => {
                if (Date.now() - signal.timestamp < 60000) { // Last minute only
                    totalConfidence += signal.confidence;
                    signalCount++;
                }
            });
            
            strategyConfidence = signalCount > 0 ? totalConfidence / signalCount : 0;
            
            // Update UI
            document.getElementById('strategyConfidence').style.width = strategyConfidence + '%';
            document.getElementById('confidenceText').textContent = strategyConfidence.toFixed(1) + '% Confidence';
        }
        
        function detectArbitrageOpportunities() {
            if (!turboData.long.lastPrice || !turboData.short.lastPrice) return;
            
            const longPrice = turboData.long.lastPrice;
            const shortPrice = turboData.short.lastPrice;
            const ratio = longPrice / shortPrice;
            
            // Check for unusual ratio (potential arbitrage)
            if (ratio > 1.05 || ratio < 0.95) {
                const opportunity = {
                    type: 'PRICE_ARBITRAGE',
                    longPrice: longPrice,
                    shortPrice: shortPrice,
                    ratio: ratio,
                    profitPotential: Math.abs(ratio - 1) * 100,
                    timestamp: Date.now()
                };
                
                arbitrageOpportunities.unshift(opportunity);
                arbitrageOpportunities = arbitrageOpportunities.slice(0, 5);
                
                // Show alert
                document.getElementById('arbitrageAlert').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('arbitrageAlert').style.display = 'none';
                }, 5000);
                
                addTradingOpportunity(`🚨 ARBITRAGE: ${ratio > 1 ? 'LONG expensive' : 'SHORT expensive'} - ${opportunity.profitPotential.toFixed(2)}% potential`);
            }
            
            // Update arbitrage display
            document.getElementById('longShortArb').textContent = `Ratio: ${ratio.toFixed(4)} ${ratio > 1.02 ? '(LONG EXPENSIVE)' : ratio < 0.98 ? '(SHORT EXPENSIVE)' : '(NORMAL)'}`;
        }
        
        // MAIN UPDATE FUNCTIONS
        window.updateLongTurbo = function(price) {
            console.log('🟢 LONG turbo price:', price);
            const numPrice = parseFloat(price);
            
            turboData.long.prices.push(numPrice);
            turboData.long.lastPrice = numPrice;
            
            if (turboData.long.prices.length > maxDataPoints) {
                turboData.long.prices.shift();
            }
            
            if (!baseline.long) baseline.long = numPrice;
            
            document.getElementById('longPrice').textContent = price;
            updateChangeDisplay('longChange', calculateRelative(numPrice, baseline.long));
            
            updateTurboAnalytics('long');
            updateComparativeAnalytics();
            updateMainChart();
            
            if (!isPaused) {
                generateTradingSignals();
                detectArbitrageOpportunities();
            }
            
            addTurboDataStream('🟢 LONG: ' + price);
            updateCount++;
            document.getElementById('statusText').textContent = '🟢 Live (' + updateCount + ')';
        };
        
        window.updateLongTurboBidAsk = function(bid, ask) {
            console.log('🟢 LONG bid/ask:', bid, ask);
            
            if (bid !== null && bid !== undefined) {
                turboData.long.bids.push(parseFloat(bid));
                turboData.long.lastBid = parseFloat(bid);
                document.getElementById('longBid').textContent = bid;
                
                if (turboData.long.bids.length > maxDataPoints) {
                    turboData.long.bids.shift();
                }
            }
            
            if (ask !== null && ask !== undefined) {
                turboData.long.asks.push(parseFloat(ask));
                turboData.long.lastAsk = parseFloat(ask);
                document.getElementById('longAsk').textContent = ask;
                
                if (turboData.long.asks.length > maxDataPoints) {
                    turboData.long.asks.shift();
                }
            }
            
            if (bid && ask) {
                const spread = calculateSpread(bid, ask);
                if (spread) {
                    turboData.long.spreads.push(spread);
                    document.getElementById('longSpread').textContent = spread.toFixed(3) + '%';
                    
                    if (turboData.long.spreads.length > maxDataPoints) {
                        turboData.long.spreads.shift();
                    }
                }
            }
            
            updateMiniCharts();
        };
        
        window.updateShortTurbo = function(price) {
            console.log('🔴 SHORT turbo price:', price);
            const numPrice = parseFloat(price);
            
            turboData.short.prices.push(numPrice);
            turboData.short.lastPrice = numPrice;
            
            if (turboData.short.prices.length > maxDataPoints) {
                turboData.short.prices.shift();
            }
            
            if (!baseline.short) baseline.short = numPrice;
            
            document.getElementById('shortPrice').textContent = price;
            updateChangeDisplay('shortChange', calculateRelative(numPrice, baseline.short));
            
            updateTurboAnalytics('short');
            updateComparativeAnalytics();
            updateMainChart();
            
            if (!isPaused) {
                generateTradingSignals();
                detectArbitrageOpportunities();
            }
            
            addTurboDataStream('🔴 SHORT: ' + price);
            updateCount++;
            document.getElementById('statusText').textContent = '🟢 Live (' + updateCount + ')';
        };
        
        window.updateShortTurboBidAsk = function(bid, ask) {
            console.log('🔴 SHORT bid/ask:', bid, ask);
            
            if (bid !== null && bid !== undefined) {
                turboData.short.bids.push(parseFloat(bid));
                turboData.short.lastBid = parseFloat(bid);
                document.getElementById('shortBid').textContent = bid;
                
                if (turboData.short.bids.length > maxDataPoints) {
                    turboData.short.bids.shift();
                }
            }
            
            if (ask !== null && ask !== undefined) {
                turboData.short.asks.push(parseFloat(ask));
                turboData.short.lastAsk = parseFloat(ask);
                document.getElementById('shortAsk').textContent = ask;
                
                if (turboData.short.asks.length > maxDataPoints) {
                    turboData.short.asks.shift();
                }
            }
            
            if (bid && ask) {
                const spread = calculateSpread(bid, ask);
                if (spread) {
                    turboData.short.spreads.push(spread);
                    document.getElementById('shortSpread').textContent = spread.toFixed(3) + '%';
                    
                    if (turboData.short.spreads.length > maxDataPoints) {
                        turboData.short.spreads.shift();
                    }
                }
            }
            
            updateMiniCharts();
        };
        
        window.updateUnderlying = function(price) {
            console.log('📈 Underlying price:', price);
            const numPrice = parseFloat(price);
            
            underlying.prices.push(numPrice);
            underlying.lastPrice = numPrice;
            
            if (underlying.prices.length > maxDataPoints) {
                underlying.prices.shift();
            }
            
            if (!baseline.underlying) baseline.underlying = numPrice;
            
            updateMainChart();
            
            // Auto-save data every 10 updates
            if (updateCount % 10 === 0) {
                saveStrategicData();
            }
        };
        
        // UTILITY FUNCTIONS
        function calculateRelative(current, base) {
            if (!base || !current) return 0;
            return ((current - base) / base) * 100;
        }
        
        function updateChangeDisplay(elementId, value) {
            const element = document.getElementById(elementId);
            if (!element) return;
            
            element.textContent = (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
            element.className = 'metric-change ' + (value > 0.1 ? 'positive' : value < -0.1 ? 'negative' : 'neutral');
        }
        
        function addTurboDataStream(message) {
            const stream = document.getElementById('turboDataStream');
            const item = document.createElement('div');
            item.className = 'data-item';
            item.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            stream.insertBefore(item, stream.firstChild);
            
            while (stream.children.length > 15) {
                stream.removeChild(stream.lastChild);
            }
        }
        
        function addStrategyEvent(message) {
            const stream = document.getElementById('strategyEvents');
            const item = document.createElement('div');
            item.className = 'data-item';
            item.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            stream.insertBefore(item, stream.firstChild);
            
            while (stream.children.length > 15) {
                stream.removeChild(stream.lastChild);
            }
        }
        
        function addTradingOpportunity(message) {
            const stream = document.getElementById('tradingOpportunities');
            const item = document.createElement('div');
            item.className = 'data-item';
            item.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            stream.insertBefore(item, stream.firstChild);
            
            while (stream.children.length > 15) {
                stream.removeChild(stream.lastChild);
            }
        }
        
        function saveStrategicData() {
            const strategicData = {
                sessionInfo: {
                    start: new Date().toISOString(),
                    updateCount: updateCount,
                    duration: (Date.now() - Date.parse(new Date())) / 1000
                },
                turboAnalytics: {
                    long: {
                        prices: turboData.long.prices,
                        bids: turboData.long.bids,
                        asks: turboData.long.asks,
                        spreads: turboData.long.spreads,
                        sma5: turboData.long.sma5,
                        sma20: turboData.long.sma20,
                        rsi: turboData.long.rsi,
                        volatility: turboData.long.volatility,
                        momentum: turboData.long.momentum
                    },
                    short: {
                        prices: turboData.short.prices,
                        bids: turboData.short.bids,
                        asks: turboData.short.asks,
                        spreads: turboData.short.spreads,
                        sma5: turboData.short.sma5,
                        sma20: turboData.short.sma20,
                        rsi: turboData.short.rsi,
                        volatility: turboData.short.volatility,
                        momentum: turboData.short.momentum
                    }
                },
                underlying: underlying.prices,
                signals: signals,
                arbitrageOpportunities: arbitrageOpportunities,
                strategyConfidence: strategyConfidence
            };
            
            try {
                window.parent.postMessage({
                    type: 'saveStrategicData',
                    data: strategicData
                }, '*');
            } catch (e) {
                console.log('📁 Strategic data ready (', turboData.long.prices.length + turboData.short.prices.length, 'turbo records)');
            }
        }
        
        // CONTROL FUNCTIONS
        function resetBaseline() {
            if (turboData.long.lastPrice && turboData.short.lastPrice && underlying.lastPrice) {
                baseline = { 
                    long: turboData.long.lastPrice, 
                    short: turboData.short.lastPrice, 
                    underlying: underlying.lastPrice 
                };
                addStrategyEvent('🔄 Baseline reset to current values');
            }
        }
        
        function togglePause() {
            isPaused = !isPaused;
            const btn = document.getElementById('pauseBtn');
            btn.textContent = isPaused ? '▶️ Resume' : '⏸️ Pause';
            addStrategyEvent(isPaused ? '⏸️ Analysis paused' : '▶️ Analysis resumed');
        }
        
        function runDeepAnalysis() {
            addStrategyEvent('🧠 Running deep turbo analysis...');
            
            setTimeout(() => {
                generateTradingSignals();
                detectArbitrageOpportunities();
                updateComparativeAnalytics();
                
                addStrategyEvent('🧠 Deep analysis complete - ' + signals.length + ' signals generated');
            }, 1000);
        }
        
        function generateSignals() {
            addStrategyEvent('📈 Generating trading signals...');
            generateTradingSignals();
            addStrategyEvent('📈 Signal generation complete');
        }
        
        function detectArbitrage() {
            addStrategyEvent('💰 Scanning for arbitrage opportunities...');
            detectArbitrageOpportunities();
            addStrategyEvent('💰 Arbitrage scan complete');
        }
        
        function exportStrategicData() {
            saveStrategicData();
            
            const strategicData = {
                sessionInfo: {
                    start: new Date().toISOString(),
                    updateCount: updateCount
                },
                turboAnalytics: {
                    long: turboData.long,
                    short: turboData.short
                },
                underlying: underlying.prices,
                signals: signals,
                arbitrageOpportunities: arbitrageOpportunities,
                strategyConfidence: strategyConfidence
            };
            
            const blob = new Blob([JSON.stringify(strategicData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `turbo-strategy-analytics-${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            addStrategyEvent('💾 Strategic data exported (' + (turboData.long.prices.length + turboData.short.prices.length) + ' turbo records)');
        }
        
        // INITIALIZE
        window.addEventListener('load', () => {
            console.log('🚀 Ultimate Turbo Strategy Analytics loading...');
            setTimeout(() => {
                initCharts();
                addTurboDataStream('🚀 Ultimate turbo analytics initialized');
                addStrategyEvent('🧠 Strategy engine ready for signals');
                addTradingOpportunity('💰 Arbitrage detection active');
                console.log('✅ Ultimate turbo analytics ready for strategy development!');
            }, 1500);
        });

        console.log('✅ Ultimate Turbo Strategy Analytics script loaded');
    </script>
</body>
</html>'''
        
        # Load enhanced dashboard
        try:
            print("📊 Loading ULTIMATE turbo strategy dashboard...")
            html_b64 = base64.b64encode(dashboard_html.encode('utf-8')).decode('utf-8')
            data_url = f"data:text/html;base64,{html_b64}"
            
            await dashboard_page.goto(data_url)
            await dashboard_page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(4)
            
            # Verify everything is working
            functions_ready = await dashboard_page.evaluate("""
                () => typeof window.updateLongTurbo === 'function' && 
                      typeof window.updateShortTurbo === 'function' && 
                      typeof window.updateUnderlying === 'function' &&
                      typeof Chart !== 'undefined'
            """)
            
            print(f"📊 Ultimate dashboard functions ready: {functions_ready}")
            
            if functions_ready:
                print("✅ ULTIMATE TURBO ANALYTICS READY!")
                print("🎯 EVERYTHING you need for winning strategies!")
            else:
                print("❌ Dashboard not fully ready - check console")
                
        except Exception as e:
            print(f"❌ Error loading ultimate dashboard: {e}")
        
        # Add dashboard to pages
        pages.append(dashboard_page)
        
        # Create trading pages with enhanced turbo data capture
        for i, url in enumerate(TURBO_URLS):
            page = await ctx.new_page()
            pages.append(page)
            
            page_name = f"TAB-{i+1}"
            
            # Enhanced console handler for turbo data
            def create_console_handler(name):
                def handle_console(msg):
                    text = msg.text
                    print(f"[{name}] {text}")
                    
                    if "📈 UNDERLYING | Price:" in text:
                        try:
                            price_part = text.split("Price: ")[1].split(" |")[0]
                            price = float(price_part)
                            asyncio.create_task(update_dashboard_underlying(price))
                        except Exception as e:
                            print(f"[{name}] ❌ Failed to parse underlying: {e}")
                return handle_console
            
            page.on("console", create_console_handler(page_name))
            page.on("response", lambda response, name=page_name: asyncio.create_task(handle_sse_response(response, name)))

            # Enhanced JavaScript injection for maximum turbo data capture
            await page.add_init_script(f"""
                window.PAGE_ID = '{page_name}';
                window.__ws = [];
                window.__wsReady = [];
                window.__detectedTurboId = null;
                window.__turboName = 'TURBO-{i+1}';
                
                // ULTIMATE WebSocket monitoring for TURBO data
                const RealWS = window.WebSocket;
                window.WebSocket = function(url, proto) {{
                    const ws = new RealWS(url, proto);
                    const wsIndex = window.__ws.length;
                    window.__ws.push(ws);
                    window.__wsReady.push(false);
                    
                    ws.addEventListener('open', () => {{
                        console.log(`🔗 TURBO WebSocket ${{wsIndex}} OPENED:`, url);
                        window.__wsReady[wsIndex] = true;
                    }});
                    
                    // ENHANCED message monitoring for TURBO analytics
                    ws.addEventListener('message', (event) => {{
                        try {{
                            const data = JSON.parse(event.data);
                            
                            // Log ALL turbo data for maximum analytics
                            if (data.type === 'price') {{
                                console.log(`📊 TURBO PRICE DATA:`, JSON.stringify(data, null, 2));
                            }} else if (data.type === 'depth') {{
                                console.log(`📊 TURBO DEPTH DATA:`, JSON.stringify(data, null, 2));
                            }} else if (data.type === 'trade') {{
                                console.log(`📊 TURBO TRADE DATA:`, JSON.stringify(data, null, 2));
                            }}
                        }} catch (e) {{
                            // Not JSON, might be other data
                        }}
                    }});
                    
                    const originalSend = ws.send.bind(ws);
                    ws.send = function(data) {{
                        try {{
                            const msg = JSON.parse(data);
                            if (msg.cmd === 'subscribe' && msg.args && msg.args.id) {{
                                console.log('🎯 TURBO SUBSCRIPTION ID:', msg.args.id);
                                if (!window.__detectedTurboId) {{
                                    window.__detectedTurboId = msg.args.id;
                                    console.log(`✅ TURBO ID for ${{window.__turboName}}:`, msg.args.id);
                                }}
                            }}
                        }} catch (e) {{}}
                        return originalSend(data);
                    }};
                    
                    return ws;
                }};
                
                // Enhanced SSE monitoring
                const originalFetch = window.fetch;
                window.fetch = function(...args) {{
                    const url = args[0];
                    if (typeof url === 'string' && url.includes('streaming/sse')) {{
                        console.log('🚀 TURBO SSE FETCH:', url);
                        
                        return originalFetch(...args).then(response => {{
                            const clonedResponse = response.clone();
                            
                            if (clonedResponse.body) {{
                                const reader = clonedResponse.body.getReader();
                                const decoder = new TextDecoder();
                                let buffer = '';
                                
                                function processChunk() {{
                                    return reader.read().then(({{done, value}}) => {{
                                        if (done) return;
                                        
                                        const chunk = decoder.decode(value, {{stream: true}});
                                        buffer += chunk;
                                        
                                        let eventEnd = buffer.indexOf('\\n\\n');
                                        while (eventEnd !== -1) {{
                                            const eventText = buffer.substring(0, eventEnd);
                                            buffer = buffer.substring(eventEnd + 2);
                                            
                                            const lines = eventText.split('\\n');
                                            let eventType = null;
                                            let eventData = null;
                                            
                                            for (const line of lines) {{
                                                if (line.startsWith('event:')) {{
                                                    eventType = line.substring(6).trim();
                                                }} else if (line.startsWith('data:')) {{
                                                    eventData = line.substring(5).trim();
                                                }}
                                            }}
                                            
                                            if (eventType === 'price' && eventData) {{
                                                try {{
                                                    const data = JSON.parse(eventData);
                                                    if (data.development !== undefined && data.absoluteDevelopment !== undefined) {{
                                                        console.log(`📈 UNDERLYING | Price: ${{data.last}} | Change: ${{data.development?.toFixed(2)}}% (${{data.absoluteDevelopment?.toFixed(2)}})`);
                                                    }}
                                                }} catch (e) {{}}
                                            }}
                                            
                                            eventEnd = buffer.indexOf('\\n\\n');
                                        }}
                                        
                                        return processChunk();
                                    }});
                                }}
                                
                                processChunk().catch(e => console.log('❌ SSE error:', e));
                            }}
                            
                            return response;
                        }});
                    }}
                    
                    return originalFetch(...args);
                }};
            """)

            # Enhanced WebSocket frame handler for ultimate turbo analytics
            def create_ws_handler(page_name, tab_index):
                def on_ws(ws):
                    print(f"[{page_name}] 🔗 TURBO WS connection: {ws.url}")
                    ws.on("framereceived", lambda payload: handle_ultimate_turbo_frame(payload, page_name, tab_index))
                return on_ws

            page.on("websocket", create_ws_handler(page_name, i))

        print("🚀 Opening ULTIMATE turbo analytics tabs...")
        
        # Open all trading pages
        for i, (page, url) in enumerate(zip(pages[1:], TURBO_URLS), 1):
            await page.goto(url)
            print(f"✅ TURBO Tab {i} opened")
            await asyncio.sleep(2)
        
        await asyncio.sleep(25)  # Wait for login

        # Enhanced subscription setup for maximum data capture
        print("🔍 Setting up ULTIMATE turbo data subscriptions...")
        
        for i, page in enumerate(pages[1:]):
            page_name = f"TAB-{i+1}"
            try:
                # Auto-detect turbo ID from URL
                turbo_id = None
                current_url = page.url
                if "unlimited-turbos" in current_url:
                    try:
                        url_parts = current_url.split('/')
                        for part in url_parts:
                            if part.isdigit() or (part.split('-')[0].isdigit()):
                                turbo_id = part.split('-')[0]
                                print(f"[{page_name}] 🎯 TURBO ID detected: {turbo_id}")
                                break
                    except:
                        pass

                # Wait for WebSockets to be ready
                for attempt in range(15):
                    try:
                        ready_ws_count = await page.evaluate("() => window.__wsReady?.filter(ready => ready).length || 0")
                        if ready_ws_count > 0:
                            break
                        await asyncio.sleep(1)
                    except:
                        await asyncio.sleep(1)

                # Enhanced subscription with ALL data types
                try:
                    detected_id = await page.evaluate("() => window.__detectedTurboId")
                    if detected_id:
                        turbo_id = detected_id

                    if turbo_id:
                        subscribe_result = await page.evaluate(f"""
                        () => {{
                            let subscribed = 0;
                            for (let i = 0; i < window.__ws.length; i++) {{
                                const ws = window.__ws[i];
                                const ready = window.__wsReady[i];
                                
                                if (ready && ws.readyState === WebSocket.OPEN) {{
                                    try {{
                                        // Subscribe to ALL turbo data types for maximum analytics
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'price',id:{turbo_id}}}}}));
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'depth',id:{turbo_id}}}}}));
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'trade',id:{turbo_id}}}}}));
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'orderbook',id:{turbo_id}}}}}));
                                        subscribed++;
                                        console.log(`✅ ULTIMATE turbo subscription to {turbo_id} on WS ${{i}}`);
                                    }} catch (err) {{
                                        console.log(`❌ Subscription failed on WS ${{i}}:`, err);
                                    }}
                                }}
                            }}
                            return subscribed;
                        }}
                        """)
                        print(f"[{page_name}] ✅ ULTIMATE subscriptions: {subscribe_result}")
                        
                        # Store turbo data for analytics
                        turbo_type = "long" if i == 0 else "short"
                        trading_data["turbos"][turbo_type]["id"] = turbo_id
                        trading_data["turbos"][turbo_type]["tab"] = page_name
                        
                except Exception as e:
                    print(f"[{page_name}] ❌ ULTIMATE subscription error: {e}")
                    
            except Exception as e:
                print(f"[{page_name}] ❌ ULTIMATE setup error: {e}")

        print("\n🎯 ULTIMATE TURBO STRATEGY ANALYTICS ACTIVE:")
        print("⭐ COMPLETE TURBO ANALYTICS - RSI, SMA, EMA, Volatility, Momentum")  
        print("📊 REAL-TIME BID/ASK SPREAD ANALYSIS")
        print("🧠 ADVANCED SIGNAL GENERATION & ARBITRAGE DETECTION")
        print("💰 AUTOMATED STRATEGY CONFIDENCE SCORING")
        print("📈 COMPARATIVE LONG vs SHORT ANALYTICS")
        print("💾 COMPREHENSIVE JSON DATA EXPORT FOR ALGO DEVELOPMENT")
        print("🚀 EVERYTHING YOU NEED FOR WINNING TURBO STRATEGIES!")
        print("\nPress ENTER to stop...\n")
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        # Save final strategic data
        await save_ultimate_trading_data()
        await browser.close()

def handle_ultimate_turbo_frame(payload: str, page_name: str, tab_index: int):
    """ULTIMATE turbo data parsing with complete analytics capture"""
    try:
        msg = json.loads(payload)
    except json.JSONDecodeError:
        return

    t = msg.get("type")
    d = msg.get("data", {})
    if not isinstance(d, dict):
        return

    emojis = ["🟢", "🔴"]
    emoji = emojis[tab_index % len(emojis)]
    turbo_type = "long" if tab_index == 0 else "short"

    # Store ALL data for comprehensive analytics
    timestamp = datetime.now().isoformat()

    if t == "price":
        price = d.get("last") or d.get("bid") or d.get("ask")
        if price is not None:
            print(f"[{page_name}] {emoji} TURBO PRICE: {price}")
            
            # Store comprehensive price data
            trading_data["turbos"][turbo_type]["prices"].append({
                "timestamp": timestamp,
                "price": price,
                "volume": d.get("volume", 0),
                "turnover": d.get("turnover", 0)
            })
            
            # Send to dashboard
            asyncio.create_task(update_dashboard_turbo(tab_index, price))
            
    elif t == "depth":
        bid = d.get("bid") or d.get("bid1") or d.get("bidPrice")
        ask = d.get("ask") or d.get("ask1") or d.get("askPrice")
        bid_size = d.get("bidSize") or d.get("bid1Size", 0)
        ask_size = d.get("askSize") or d.get("ask1Size", 0)
        
        if bid is not None or ask is not None:
            print(f"[{page_name}] {emoji} TURBO DEPTH | Bid: {bid} ({bid_size}) | Ask: {ask} ({ask_size})")
            
            # Store comprehensive bid/ask data
            if bid is not None:
                trading_data["turbos"][turbo_type]["bids"].append({
                    "timestamp": timestamp,
                    "bid": bid,
                    "size": bid_size,
                    "depth": d.get("bidDepth", 1)
                })
            if ask is not None:
                trading_data["turbos"][turbo_type]["asks"].append({
                    "timestamp": timestamp,
                    "ask": ask,
                    "size": ask_size,
                    "depth": d.get("askDepth", 1)
                })
                
            # Calculate and store spread data
            if bid and ask:
                spread = ((ask - bid) / bid) * 100
                trading_data["turbos"][turbo_type]["spreads"].append({
                    "timestamp": timestamp,
                    "spread": spread,
                    "bid": bid,
                    "ask": ask,
                    "bid_size": bid_size,
                    "ask_size": ask_size
                })
            
            # Send to dashboard with enhanced bid/ask update
            asyncio.create_task(update_dashboard_turbo_bidask(tab_index, bid, ask))
            
    elif t == "trade":
        # Store trade data for volume analysis
        trade_price = d.get("price")
        trade_volume = d.get("volume", 0)
        trade_side = d.get("side", "unknown")
        
        if trade_price:
            print(f"[{page_name}] {emoji} TURBO TRADE: {trade_price} vol:{trade_volume} side:{trade_side}")
            
            # Store trade data for analytics
            if "trades" not in trading_data["turbos"][turbo_type]:
                trading_data["turbos"][turbo_type]["trades"] = []
            
            trading_data["turbos"][turbo_type]["trades"].append({
                "timestamp": timestamp,
                "price": trade_price,
                "volume": trade_volume,
                "side": trade_side
            })

async def update_dashboard_turbo(tab_index, price):
    """Enhanced dashboard turbo update for ultimate analytics"""
    try:
        if len(pages) >= 1:
            dashboard_page = pages[0]
            
            if "about:blank" in dashboard_page.url:
                return
                
            if tab_index == 0:  # TAB-1 = LONG
                await dashboard_page.evaluate(f"window.updateLongTurbo({price})")
                print(f"📊 ✅ ULTIMATE LONG update: {price}")
            elif tab_index == 1:  # TAB-2 = SHORT
                await dashboard_page.evaluate(f"window.updateShortTurbo({price})")
                print(f"📊 ✅ ULTIMATE SHORT update: {price}")
    except Exception as e:
        print(f"❌ Dashboard turbo update error: {e}")

async def update_dashboard_turbo_bidask(tab_index, bid, ask):
    """Enhanced dashboard bid/ask update for ultimate analytics"""
    try:
        if len(pages) >= 1:
            dashboard_page = pages[0]
            
            if "about:blank" in dashboard_page.url:
                return
            
            bid_val = bid if bid is not None else "null"
            ask_val = ask if ask is not None else "null"
                
            if tab_index == 0:  # TAB-1 = LONG
                await dashboard_page.evaluate(f"window.updateLongTurboBidAsk({bid_val}, {ask_val})")
                print(f"📊 ✅ ULTIMATE LONG bid/ask: {bid}/{ask}")
            elif tab_index == 1:  # TAB-2 = SHORT
                await dashboard_page.evaluate(f"window.updateShortTurboBidAsk({bid_val}, {ask_val})")
                print(f"📊 ✅ ULTIMATE SHORT bid/ask: {bid}/{ask}")
    except Exception as e:
        print(f"❌ Dashboard bid/ask update error: {e}")

async def update_dashboard_underlying(price):
    """Enhanced dashboard underlying update for ultimate analytics"""
    try:
        if len(pages) >= 1:
            dashboard_page = pages[0]
            
            if "about:blank" in dashboard_page.url:
                return
            
            # Store in comprehensive data structure
            trading_data["underlying"].append({
                "timestamp": datetime.now().isoformat(),
                "price": price
            })
                
            await dashboard_page.evaluate(f"window.updateUnderlying({price})")
            print(f"📊 ✅ ULTIMATE underlying: {price}")
    except Exception as e:
        print(f"❌ Dashboard underlying update error: {e}")

async def handle_sse_response(response, page_name):
    """Enhanced SSE response handling for ultimate analytics"""
    try:
        if "streaming/sse" in response.url and response.status == 200:
            print(f"[{page_name}] 🎯 ULTIMATE SSE Response detected")
    except Exception as e:
        pass

async def save_ultimate_trading_data():
    """Save comprehensive turbo trading data with all analytics"""
    try:
        # Calculate final session statistics
        session_end = datetime.now()
        session_start = datetime.fromisoformat(trading_data["session_start"])
        session_duration = (session_end - session_start).total_seconds() / 60
        
        # Enhanced statistics calculation
        long_updates = len(trading_data["turbos"]["long"]["prices"])
        short_updates = len(trading_data["turbos"]["short"]["prices"])
        underlying_updates = len(trading_data["underlying"])
        total_spreads = len(trading_data["turbos"]["long"]["spreads"]) + len(trading_data["turbos"]["short"]["spreads"])
        
        # Calculate advanced analytics
        analytics_summary = {
            "session_metrics": {
                "duration_minutes": session_duration,
                "total_turbo_updates": long_updates + short_updates,
                "total_underlying_updates": underlying_updates,
                "total_spread_calculations": total_spreads,
                "update_frequency": (long_updates + short_updates) / max(session_duration, 1),
                "data_quality_score": min(100, (long_updates + short_updates + underlying_updates) / 10)
            },
            "turbo_performance": {
                "long_turbo": {
                    "total_updates": long_updates,
                    "price_range": calculate_price_range(trading_data["turbos"]["long"]["prices"]),
                    "avg_spread": calculate_avg_spread(trading_data["turbos"]["long"]["spreads"]),
                    "volatility_score": calculate_volatility_score(trading_data["turbos"]["long"]["prices"])
                },
                "short_turbo": {
                    "total_updates": short_updates,
                    "price_range": calculate_price_range(trading_data["turbos"]["short"]["prices"]),
                    "avg_spread": calculate_avg_spread(trading_data["turbos"]["short"]["spreads"]),
                    "volatility_score": calculate_volatility_score(trading_data["turbos"]["short"]["prices"])
                }
            },
            "strategy_opportunities": {
                "arbitrage_events": len([s for s in trading_data.get("strategy_signals", []) if "arbitrage" in s.get("type", "").lower()]),
                "high_volatility_periods": count_high_volatility_periods(),
                "correlation_strength": calculate_final_correlation(),
                "trading_recommendations": generate_final_recommendations()
            }
        }
        
        # Comprehensive data export
        ultimate_data = {
            "session_info": {
                "start": trading_data["session_start"],
                "end": session_end.isoformat(),
                "duration_minutes": session_duration,
                "total_data_points": long_updates + short_updates + underlying_updates
            },
            "turbo_analytics": {
                "long": trading_data["turbos"]["long"],
                "short": trading_data["turbos"]["short"]
            },
            "underlying_data": trading_data["underlying"],
            "strategy_signals": trading_data.get("strategy_signals", []),
            "arbitrage_opportunities": trading_data.get("arbitrage_opportunities", []),
            "volatility_events": trading_data.get("volatility_events", []),
            "patterns": trading_data.get("patterns", []),
            "analytics_summary": analytics_summary,
            "export_metadata": {
                "export_time": datetime.now().isoformat(),
                "data_version": "ultimate_v1.0",
                "recommended_analysis": [
                    "Correlation analysis between long/short turbos",
                    "Spread arbitrage opportunity detection", 
                    "Volatility-based momentum strategies",
                    "Mean reversion pattern analysis",
                    "Optimal entry/exit timing based on RSI divergence"
                ]
            }
        }
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ultimate_turbo_strategy_data_{timestamp}.json"
        
        # Save comprehensive data
        with open(filename, 'w') as f:
            json.dump(ultimate_data, f, indent=2)
        
        print(f"\n💾 ✅ ULTIMATE TURBO DATA SAVED: {filename}")
        print(f"📊 Session Summary:")
        print(f"   🕒 Duration: {session_duration:.1f} minutes")
        print(f"   📈 Long Turbo Updates: {long_updates}")
        print(f"   📉 Short Turbo Updates: {short_updates}")
        print(f"   🎯 Underlying Updates: {underlying_updates}")
        print(f"   💰 Total Spread Data: {total_spreads}")
        print(f"   ⚡ Update Frequency: {analytics_summary['session_metrics']['update_frequency']:.2f}/min")
        print(f"   🏆 Data Quality Score: {analytics_summary['session_metrics']['data_quality_score']:.1f}%")
        print(f"\n🚀 PERFECT FOR ALGORITHM DEVELOPMENT!")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error saving ultimate trading data: {e}")
        return None

def calculate_price_range(price_data):
    """Calculate price range from price data"""
    if not price_data:
        return {"min": 0, "max": 0, "range": 0}
    
    prices = [item["price"] if isinstance(item, dict) else item for item in price_data]
    if not prices:
        return {"min": 0, "max": 0, "range": 0}
    
    min_price = min(prices)
    max_price = max(prices)
    return {
        "min": min_price,
        "max": max_price,
        "range": max_price - min_price,
        "range_percent": ((max_price - min_price) / min_price * 100) if min_price > 0 else 0
    }

def calculate_avg_spread(spread_data):
    """Calculate average spread from spread data"""
    if not spread_data:
        return 0
    
    spreads = [item["spread"] if isinstance(item, dict) else item for item in spread_data]
    if not spreads:
        return 0
    
    return {
        "average": sum(spreads) / len(spreads),
        "min": min(spreads),
        "max": max(spreads),
        "count": len(spreads)
    }

def calculate_volatility_score(price_data):
    """Calculate volatility score from price data"""
    if len(price_data) < 2:
        return 0
    
    prices = [item["price"] if isinstance(item, dict) else item for item in price_data]
    if len(prices) < 2:
        return 0
    
    # Calculate price changes
    changes = []
    for i in range(1, len(prices)):
        change = abs(prices[i] - prices[i-1]) / prices[i-1] * 100
        changes.append(change)
    
    if not changes:
        return 0
    
    return {
        "avg_change_percent": sum(changes) / len(changes),
        "max_change_percent": max(changes),
        "volatility_events": len([c for c in changes if c > 1.0]),  # Changes > 1%
        "stability_score": 100 - min(100, sum(changes) / len(changes) * 10)
    }

def count_high_volatility_periods():
    """Count periods of high volatility across all turbos"""
    count = 0
    
    # Check long turbo volatility
    long_prices = trading_data["turbos"]["long"]["prices"]
    if len(long_prices) > 1:
        prices = [item["price"] if isinstance(item, dict) else item for item in long_prices]
        for i in range(1, len(prices)):
            if abs(prices[i] - prices[i-1]) / prices[i-1] > 0.02:  # 2% change
                count += 1
    
    # Check short turbo volatility  
    short_prices = trading_data["turbos"]["short"]["prices"]
    if len(short_prices) > 1:
        prices = [item["price"] if isinstance(item, dict) else item for item in short_prices]
        for i in range(1, len(prices)):
            if abs(prices[i] - prices[i-1]) / prices[i-1] > 0.02:  # 2% change
                count += 1
    
    return count

def calculate_final_correlation():
    """Calculate final correlation between long and short turbos"""
    long_prices = [item["price"] if isinstance(item, dict) else item for item in trading_data["turbos"]["long"]["prices"]]
    short_prices = [item["price"] if isinstance(item, dict) else item for item in trading_data["turbos"]["short"]["prices"]]
    
    if len(long_prices) < 5 or len(short_prices) < 5:
        return {"correlation": 0, "strength": "insufficient_data", "sample_size": 0}
    
    # Align data by taking minimum length
    min_length = min(len(long_prices), len(short_prices))
    long_aligned = long_prices[-min_length:]
    short_aligned = short_prices[-min_length:]
    
    if min_length < 5:
        return {"correlation": 0, "strength": "insufficient_data", "sample_size": min_length}
    
    # Calculate Pearson correlation
    try:
        n = min_length
        sum_x = sum(long_aligned)
        sum_y = sum(short_aligned)
        sum_xy = sum(x * y for x, y in zip(long_aligned, short_aligned))
        sum_x2 = sum(x * x for x in long_aligned)
        sum_y2 = sum(y * y for y in short_aligned)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            correlation = 0
        else:
            correlation = numerator / denominator
        
        # Determine strength
        abs_corr = abs(correlation)
        if abs_corr > 0.8:
            strength = "very_strong"
        elif abs_corr > 0.6:
            strength = "strong" 
        elif abs_corr > 0.4:
            strength = "moderate"
        elif abs_corr > 0.2:
            strength = "weak"
        else:
            strength = "very_weak"
        
        return {
            "correlation": correlation,
            "strength": strength,
            "sample_size": n,
            "interpretation": f"{'Positive' if correlation > 0 else 'Negative'} {strength} correlation"
        }
        
    except Exception as e:
        return {"correlation": 0, "strength": "calculation_error", "error": str(e), "sample_size": min_length}

def generate_final_recommendations():
    """Generate final trading strategy recommendations based on collected data"""
    recommendations = []
    
    # Analyze correlation
    correlation_data = calculate_final_correlation()
    corr = correlation_data.get("correlation", 0)
    
    if abs(corr) > 0.7:
        if corr > 0:
            recommendations.append({
                "strategy": "Correlation Trading",
                "type": "POSITIVE_CORRELATION",
                "confidence": "HIGH", 
                "description": "Strong positive correlation detected. Consider momentum strategies where both turbos move together.",
                "action": "Monitor for synchronized breakouts and trade in same direction"
            })
        else:
            recommendations.append({
                "strategy": "Divergence Trading", 
                "type": "NEGATIVE_CORRELATION",
                "confidence": "HIGH",
                "description": "Strong negative correlation detected. Perfect for hedge strategies.",
                "action": "Use opposite positions to hedge risk or capture mean reversion"
            })
    
    # Analyze spreads
    long_spread_data = calculate_avg_spread(trading_data["turbos"]["long"]["spreads"])
    short_spread_data = calculate_avg_spread(trading_data["turbos"]["short"]["spreads"])
    
    if isinstance(long_spread_data, dict) and isinstance(short_spread_data, dict):
        avg_long_spread = long_spread_data.get("average", 0)
        avg_short_spread = short_spread_data.get("average", 0)
        
        if abs(avg_long_spread - avg_short_spread) > 0.1:
            recommendations.append({
                "strategy": "Spread Arbitrage",
                "type": "SPREAD_DIFFERENTIAL", 
                "confidence": "MEDIUM",
                "description": f"Spread difference detected: Long {avg_long_spread:.3f}% vs Short {avg_short_spread:.3f}%",
                "action": f"Favor {'short' if avg_long_spread > avg_short_spread else 'long'} turbo for better execution costs"
            })
    
    # Analyze volatility
    long_vol = calculate_volatility_score(trading_data["turbos"]["long"]["prices"])
    short_vol = calculate_volatility_score(trading_data["turbos"]["short"]["prices"])
    
    if isinstance(long_vol, dict) and isinstance(short_vol, dict):
        long_vol_score = long_vol.get("avg_change_percent", 0)
        short_vol_score = short_vol.get("avg_change_percent", 0)
        
        if long_vol_score > 0.5 or short_vol_score > 0.5:
            recommendations.append({
                "strategy": "Volatility Trading",
                "type": "HIGH_VOLATILITY",
                "confidence": "MEDIUM",
                "description": f"High volatility detected: Long {long_vol_score:.2f}%, Short {short_vol_score:.2f}%",
                "action": "Consider volatility-based strategies like straddles or momentum breakouts"
            })
    
    # Data quality recommendation
    total_updates = len(trading_data["turbos"]["long"]["prices"]) + len(trading_data["turbos"]["short"]["prices"])
    if total_updates > 100:
        recommendations.append({
            "strategy": "Algorithm Development",
            "type": "DATA_QUALITY",
            "confidence": "HIGH",
            "description": f"Excellent data quality with {total_updates} updates collected",
            "action": "Sufficient data for backtesting and algorithm development"
        })
    elif total_updates > 50:
        recommendations.append({
            "strategy": "Extended Monitoring", 
            "type": "DATA_QUALITY",
            "confidence": "MEDIUM",
            "description": f"Good data quality with {total_updates} updates, but could benefit from longer monitoring",
            "action": "Collect more data for robust algorithm development"
        })
    else:
        recommendations.append({
            "strategy": "Longer Data Collection",
            "type": "DATA_QUALITY", 
            "confidence": "LOW",
            "description": f"Limited data with only {total_updates} updates collected",
            "action": "Extend monitoring period for better strategy development"
        })
    
    if not recommendations:
        recommendations.append({
            "strategy": "Continue Monitoring",
            "type": "INSUFFICIENT_DATA",
            "confidence": "LOW", 
            "description": "Insufficient data for specific recommendations",
            "action": "Continue collecting data and monitor for patterns"
        })
    
    return recommendations

if __name__ == "__main__":
    print("🚀 ULTIMATE TURBO STRATEGY ANALYTICS")
    print("=" * 50)
    print("This system provides EVERYTHING you need for turbo algorithm development:")
    print("📊 Real-time price, bid/ask, and spread analytics")
    print("🧠 Advanced technical indicators (RSI, SMA, EMA, momentum)")
    print("💰 Arbitrage opportunity detection")
    print("📈 Correlation and volatility analysis") 
    print("🎯 Automated signal generation")
    print("💾 Comprehensive JSON data export")
    print("=" * 50)
    print()
    
    asyncio.run(main())