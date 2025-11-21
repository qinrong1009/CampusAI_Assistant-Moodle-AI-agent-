/**
 * DEBUG SCROLL ISSUE - 在 Chrome Console 執行此代碼
 * 
 * 使用方式：
 * 1. 打開任何網站
 * 2. 按 F12 打開 DevTools
 * 3. 進入 Console 頁籤
 * 4. 複製貼上此代碼並執行
 */

console.log("========== SCROLL DEBUG START ==========");

// 1. 檢查 iframe 容器是否存在和其屬性
const container = document.getElementById("aiAssistantContainer");
if (container) {
  console.log("✓ iframe 容器找到");
  console.log("  - display:", container.style.display);
  console.log("  - pointerEvents:", container.style.pointerEvents);
  console.log("  - position:", container.style.position);
  console.log("  - z-index:", container.style.zIndex);
  console.log("  - width:", container.style.width);
  console.log("  - height:", container.style.height);
  
  const rect = container.getBoundingClientRect();
  console.log("  - getBoundingClientRect():", {
    left: rect.left,
    right: rect.right,
    top: rect.top,
    bottom: rect.bottom
  });
} else {
  console.log("✗ iframe 容器未找到");
}

// 2. 檢查 iframe 元素
const iframe = document.getElementById("aiAssistantFrame");
if (iframe) {
  console.log("✓ iframe 元素找到");
  console.log("  - src:", iframe.src);
  console.log("  - pointerEvents:", iframe.style.pointerEvents);
  console.log("  - scrolling:", iframe.scrolling);
} else {
  console.log("✗ iframe 元素未找到");
}

// 3. 檢查滾輪事件監聽器
console.log("\n檢查滾輪事件監聽器:");
let wheelListenerCount = 0;
document.addEventListener('wheel', (e) => {
  wheelListenerCount++;
  console.log(`[Wheel Event #${wheelListenerCount}]`, {
    clientX: e.clientX,
    clientY: e.clientY,
    deltaY: e.deltaY,
    defaultPrevented: e.defaultPrevented,
    cancelable: e.cancelable,
    target: e.target.tagName,
    targetId: e.target.id,
    targetClass: e.target.className
  });
  
  // 檢查事件是否被阻止
  if (e.defaultPrevented) {
    console.warn("⚠️  滾輪事件被阻止 (preventDefault 已調用)");
  }
}, false);

console.log("✓ 滾輪事件監聽器已添加（查看 console 以觀察滾輪事件）");

// 4. 測試滾動
console.log("\n===== 測試滾動 =====");
console.log("嘗試滾動網頁...");
window.scrollBy(0, 50);
console.log("scrollY 當前值:", window.scrollY);

// 5. 檢查 body 和 html 是否有阻擋屬性
const bodyStyle = window.getComputedStyle(document.body);
const htmlStyle = window.getComputedStyle(document.documentElement);

console.log("\n檢查 document.body 的 CSS:");
console.log("  - overflow:", bodyStyle.overflow);
console.log("  - overflow-y:", bodyStyle.overflowY);
console.log("  - position:", bodyStyle.position);
console.log("  - pointerEvents:", bodyStyle.pointerEvents);

console.log("\n檢查 document.documentElement 的 CSS:");
console.log("  - overflow:", htmlStyle.overflow);
console.log("  - overflow-y:", htmlStyle.overflowY);
console.log("  - position:", htmlStyle.position);
console.log("  - pointerEvents:", htmlStyle.pointerEvents);

// 6. 嘗試強制滾動測試
console.log("\n===== 強制滾動測試 =====");
try {
  document.documentElement.scrollTop = 100;
  document.body.scrollTop = 100;
  console.log("✓ 已執行 scrollTop = 100");
  console.log("  實際 scrollY:", window.scrollY);
} catch (e) {
  console.error("✗ 滾動失敗:", e);
}

// 7. 檢查是否有其他 overlay 元素阻擋
console.log("\n===== 檢查全屏 overlay 元素 =====");
const allFixed = document.querySelectorAll("[style*='position: fixed'], [style*='position:fixed']");
console.log(`找到 ${allFixed.length} 個 fixed 定位元素`);
allFixed.forEach((el, i) => {
  const style = el.getAttribute('style');
  const zIndex = window.getComputedStyle(el).zIndex;
  const pointerEvents = window.getComputedStyle(el).pointerEvents;
  console.log(`  [${i}] ${el.tagName}#${el.id}.${el.className} z-index:${zIndex} pointerEvents:${pointerEvents}`);
});

console.log("\n========== DEBUG INFO 收集完成 ==========");
console.log("上方信息應該能幫助你找出問題所在。");
console.log("接下來滾動頁面，觀察 [Wheel Event] 的日誌。");
