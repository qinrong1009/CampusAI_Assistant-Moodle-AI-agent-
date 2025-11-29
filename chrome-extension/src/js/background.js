/**
 * Background Service Worker
 * 處理插件的後台邏輯和訊息傳遞
 */

console.log("[Background] Service Worker 已啟動");
console.log("[Background] extension id:", chrome.runtime.id);

// 儲存視窗 ID，避免重複創建
let chatWindowId = null;
// 儲存當前會話 session_id（由後端回傳或建立）
let sessionId = null;

// 監聽擴展圖標點擊
chrome.action.onClicked.addListener(() => {
  console.log("[Background] 圖標被點擊");
  openChatWindow();
});

// 監聽快捷鍵命令
chrome.commands.onCommand.addListener((command) => {
  console.log("[Background] 命令:", command);
  if (command === "toggle-sidebar") {
    // 改為創建獨立視窗
    openChatWindow();
  }
});

// 創建或聚焦聊天視窗
async function openChatWindow() {
  try {
    // 檢查視窗是否已存在
    if (chatWindowId !== null) {
      try {
        const existingWindow = await chrome.windows.get(chatWindowId);
        // 視窗存在，聚焦它
        await chrome.windows.update(chatWindowId, { focused: true });
        console.log("[Background] 聚焦現有視窗");
        return;
      } catch (e) {
        // 視窗不存在了，清除 ID
        chatWindowId = null;
      }
    }
    
    // 創建新視窗（不指定位置，讓系統自動決定）
    const window = await chrome.windows.create({
      url: chrome.runtime.getURL("src/html/sidebar.html"),
      type: "popup",
      width: 500,
      height: 700
    });
    
    chatWindowId = window.id;
    console.log("[Background] 創建新視窗, ID:", chatWindowId);

    // 監聽視窗關閉
    chrome.windows.onRemoved.addListener(async (windowId) => {
      if (windowId === chatWindowId) {
        chatWindowId = null;
        console.log("[Background] 視窗已關閉");

        try {
          // 嘗試從儲存取得 sessionId（若存在）
          chrome.storage.local.get(["session_id", "apiUrl"], async (data) => {
            const sid = data.session_id || sessionId;
            const apiUrl = data.apiUrl || "http://localhost:5001";
            if (sid) {
              console.log("[Background] 清除後端記憶，session_id:", sid);
              try {
                await fetch(`${apiUrl}/api/clear_memory`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ session_id: sid })
                });
              } catch (err) {
                console.warn("[Background] 無法呼叫 clear_memory:", err);
              }

              // 清除本地 session_id
              chrome.storage.local.remove(["session_id"], () => {
                sessionId = null;
              });
            }
          });
        } catch (err) {
          console.error("[Background] 清除記憶失敗:", err);
        }
      }
    });
  } catch (error) {
    console.error("[Background] 創建視窗失敗:", error);
  }
}

// 處理來自 Content Script 的訊息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    console.log("[Background] 收到訊息:", request, 'from', sender);

    // 防護：如果沒有 action 欄位也能容錯處理
    const action = request && (request.action || request.type);
  
    if (action === "captureScreenshot") {
    // 截圖請求 - 需要截取當前活躍的標籤頁，而不是發送者的視窗
    captureActiveTabScreenshot().then(screenshot => {
      sendResponse({ 
        success: true, 
        screenshot: screenshot 
      });
    }).catch(error => {
      console.error("[Background] 截圖失敗:", error);
      sendResponse({ 
        success: false, 
        error: error.message 
      });
    });
    return true; // 異步回應
  }
  
    if (action === "clearMemory") {
    // 主動清除 session 記憶（來自 sidebar 的 unload 或 background 事件）
    chrome.storage.local.get(["session_id", "apiUrl"], async (data) => {
      const sid = data.session_id || sessionId;
      const apiUrl = data.apiUrl || "http://localhost:5001";
      if (!sid) {
        sendResponse({ success: true, cleared: false, reason: 'no session' });
        return;
      }

        try {
          console.log('[Background] calling clear_memory ->', apiUrl + '/api/clear_memory', 'session', sid);
          const resp = await fetch(`${apiUrl}/api/clear_memory`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sid })
          });
          let json = null;
          try { json = await resp.json(); } catch(e) { json = null; }
          console.log('[Background] clear_memory response', resp.status, json);

          chrome.storage.local.remove(["session_id"], () => {
            sessionId = null;
            sendResponse({ success: true, cleared: true, server_response: json });
          });
        } catch (err) {
          console.warn('[Background] clearMemory failed', err);
          // 回傳詳細錯誤，並避免未處理 promise
          sendResponse({ success: false, error: err && err.message ? err.message : String(err) });
        }
    });

    return true;
  }
  
    if (action === "setModel") {
    // 設置預設模型（會呼叫後端 /api/set_model 並儲存到 sync）
    const newModel = request.model;
    chrome.storage.sync.get(["apiUrl"], async (data) => {
      const apiUrl = data.apiUrl || "http://localhost:5001";
      try {
        const resp = await fetch(`${apiUrl}/api/set_model`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: newModel })
        });
        const json = await resp.json().catch(() => null);
        if (resp.ok) {
          // 儲存到 sync，讓未來請求有預設值
          chrome.storage.sync.set({ modelType: newModel }, () => {
            console.log('[Background] modelType saved to sync:', newModel);
            sendResponse({ success: true, model: newModel, server_response: json });
          });
        } else {
          sendResponse({ success: false, error: json || `HTTP ${resp.status}` });
        }
      } catch (err) {
        console.error('[Background] setModel failed', err);
        sendResponse({ success: false, error: err && err.message ? err.message : String(err) });
      }
    });

    return true; // async response
  }
  
    if (action === "apiCall") {
    // 從儲存空間取得 API 設定
    chrome.storage.sync.get(["apiUrl", "modelType"], (data) => {
      const apiUrl = data.apiUrl || "http://localhost:5001";
  const model = data.modelType || "llama3.2";

      // 嘗試取得已存的 session_id
      chrome.storage.local.get(["session_id"], (sdata) => {
        const storedSid = sdata.session_id || sessionId;

  console.log("[Background] 呼叫 API:", apiUrl, " model:", model, " session:", storedSid);

        // 呼叫後端 API（包含 session_id，如果有的話）
        fetch(`${apiUrl}/api/analyze`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            screenshot: request.screenshot,
            question: request.question,
            model: model,
            session_id: storedSid
          })
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log("[Background] API 成功:", data);
          // 後端可能回傳 session_id（當 server 生成新的 session）
          if (data && data.session_id) {
            sessionId = data.session_id;
            chrome.storage.local.set({ session_id: sessionId }, () => {
              console.log('[Background] 儲存 session_id 到 local storage:', sessionId);
            });
          }

          sendResponse({ success: true, data: data });
        })
        .catch(error => {
          console.error("[Background] API 錯誤:", error);
          sendResponse({ 
            success: false, 
            error: error && error.message ? error.message : String(error)
          });
        });
      });
    });
    
    // 異步發送回應
    return true;
  }
  } catch (err) {
    console.error('[Background] onMessage handler error', err);
    // 若發生未預期錯誤，嘗試回應以避免 sender 的 promise reject
    try { sendResponse({ success: false, error: String(err) }); } catch(e) {}
    return false;
  }
});

