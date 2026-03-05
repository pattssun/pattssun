const totalCountEl = document.getElementById('totalCount');
const newCountEl = document.getElementById('newCount');
const dupeCountEl = document.getElementById('dupeCount');
const scanBtn = document.getElementById('scanBtn');
const exportBtn = document.getElementById('exportBtn');
const clearBtn = document.getElementById('clearBtn');
const logEl = document.getElementById('log');

let scanMode = 'visible';
let activeTabId = null;

// Mode toggle
document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelector('.mode-btn.active').classList.remove('active');
    btn.classList.add('active');
    scanMode = btn.dataset.mode;
  });
});

// Load stored count on open
chrome.storage.local.get(['bookmarks_data'], ({ bookmarks_data = [] }) => {
  totalCountEl.textContent = bookmarks_data.length;
  exportBtn.disabled = bookmarks_data.length === 0;
});

// Check if current tab is bookmarks page
chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  if (tab && /^https:\/\/(x\.com|twitter\.com)\/i\/bookmarks/.test(tab.url)) {
    scanBtn.disabled = false;
    activeTabId = tab.id;
  }
});

// Scan
scanBtn.addEventListener('click', () => {
  if (!activeTabId) return;
  scanBtn.disabled = true;
  scanBtn.textContent = 'Scanning...';
  logEl.classList.add('visible');
  logEl.textContent = 'Starting scan...\n';

  chrome.tabs.sendMessage(activeTabId, { action: 'scan', mode: scanMode });
});

// Listen for messages from background/content
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === 'scrollProgress') {
    logEl.textContent += `Found ${msg.found} tweets (+${msg.newInBatch} new)\n`;
    logEl.scrollTop = logEl.scrollHeight;
  } else if (msg.action === 'scanComplete') {
    totalCountEl.textContent = msg.totalCount;
    newCountEl.textContent = msg.newCount;
    dupeCountEl.textContent = msg.dupeCount;
    scanBtn.disabled = false;
    scanBtn.textContent = 'Scan Bookmarks';
    exportBtn.disabled = msg.totalCount === 0;
    logEl.textContent += `Done! ${msg.newCount} new, ${msg.dupeCount} dupes, ${msg.totalCount} total\n`;
  }
});

// Save to Folder
exportBtn.addEventListener('click', async () => {
  exportBtn.disabled = true;
  exportBtn.textContent = 'Saving...';
  logEl.classList.add('visible');
  logEl.textContent += 'Saving to folder...\n';

  try {
    const result = await chrome.runtime.sendMessage({ action: 'saveToFolder' });
    if (result.success) {
      logEl.textContent += `Saved! ${result.bookmarks} bookmarks\n`;
    } else {
      logEl.textContent += `Error: ${result.error}\n`;
    }
  } catch (err) {
    logEl.textContent += `Error: ${err.message}\n`;
  }

  exportBtn.disabled = false;
  exportBtn.textContent = 'Save to Folder';
});

// Clear
clearBtn.addEventListener('click', () => {
  chrome.storage.local.remove(['bookmarks_index', 'bookmarks_data'], () => {
    totalCountEl.textContent = '0';
    newCountEl.textContent = '-';
    dupeCountEl.textContent = '-';
    exportBtn.disabled = true;
    logEl.textContent = '';
    logEl.classList.remove('visible');
  });
});
