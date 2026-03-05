if (!window.__bookmarkScraperLoaded) {
  window.__bookmarkScraperLoaded = true;

  const seenIds = new Set();

  function scrapeVisible() {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    const tweets = [];

    for (const article of articles) {
      let tweetId = '';
      let authorUsername = '';
      const statusLinks = article.querySelectorAll('a[href*="/status/"]');
      for (const link of statusLinks) {
        const match = link.getAttribute('href').match(/^\/([^/]+)\/status\/(\d+)/);
        if (match) {
          authorUsername = match[1];
          tweetId = match[2];
          break;
        }
      }
      if (!tweetId || seenIds.has(tweetId)) continue;
      seenIds.add(tweetId);

      const showMore = article.querySelector('[data-testid="tweet-text-show-more-link"]');
      if (showMore) showMore.click();

      const tweetTextEl = article.querySelector('div[data-testid="tweetText"]');
      const text = tweetTextEl ? tweetTextEl.innerText : '';

      tweets.push({
        id: tweetId,
        text,
        author_username: authorUsername,
        tweet_url: `https://x.com/${authorUsername}/status/${tweetId}`,
        scraped_at: new Date().toISOString()
      });
    }

    return tweets;
  }

  async function scrapeVisibleMode() {
    await new Promise(r => setTimeout(r, 300));
    return scrapeVisible();
  }

  async function scrapeWithScroll() {
    const allTweets = [];
    let stallCount = 0;
    const MAX_STALLS = 3;
    const MAX_TWEETS = 2000;
    const SCROLL_PX = 1500;
    const SCROLL_DELAY = 400;

    while (stallCount < MAX_STALLS && allTweets.length < MAX_TWEETS) {
      const batch = scrapeVisible();

      chrome.runtime.sendMessage({
        action: 'scrollProgress',
        found: allTweets.length + batch.length,
        newInBatch: batch.length
      });

      allTweets.push(...batch);

      if (batch.length === 0) {
        stallCount++;
        await new Promise(r => setTimeout(r, 1000));
      } else {
        stallCount = 0;
      }

      if (stallCount >= MAX_STALLS || allTweets.length >= MAX_TWEETS) break;

      window.scrollBy(0, SCROLL_PX);
      await new Promise(r => setTimeout(r, SCROLL_DELAY));
    }

    return allTweets;
  }

  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === 'scan') {
      const run = async () => {
        seenIds.clear();

        const tweets = msg.mode === 'scroll'
          ? await scrapeWithScroll()
          : await scrapeVisibleMode();

        chrome.runtime.sendMessage({ action: 'saveTweets', tweets });
      };
      run();
      return true;
    }
  });
}
