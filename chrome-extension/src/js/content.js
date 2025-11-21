/**
 * Content Script
 * 在網頁上運行，負責與頁面交互和截圖
 */

let sidebarInjected = false;

console.log("[Content] Content script 正在初始化...");

// 快捷鍵監聽 (Alt+A 或 Cmd+Shift+A on Mac)
document.addEventListener("keydown", (event) => {
  console.log("[Content] 按鍵:", event.key, "Alt:", event.altKey, "Cmd:", event.metaKey, "Code:", event.code);
  
  // Windows/Linux: Alt+A
  if (event.altKey && event.code === "KeyA") {
    console.log("[Content] 觸發 Alt+A");
    event.preventDefault();
    toggleSidebar();
  }
  
  // macOS: Cmd+Shift+A
  if (event.metaKey && event.shiftKey && event.code === "KeyA") {
    console.log("[Content] 觸發 Cmd+Shift+A");
    event.preventDefault();
    toggleSidebar();
  }
});

// 從 Background 接收訊息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("[Content] 收到訊息:", request.action);
  if (request.action === "toggleSidebar") {
    toggleSidebar();
  }
});

// 切換側邊欄顯示/隱藏
function toggleSidebar() {
  console.log("[Content] toggleSidebar 調用, sidebarInjected:", sidebarInjected);
  if (!sidebarInjected) {
    injectSidebar();
    sidebarInjected = true;
    // 新建立的 sidebar 自動打開
    const sidebar = document.getElementById("aiAssistantContainer");
    if (sidebar) {
      sidebar.style.display = "block";
      sidebar.style.pointerEvents = "auto";
    }
  } else {
    const sidebar = document.getElementById("aiAssistantContainer");
    if (sidebar) {
      console.log("[Content] 切換 sidebar 可見性");
      const isShown = sidebar.style.display === "block";
      sidebar.style.display = isShown ? "none" : "block";
      sidebar.style.pointerEvents = isShown ? "none" : "auto";
    }
  }
}

// 在頁面中注入側邊欄
function injectSidebar() {
  console.log("[Content] 開始注入 sidebar...");
  
  // 檢查是否已存在
  if (document.getElementById("aiAssistantContainer")) {
    console.log("[Content] Sidebar 已存在");
    return;
  }

  // 建立 iframe 容器 - 由 content.css 提供樣式
  const container = document.createElement("div");
  container.id = "aiAssistantContainer";
  
  // 從 sidebar.html 載入內容
  const iframe = document.createElement("iframe");
  iframe.src = chrome.runtime.getURL("src/html/sidebar.html");
  iframe.id = "aiAssistantFrame";
  // iframe 樣式由 content.css 定義，無需 inline style

  container.appendChild(iframe);
  document.body.appendChild(container);
  
  console.log("[Content] Sidebar iframe 已創建");

  // 與 iframe 通信
  setTimeout(() => {
    const iframeWindow = iframe.contentWindow;
    window.addEventListener("message", (event) => {
      if (event.source !== iframeWindow) return;

      if (event.data.type === "SCREENSHOT_REQUEST") {
        console.log("[Content] 收到截圖請求");
        captureScreenshot().then(screenshot => {
          iframeWindow.postMessage({
            type: "SCREENSHOT_RESPONSE",
            screenshot: screenshot
          }, "*");
        });
      }

      if (event.data.type === "SUBMIT_QUESTION") {
        console.log("[Content] 收到提問");
        handleQuestionSubmit(
          event.data.question,
          event.data.screenshot,
          iframeWindow
        );
      }

      if (event.data.type === "CLOSE_SIDEBAR") {
        console.log("[Content] 收到關閉側邊欄請求");
        container.style.display = "none";
        container.style.pointerEvents = "none";
      }
    });
    console.log("[Content] Message listener 已設置");
  }, 500);
}

// ❌ 完全移除 wheel listener - 這是阻擋滾動的根本原因！
// 改用 CSS pointer-events 來控制滾輪交互
// 詳見 sidebar.css: .chat-area 設置了 overflow-y: auto
// 詳見 sidebar.html: iframe 內部會自動處理滾輪

// 截圖功能 - 調用 Background 進行真實截圖
async function captureScreenshot() {
  try {
    console.log("[Content] 請求 Background 進行截圖");
    
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: "captureScreenshot" },
        (response) => {
          if (response && response.success) {
            console.log("[Content] 截圖成功");
            resolve(response.screenshot);
          } else {
            console.error("[Content] 截圖失敗");
            reject(new Error(response?.error || "截圖失敗"));
          }
        }
      );
    });
  } catch (error) {
    console.error("[Content] 截圖錯誤:", error);
    return await captureScreenshotSimple();
  }
}

// 簡單截圖方案（不依賴任何庫）
async function captureScreenshotSimple() {
  try {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // 背景
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 標題
    ctx.fillStyle = "#333";
    ctx.font = "bold 16px Arial";
    ctx.fillText("頁面截圖", 20, 40);
    
    // 頁面信息
    ctx.font = "12px Arial";
    ctx.fillStyle = "#666";
    ctx.fillText("URL: " + window.location.href, 20, 70);
    ctx.fillText("時間: " + new Date().toLocaleString(), 20, 90);
    ctx.fillText("視窗大小: " + canvas.width + " x " + canvas.height, 20, 110);
    
    // 頁面內容預覽（簡單文字版）
    ctx.fillStyle = "#999";
    ctx.font = "11px monospace";
    let y = 150;
    const lines = document.body.innerText.split("\n").slice(0, 20);
    lines.forEach((line, index) => {
      if (y < canvas.height - 20) {
        ctx.fillText(line.substring(0, 80), 20, y);
        y += 20;
      }
    });
    
    return canvas.toDataURL("image/jpeg", 0.8);
  } catch (error) {
    console.error("簡單截圖失敗:", error);
    throw new Error("無法截圖");
  }
}

// 處理提問提交
function handleQuestionSubmit(question, screenshot, iframeWindow) {
  console.log("[Content] 提交問題:", {
    question: question.substring(0, 50),
    screenshotLength: screenshot ? screenshot.length : 0,
    screenshotPreview: screenshot ? screenshot.substring(0, 50) : null
  });
  
  // 發送訊息到 Background Script
  chrome.runtime.sendMessage({
    action: "apiCall",
    question: question,
    screenshot: screenshot
  }, (response) => {
    console.log("[Content] API 回應:", response);
    if (response && response.success) {
      iframeWindow.postMessage({
        type: "API_RESPONSE",
        success: true,
        data: response.data
      }, "*");
    } else {
      iframeWindow.postMessage({
        type: "API_RESPONSE",
        success: false,
        error: (response && response.error) || "API 連接失敗"
      }, "*");
    }
  });
}

console.log("[Content] Content script 已成功載入並初始化");

