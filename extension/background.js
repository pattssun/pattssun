chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'saveTweets') {
    handleSaveTweets(msg.tweets);
  } else if (msg.action === 'scrollProgress') {
    chrome.runtime.sendMessage(msg).catch(() => {});
  } else if (msg.action === 'saveToFolder') {
    handleSaveToFolder().then(sendResponse);
    return true;
  }
});

async function handleSaveTweets(tweets) {
  const { bookmarks_index = {}, bookmarks_data = [] } = await chrome.storage.local.get(['bookmarks_index', 'bookmarks_data']);

  let newCount = 0;
  let dupeCount = 0;

  for (const tweet of tweets) {
    if (bookmarks_index[tweet.id]) {
      dupeCount++;
    } else {
      bookmarks_index[tweet.id] = true;
      bookmarks_data.push(tweet);
      newCount++;
    }
  }

  await chrome.storage.local.set({ bookmarks_index, bookmarks_data });

  chrome.runtime.sendMessage({
    action: 'scanComplete',
    newCount,
    dupeCount,
    totalCount: bookmarks_data.length
  }).catch(() => {});
}

async function handleSaveToFolder() {
  try {
    const { bookmarks_data = [] } = await chrome.storage.local.get(['bookmarks_data']);

    const jsonStr = JSON.stringify(bookmarks_data, null, 2);
    const jsonDataUrl = 'data:application/json;base64,' + btoa(unescape(encodeURIComponent(jsonStr)));
    await chrome.downloads.download({
      url: jsonDataUrl,
      filename: 'bookmarks.json',
      conflictAction: 'overwrite'
    });

    return { success: true, bookmarks: bookmarks_data.length };
  } catch (err) {
    return { success: false, error: err.message };
  }
}
