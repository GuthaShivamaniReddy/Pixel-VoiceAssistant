const ALLOWED_HOSTS = new Set(["cyberflorida.org", "www.cyberflorida.org"]);

export function isAllowlistedHref(href: string): boolean {
  try {
    const url = new URL(href);
    if (url.protocol !== "https:") {
      return false;
    }
    return ALLOWED_HOSTS.has(url.hostname.toLowerCase());
  } catch {
    return false;
  }
}
