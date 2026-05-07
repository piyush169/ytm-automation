const WEBHOOK_URL = "https://fishless-semibiologic-nella.ngrok-free.dev/webhook/ytm-add";

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) return;

  try {
    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const t = (sel) => document.querySelector(sel)?.textContent?.trim() || "";

        const host = location.hostname;
        const pageUrl = location.href;

        let title = "";
        let artist = "";
        let byline = "";

        if (host.includes("music.youtube.com")) {
          title = t("ytmusic-player-bar .title");
          byline = t("ytmusic-player-bar .byline");
          artist = (byline.split("•")[0] || byline.split("·")[0] || "").trim();
        } else if (host.includes("youtube.com")) {
          title =
            t("ytd-watch-metadata h1 yt-formatted-string") ||
            t("h1.title yt-formatted-string") ||
            (document.title || "").replace(/\s*-\s*YouTube\s*$/i, "").trim();

          artist =
            t("#owner #channel-name a") ||
            t("ytd-channel-name a") ||
            "";

          byline = artist;
        }

        if (!title) {
          title = (document.title || "")
            .replace(/\s*-\s*YouTube Music\s*$/i, "")
            .replace(/\s*-\s*YouTube\s*$/i, "")
            .trim();
        }

        if (!artist) artist = "Unknown Artist";
        if (!title) title = "Unknown Title";

        return { pageUrl, title, artist, byline, capturedAt: new Date().toISOString() };
      }
    });

    console.log("Payload:", result);

    const resp = await fetch(WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result)
    });

    console.log("Webhook status:", resp.status, "body:", await resp.text());
  } catch (e) {
    console.error("Failed sending to n8n:", e);
  }
});
