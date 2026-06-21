export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = url.searchParams.get("url");

    if (!target) {
      return new Response("Missing ?url= parameter", { status: 400 });
    }

    try {
      new URL(target);
    } catch {
      return new Response("Invalid URL", { status: 400 });
    }

    const resp = await fetch(target, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "*/*",
      },
      redirect: "follow",
    });

    const newHeaders = new Headers(resp.headers);
    newHeaders.set("Access-Control-Allow-Origin", "*");
    newHeaders.delete("X-Frame-Options");
    newHeaders.delete("Content-Security-Policy");

    return new Response(resp.body, {
      status: resp.status,
      headers: newHeaders,
    });
  },
};