// 截取當前活躍標籤頁的截圖（用於獨立視窗）
async function captureActiveTabScreenshot() {
  try {
    // 目標：避免捕捉到 extension popup 本身，優先取得最後聚焦的普通瀏覽器視窗 (type='normal')
    try {
      const lastNormal = await chrome.windows.getLastFocused({ populate: true, windowTypes: ['normal'] });
      if (lastNormal && lastNormal.id && lastNormal.tabs && lastNormal.tabs.length) {
        const activeTab = lastNormal.tabs.find(t => t.active) || lastNormal.tabs[0];
        if (activeTab) {
          console.log('[Background] 使用 last-focused normal window id:', lastNormal.id, 'tabId:', activeTab.id);
          return await captureScreenshotFromWindow(lastNormal.id);
        }
      }
    } catch (err) {
      // 可能沒有 normal window 或 API 拋錯，繼續後續 fallback
      console.warn('[Background] getLastFocused normal window 失敗，嘗試掃描所有普通視窗:', err);
    }

    // fallback：掃描所有普通視窗以找到 active tab
    const windows = await chrome.windows.getAll({ populate: true, windowTypes: ['normal'] });
    for (const win of windows) {
      const activeTab = win.tabs && win.tabs.find(tab => tab.active);
      if (activeTab) {
        console.log('[Background] fallback 使用 window id:', win.id, 'tabId:', activeTab.id);
        return await captureScreenshotFromWindow(win.id);
      }
    }

    throw new Error('找不到可截圖的普通瀏覽器視窗');
  } catch (error) {
    console.error('[Background] 截取活躍標籤失敗:', error);
    throw error;
  }
}

// 從指定視窗截圖
async function captureScreenshotFromWindow(windowId) {
  try {
    // 使用 Chrome 的 captureVisibleTab API
    const dataUrl = await chrome.tabs.captureVisibleTab(windowId, {
      format: 'jpeg',
      quality: 80
    });

    console.log('[Background] 截圖成功');
    return dataUrl;
  } catch (error) {
    console.error('[Background] Chrome API 截圖失敗:', error);

    // 如果錯誤與 activeTab 權限相關，輸出更清楚的提示
    try {
      if (error && error.message && error.message.includes('activeTab')) {
        console.warn('[Background] activeTab 權限未啟用：請從 toolbar 按鈕或快捷鍵觸發擴充功能，或在 manifest 加上 "tabs" 權限。');
      }
    } catch (e) {
      // ignore
    }

    // 回傳靜態備援圖，避免在 service worker 中使用 document/DOM
    return FALLBACK_IMG;
  }
}

// 使用 Chrome 的截圖 API（舊版，保留以防需要）
async function captureScreenshotFromTab(tabId) {
  try {
    // 使用 Chrome 的 captureVisibleTab API
    const dataUrl = await chrome.tabs.captureVisibleTab(null, {
      format: 'jpeg',
      quality: 80
    });

    console.log('[Background] 截圖成功');
    return dataUrl;
  } catch (error) {
    console.error('[Background] Chrome API 截圖失敗:', error);
    return FALLBACK_IMG;
  }
}

// 插件安裝時初始化設定
chrome.runtime.onInstalled.addListener(() => {
  console.log("[Background] 插件已安裝，初始化設定");
  chrome.storage.sync.set({
    apiUrl: "http://localhost:5001",
  modelType: "llama3.2"
  });
});

console.log("[Background] 所有監聽器已註冊");

// 靜態備援圖（1x1 PNG 白色），用於在無法使用 Chrome 截圖 API 時回傳，不依賴 DOM
const FALLBACK_IMG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==';
