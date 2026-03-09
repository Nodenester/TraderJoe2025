import asyncio
import json
from playwright.async_api import async_playwright

# ─── CONFIG ──────────────────────────────────────────────────────────────────
TURBO_URLS = [
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # First tab
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # Second tab
]

# Global variable to store pages for dashboard updates
pages = []
# ────────────────────────────────────────────────────────────────────────────

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        
        # Initialize variables
        global pages
        pages = []
        turbo_names = ["TURBO-1", "TURBO-2", "DASHBOARD"]
        
        print("🚀 Creating Trading Dashboard + Tabs...")
        
        # Create dashboard page first
        dashboard_page = await ctx.new_page()
        
        # Dashboard HTML content (simplified version without Chart.js for now)
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Turbo Trading Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .dashboard { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .controls { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .btn { padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px; }
        .btn-reset { background: linear-gradient(45deg, #ff6b6b, #ff8e53); color: white; }
        .btn-reset:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3); }
        .btn-toggle { background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; }
        .btn-toggle:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(78, 205, 196, 0.3); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
        .stat-title { font-size: 0.9em; opacity: 0.8; margin-bottom: 5px; }
        .stat-value { font-size: 1.8em; font-weight: bold; margin-bottom: 5px; }
        .stat-change { font-size: 0.9em; padding: 5px 10px; border-radius: 20px; display: inline-block; }
        .positive { background: rgba(76, 175, 80, 0.3); color: #4CAF50; }
        .negative { background: rgba(244, 67, 54, 0.3); color: #F44336; }
        .neutral { background: rgba(158, 158, 158, 0.3); color: #9E9E9E; }
        .connection-status { position: fixed; top: 20px; right: 20px; padding: 10px 20px; border-radius: 25px; font-weight: bold; backdrop-filter: blur(10px); }
        .connected { background: rgba(76, 175, 80, 0.3); color: #4CAF50; border: 1px solid #4CAF50; }
        .data-flow { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.2); }
        .data-item { margin: 10px 0; padding: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 Real-Time Turbo Trading Dashboard</h1>
            <p>Monitor Long & Short positions with relative performance tracking</p>
        </div>
        <div class="connection-status connected" id="connectionStatus">
            <span id="statusText">🟢 Live Data</span>
        </div>
        <div class="controls">
            <button class="btn btn-reset" onclick="resetBaseline()">🔄 Reset Baseline</button>
            <button class="btn btn-toggle" onclick="togglePause()" id="pauseBtn">⏸️ Pause</button>
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">🟢 LONG Turbo</div>
                <div class="stat-value" id="longPrice">-</div>
                <div class="stat-change neutral" id="longChange">+0.00%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">🔴 SHORT Turbo</div>
                <div class="stat-value" id="shortPrice">-</div>
                <div class="stat-change neutral" id="shortChange">+0.00%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">📈 Underlying</div>
                <div class="stat-value" id="underlyingPrice">-</div>
                <div class="stat-change neutral" id="underlyingChange">+0.00%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">⚖️ Long vs Short</div>
                <div class="stat-value" id="ratio">-</div>
                <div class="stat-change neutral" id="ratioChange">+0.00%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">🎯 Performance</div>
                <div class="stat-value" id="totalReturn">-</div>
                <div class="stat-change neutral" id="returnChange">Strategy</div>
            </div>
        </div>
        <div class="data-flow">
            <h3>📊 Live Data Stream</h3>
            <div id="dataStream"></div>
        </div>
    </div>

    <script>
        console.log('🚀 Dashboard script starting...');
        
        let baseline = { long: null, short: null, underlying: null };
        let currentData = { long: null, short: null, underlying: null };
        let isPaused = false;
        let updateCount = 0;

        function resetBaseline() {
            if (currentData.long && currentData.short && currentData.underlying) {
                baseline = { ...currentData };
                updateStats();
                console.log('📊 Baseline reset to current values');
                addDataStreamItem('🔄 Baseline reset');
            }
        }

        function togglePause() {
            isPaused = !isPaused;
            const btn = document.getElementById('pauseBtn');
            btn.textContent = isPaused ? '▶️ Resume' : '⏸️ Pause';
            addDataStreamItem(isPaused ? '⏸️ Paused' : '▶️ Resumed');
        }

        function calculateRelative(current, base) {
            if (!base || !current) return 0;
            return ((current - base) / base) * 100;
        }

        function updateStats() {
            if (!baseline.long || !currentData.long) return;

            const longRel = calculateRelative(currentData.long, baseline.long);
            const shortRel = calculateRelative(currentData.short, baseline.short);
            const underlyingRel = calculateRelative(currentData.underlying, baseline.underlying);
            const ratio = currentData.long / currentData.short;
            const baseRatio = baseline.long / baseline.short;
            const ratioChange = ((ratio - baseRatio) / baseRatio) * 100;

            document.getElementById('ratio').textContent = ratio.toFixed(4);
            updateChangeDisplay('longChange', longRel);
            updateChangeDisplay('shortChange', shortRel);
            updateChangeDisplay('underlyingChange', underlyingRel);
            updateChangeDisplay('ratioChange', ratioChange);

            const performance = (longRel + shortRel) / 2;
            document.getElementById('totalReturn').textContent = performance.toFixed(2) + '%';
            updateChangeDisplay('returnChange', performance, false);
        }

        function updateChangeDisplay(elementId, value, isPercent = true) {
            const element = document.getElementById(elementId);
            const suffix = isPercent && elementId !== 'returnChange' ? '%' : '';
            element.textContent = (value >= 0 ? '+' : '') + value.toFixed(2) + suffix;
            element.className = 'stat-change ' + (value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral');
        }

        function addDataStreamItem(message) {
            const stream = document.getElementById('dataStream');
            const item = document.createElement('div');
            item.className = 'data-item';
            item.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            stream.appendChild(item);
            
            // Keep only last 10 items
            while (stream.children.length > 10) {
                stream.removeChild(stream.firstChild);
            }
        }

        window.updateLongTurbo = function(price) {
            console.log('🟢 Dashboard received LONG turbo price:', price);
            currentData.long = parseFloat(price);
            if (!baseline.long) baseline.long = currentData.long;
            
            document.getElementById('longPrice').textContent = price;
            addDataStreamItem('🟢 LONG: ' + price);
            
            if (!isPaused) updateStats();
            updateCount++;
            document.getElementById('statusText').textContent = '🟢 Live Data (' + updateCount + ')';
        };

        window.updateShortTurbo = function(price) {
            console.log('🔴 Dashboard received SHORT turbo price:', price);
            currentData.short = parseFloat(price);
            if (!baseline.short) baseline.short = currentData.short;
            
            document.getElementById('shortPrice').textContent = price;
            addDataStreamItem('🔴 SHORT: ' + price);
            
            if (!isPaused) updateStats();
            updateCount++;
            document.getElementById('statusText').textContent = '🟢 Live Data (' + updateCount + ')';
        };

        window.updateUnderlying = function(price) {
            console.log('📈 Dashboard received underlying price:', price);
            currentData.underlying = parseFloat(price);
            if (!baseline.underlying) baseline.underlying = currentData.underlying;
            
            document.getElementById('underlyingPrice').textContent = price;
            addDataStreamItem('📈 UNDERLYING: ' + price);
            
            if (!isPaused) updateStats();
            updateCount++;
            document.getElementById('statusText').textContent = '🟢 Live Data (' + updateCount + ')';
        };

        console.log('✅ Dashboard functions defined successfully');
        addDataStreamItem('🚀 Dashboard initialized');
    </script>
</body>
</html>'''
        
        # Load dashboard using data URL navigation (more reliable than set_content)
        try:
            print("📊 Loading dashboard via data URL...")
            import base64
            html_b64 = base64.b64encode(dashboard_html.encode('utf-8')).decode('utf-8')
            data_url = f"data:text/html;base64,{html_b64}"
            
            await dashboard_page.goto(data_url)
            await dashboard_page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(5)  # Give extra time for Chart.js to load
            
            # Check if it loaded properly
            page_title = await dashboard_page.title()
            page_url = dashboard_page.url
            print(f"📊 Dashboard loaded! Title: {page_title}")
            print(f"📊 Dashboard URL: {page_url[:50]}...")
            
            # Verify the functions exist with retry and debugging
            functions_exist = None
            for attempt in range(10):  # Try for 10 seconds
                try:
                    # Check for JavaScript errors first
                    js_errors = await dashboard_page.evaluate("""
                        () => {
                            const errors = [];
                            // Check if Chart.js loaded
                            errors.push('Chart.js loaded: ' + (typeof window.Chart !== 'undefined'));
                            
                            // Check for script errors
                            const scripts = document.querySelectorAll('script');
                            errors.push('Script tags found: ' + scripts.length);
                            
                            // Check if our functions are defined
                            errors.push('updateLongTurbo defined: ' + (typeof window.updateLongTurbo === 'function'));
                            
                            return errors;
                        }
                    """)
                    print(f"📊 🔧 Attempt {attempt+1} Debug info: {js_errors}")
                    
                    functions_exist = await dashboard_page.evaluate("""
                        () => {
                            return {
                                updateLongTurbo: typeof window.updateLongTurbo === 'function',
                                updateShortTurbo: typeof window.updateShortTurbo === 'function',
                                updateUnderlying: typeof window.updateUnderlying === 'function',
                                Chart: typeof window.Chart !== 'undefined'
                            };
                        }
                    """)
                    
                    if functions_exist['updateLongTurbo'] and functions_exist['updateShortTurbo'] and functions_exist['updateUnderlying']:
                        print(f"📊 ✅ Dashboard functions loaded successfully: {functions_exist}")
                        break
                    else:
                        if attempt == 0:  # On first attempt, try to manually define functions
                            print("📊 🔧 Attempting to manually define functions...")
                            await dashboard_page.evaluate("""
                                () => {
                                    console.log('🔧 Manually defining dashboard functions...');
                                    
                                    let baseline = { long: null, short: null, underlying: null };
                                    let currentData = { long: null, short: null, underlying: null };
                                    let isPaused = false;
                                    let showPercent = false;
                                    
                                    window.updateLongTurbo = function(price) {
                                        console.log('🟢 Dashboard received LONG turbo price:', price);
                                        currentData.long = parseFloat(price);
                                        if (!baseline.long) baseline.long = currentData.long;
                                        document.getElementById('longPrice').textContent = price;
                                    };

                                    window.updateShortTurbo = function(price) {
                                        console.log('🔴 Dashboard received SHORT turbo price:', price);
                                        currentData.short = parseFloat(price);
                                        if (!baseline.short) baseline.short = currentData.short;
                                        document.getElementById('shortPrice').textContent = price;
                                    };

                                    window.updateUnderlying = function(price) {
                                        console.log('📈 Dashboard received underlying price:', price);
                                        currentData.underlying = parseFloat(price);
                                        if (!baseline.underlying) baseline.underlying = currentData.underlying;
                                        document.getElementById('underlyingPrice').textContent = price;
                                    };
                                    
                                    console.log('✅ Dashboard functions manually defined');
                                }
                            """)
                        
                        print(f"📊 ⏳ Waiting for functions... attempt {attempt+1}: {functions_exist}")
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    print(f"📊 ❌ Error checking functions attempt {attempt+1}: {e}")
                    await asyncio.sleep(1)
            
            if not functions_exist or not functions_exist.get('updateLongTurbo'):
                print("❌ CRITICAL: Dashboard functions failed to load after 10 attempts!")
                print("❌ Dashboard will not work. Check browser console for errors.")
                # Still continue but warn user
            else:
                print("✅ Dashboard is ready to receive data!")
            
        except Exception as e:
            print(f"❌ Error loading dashboard: {e}")
            print("❌ Continuing without dashboard...")
        
        # Add dashboard to pages list
        pages.append(dashboard_page)
        
        print("⏳ Dashboard setup complete, now creating trading tabs...")
        await asyncio.sleep(2)  # Small pause before creating trading pages
        
        # Create trading pages/tabs
        for i, url in enumerate(TURBO_URLS):
            page = await ctx.new_page()
            pages.append(page)
            
            # Add page identifier for logging and dashboard integration
            page_name = f"TAB-{i+1}"
            
            # Forward console.log with tab identification and dashboard updates
            def create_console_handler(name):
                def handle_console(msg):
                    text = msg.text
                    print(f"[{name}] {text}")
                    
                    # Parse underlying data and send to dashboard
                    if "📈 UNDERLYING | Price:" in text:
                        try:
                            # Extract price from: "📈 UNDERLYING | Price: 3428.98 | Change: 0.96% (32.56)"
                            price_part = text.split("Price: ")[1].split(" |")[0]
                            price = float(price_part)
                            print(f"[{name}] 🎯 Parsed underlying price: {price}")
                            asyncio.create_task(update_dashboard_underlying(price))
                        except Exception as e:
                            print(f"[{name}] ❌ Failed to parse underlying price: {e}")
                return handle_console
            
            page.on("console", create_console_handler(page_name))

            # Monitor SSE responses for this specific page
            page.on("response", lambda response, name=page_name: asyncio.create_task(handle_sse_response(response, name)))

            # Inject JavaScript with page identification
            await page.add_init_script(f"""
                window.PAGE_ID = '{page_name}';
                
                // Override fetch to intercept SSE streams properly
                const originalFetch = window.fetch;
                window.fetch = function(...args) {{
                    const url = args[0];
                    if (typeof url === 'string' && url.includes('streaming/sse')) {{
                        console.log('🚀 Intercepting SSE fetch:', url);
                        
                        return originalFetch(...args).then(response => {{
                            console.log('📡 SSE fetch response received');
                            
                            // Clone the response so we can read it
                            const clonedResponse = response.clone();
                            
                            // Read the streaming response
                            if (clonedResponse.body) {{
                                const reader = clonedResponse.body.getReader();
                                const decoder = new TextDecoder();
                                let buffer = '';
                                
                                function processChunk() {{
                                    return reader.read().then(({{done, value}}) => {{
                                        if (done) {{
                                            console.log('🏁 SSE stream finished');
                                            return;
                                        }}
                                        
                                        // Decode the chunk and add to buffer
                                        const chunk = decoder.decode(value, {{stream: true}});
                                        buffer += chunk;
                                        
                                        // Process complete SSE events (separated by double newlines)
                                        let eventEnd = buffer.indexOf('\\n\\n');
                                        while (eventEnd !== -1) {{
                                            const eventText = buffer.substring(0, eventEnd);
                                            buffer = buffer.substring(eventEnd + 2);
                                            
                                            // Parse SSE event
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
                                            
                                            // Handle the event - only show relevant underlying data
                                            if (eventType === 'price' && eventData) {{
                                                try {{
                                                    const data = JSON.parse(eventData);
                                                    // Only show if we have BOTH percentage and absolute change
                                                    if (data.development !== undefined && data.absoluteDevelopment !== undefined) {{
                                                        console.log(`📈 UNDERLYING | Price: ${{data.last}} | Change: ${{data.development?.toFixed(2)}}% (${{data.absoluteDevelopment?.toFixed(2)}})`);
                                                    }}
                                                }} catch (e) {{
                                                    // Skip malformed data
                                                }}
                                            }} else if (eventType === 'heartbeat') {{
                                                console.log('💓 UNDERLYING heartbeat');
                                            }}
                                            
                                            eventEnd = buffer.indexOf('\\n\\n');
                                        }}
                                        
                                        // Continue reading
                                        return processChunk();
                                    }});
                                }}
                                
                                // Start processing
                                processChunk().catch(e => console.log('❌ SSE stream error:', e));
                            }}
                            
                            // Return the original response
                            return response;
                        }});
                    }}
                    
                    return originalFetch(...args);
                }};
                
                // Also try to intercept EventSource if used
                const RealEventSource = window.EventSource;
                window.EventSource = function(url, options) {{
                    console.log('🔗 EventSource created:', url);
                    const es = new RealEventSource(url, options);
                    
                    es.addEventListener('price', function(event) {{
                        try {{
                            const data = JSON.parse(event.data);
                            // Only show if we have BOTH percentage and absolute change
                            if (data.development !== undefined && data.absoluteDevelopment !== undefined) {{
                                console.log(`📈 UNDERLYING ES | Price: ${{data.last}} | Change: ${{data.development?.toFixed(2)}}% (${{data.absoluteDevelopment?.toFixed(2)}})`);
                            }}
                        }} catch (e) {{
                            // Skip malformed data
                        }}
                    }});
                    
                    es.addEventListener('heartbeat', function(event) {{
                        console.log('💓 UNDERLYING ES heartbeat');
                    }});
                    
                    es.addEventListener('message', function(event) {{
                        console.log('📨 UNDERLYING ES message:', event.data);
                    }});
                    
                    return es;
                }};
            """)

            # WebSocket setup for each page
            await page.add_init_script(f"""
                window.__ws = [];
                window.__wsReady = [];
                window.__detectedTurboId = null;
                window.__turboName = 'TURBO-{i+1}';
                
                const RealWS = window.WebSocket;
                window.WebSocket = function(url, proto) {{
                    const ws = new RealWS(url, proto);
                    const wsIndex = window.__ws.length;
                    window.__ws.push(ws);
                    window.__wsReady.push(false);
                    
                    ws.addEventListener('open', () => {{
                        console.log(`🔗 WebSocket ${{wsIndex}} OPENED:`, url);
                        window.__wsReady[wsIndex] = true;
                    }});
                    
                    // Intercept outgoing messages to detect turbo ID
                    const originalSend = ws.send.bind(ws);
                    ws.send = function(data) {{
                        try {{
                            const msg = JSON.parse(data);
                            if (msg.cmd === 'subscribe' && msg.args && msg.args.id) {{
                                console.log('🎯 Detected subscription ID:', msg.args.id);
                                if (!window.__detectedTurboId) {{
                                    window.__detectedTurboId = msg.args.id;
                                    console.log(`✅ Auto-detected Turbo ID for ${{window.__turboName}}:`, msg.args.id);
                                }}
                            }}
                        }} catch (e) {{}}
                        return originalSend(data);
                    }};
                    
                    return ws;
                }};
            """)

            # Setup WebSocket monitoring for each page
            def create_ws_handler(page_name, tab_index):
                def on_ws(ws):
                    print(f"[{page_name}] 🔗 WS connection detected: {ws.url}")
                    ws.on("framereceived", lambda payload: handle_turbo_frame(payload, page_name, tab_index))
                return on_ws

            page.on("websocket", create_ws_handler(page_name, i))

        print("🚀 Opening multiple Nordnet tabs + Dashboard...")
        print("📝 Log in on the first tab, then navigate each tab to different turbos")
        print("💡 Suggestion: Use TAB-1 for LONG and TAB-2 for SHORT positions!")
        print("📊 Dashboard will show real-time comparison charts!")
        
        # Open all pages (skip dashboard as it's already loaded)
        for i, (page, url) in enumerate(zip(pages[1:], TURBO_URLS), 1):
            await page.goto(url)
            print(f"✅ Tab {i} opened")
            await asyncio.sleep(2)  # Small delay between tabs
        
        # Wait for user to log in and navigate
        await asyncio.sleep(25)

        # Setup subscriptions for all trading pages (skip dashboard which is pages[0])
        print("🔍 Setting up WebSocket subscriptions for all tabs...")
        
        for i, page in enumerate(pages[1:]):  # Skip dashboard page at index 0
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
                                print(f"[{page_name}] 🎯 Auto-detected Turbo ID from URL: {turbo_id}")
                                break
                    except:
                        turbo_id = None

                # Wait for WebSockets and attempt subscriptions
                for attempt in range(10):
                    try:
                        ready_ws_count = await page.evaluate("() => window.__wsReady?.filter(ready => ready).length || 0")
                        if ready_ws_count > 0:
                            break
                        await asyncio.sleep(1)
                    except:
                        await asyncio.sleep(1)

                # Get detected turbo ID and subscribe
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
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'price',id:{turbo_id}}}}}));
                                        ws.send(JSON.stringify({{cmd:'subscribe',args:{{t:'depth',id:{turbo_id}}}}}));
                                        subscribed++;
                                        console.log(`✅ Subscribed to turbo {turbo_id} on WebSocket ${{i}}`);
                                    }} catch (err) {{
                                        console.log(`❌ Subscription failed on WS ${{i}}:`, err);
                                    }}
                                }}
                            }}
                            return subscribed;
                        }}
                        """)
                        print(f"[{page_name}] ✅ Turbo subscriptions: {subscribe_result}")
                        
                        # Update turbo name with ID
                        turbo_names[i] = f"TURBO-{turbo_id}"
                        
                except Exception as e:
                    print(f"[{page_name}] ❌ Subscription error: {e}")
                    
            except Exception as e:
                print(f"[{page_name}] ❌ Setup error: {e}")

        print("\n🎯 MULTI-TURBO MONITOR + DASHBOARD ACTIVE:")
        print("⭐ TURBO data (WebSocket - multiple turbos)")  
        print("📈 UNDERLYING data (SSE - auto-detected)")
        print("📊 REAL-TIME DASHBOARD with relative performance!")
        print("💰 Perfect for monitoring LONG + SHORT positions!")
        print("\nPress ENTER to stop...\n")
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        await browser.close()

async def handle_sse_response(response, page_name):
    """Handle SSE response with page identification"""
    try:
        if "streaming/sse" in response.url and response.status == 200:
            print(f"[{page_name}] 🎯 SSE Response detected")
    except Exception as e:
        pass

def handle_turbo_frame(payload: str, page_name: str, tab_index: int):
    """Parse and print turbo price/depth from WS messages with page identification."""
    try:
        msg = json.loads(payload)
    except json.JSONDecodeError:
        return

    t = msg.get("type")
    d = msg.get("data", {})
    if not isinstance(d, dict):
        return

    # Use different emojis for different tabs
    emojis = ["🟢", "🔴", "🟡", "🟣"]
    emoji = emojis[tab_index % len(emojis)]

    if t == "price":
        price = d.get("last") or d.get("bid") or d.get("ask")
        if price is not None:
            print(f"[{page_name}] {emoji} TURBO Price: {price}")
            
            # Send to dashboard
            asyncio.create_task(update_dashboard_turbo(tab_index, price))
    elif t == "depth":
        bid = d.get("bid") or d.get("bid1")
        ask = d.get("ask") or d.get("ask1")
        if bid is not None or ask is not None:
            print(f"[{page_name}] {emoji} TURBO Depth | Bid: {bid} | Ask: {ask}")

async def update_dashboard_turbo(tab_index, price):
    """Update dashboard with turbo price data"""
    try:
        if len(pages) >= 1:  # Ensure we have dashboard page
            dashboard_page = pages[0]  # Dashboard is first page (index 0)
            
            # Check if page is properly loaded
            page_url = dashboard_page.url
            if "about:blank" in page_url:
                print("❌ Dashboard page is still blank! Skipping update.")
                return
                
            if tab_index == 0:  # TAB-1 = LONG
                await dashboard_page.evaluate(f"window.updateLongTurbo({price})")
                print(f"📊 ✅ Updated LONG turbo: {price}")
            elif tab_index == 1:  # TAB-2 = SHORT
                await dashboard_page.evaluate(f"window.updateShortTurbo({price})")
                print(f"📊 ✅ Updated SHORT turbo: {price}")
    except Exception as e:
        print(f"❌ Dashboard turbo update error: {e}")

async def update_dashboard_underlying(price):
    """Update dashboard with underlying price data"""
    try:
        if len(pages) >= 1:  # Ensure we have dashboard page
            dashboard_page = pages[0]  # Dashboard is first page (index 0)
            
            # Check if page is properly loaded
            page_url = dashboard_page.url
            if "about:blank" in page_url:
                print("❌ Dashboard page is still blank! Skipping update.")
                return
                
            await dashboard_page.evaluate(f"window.updateUnderlying({price})")
            print(f"📊 ✅ Updated underlying: {price}")
    except Exception as e:
        print(f"❌ Dashboard underlying update error: {e}")

if __name__ == "__main__":
    asyncio.run(main())