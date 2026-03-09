import asyncio
import json
from playwright.async_api import async_playwright

# ─── CONFIG ──────────────────────────────────────────────────────────────────
# Add URLs for the turbos you want to monitor
TURBO_URLS = [
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # First tab - you navigate manually
    "https://www.nordnet.se/loggain?redirect_to=%2Fmarknaden%2Funlimited-turbos",  # Second tab - you navigate manually
]
# ────────────────────────────────────────────────────────────────────────────

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        
        pages = []
        turbo_names = ["TURBO-1", "TURBO-2"]  # Will be updated with actual names
        
        # Create multiple pages/tabs
        for i, url in enumerate(TURBO_URLS):
            page = await ctx.new_page()
            pages.append(page)
            
            # Add page identifier for logging
            page_name = f"TAB-{i+1}"
            
            # Forward console.log with tab identification
            page.on("console", lambda msg, name=page_name: print(f"[{name}] {msg.text}"))

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

        print("🚀 Opening multiple Nordnet tabs...")
        print("📝 Log in on the first tab, then navigate each tab to different turbos")
        print("💡 Suggestion: Use one for LONG and one for SHORT positions!")
        
        # Open all pages
        for i, (page, url) in enumerate(zip(pages, TURBO_URLS)):
            await page.goto(url)
            print(f"✅ Tab {i+1} opened")
            await asyncio.sleep(2)  # Small delay between tabs
        
        # Wait for user to log in and navigate
        await asyncio.sleep(25)

        # Setup subscriptions for all pages
        print("🔍 Setting up WebSocket subscriptions for all tabs...")
        
        for i, page in enumerate(pages):
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

        print("\n🎯 MULTI-TURBO MONITOR ACTIVE:")
        print("⭐ TURBO data (WebSocket - multiple turbos)")  
        print("📈 UNDERLYING data (SSE - auto-detected)")
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
    elif t == "depth":
        bid = d.get("bid") or d.get("bid1")
        ask = d.get("ask") or d.get("ask1")
        if bid is not None or ask is not None:
            print(f"[{page_name}] {emoji} TURBO Depth | Bid: {bid} | Ask: {ask}")

if __name__ == "__main__":
    asyncio.run(main())