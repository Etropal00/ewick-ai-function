// netlify/functions/ai.js
export async function handler(event) {
  // --- CORS headers ---
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
  };

  // --- Preflight CORS ---
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: cors, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers: cors, body: "Method Not Allowed" };
  }

  try {
    const { idea = "", system = "" } = JSON.parse(event.body || "{}");

    if (!idea.trim()) {
      return {
        statusCode: 400,
        headers: cors,
        body: JSON.stringify({ error: "Missing 'idea' in request body." }),
      };
    }

    const API_KEY = process.env.GOOGLE_API_KEY;
    if (!API_KEY) {
      return {
        statusCode: 500,
        headers: cors,
        body: JSON.stringify({ error: "GOOGLE_API_KEY not set on Netlify." }),
      };
    }

    const body = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text:
                `Transform this idea into a single-line, production-ready prompt in English ` +
                `(cinematic, camera, lighting, textures, tone). Keep it one sentence: "${idea}"`
            }
          ]
        }
      ],
      systemInstruction: { parts: [{ text: system || "" }] },
    };

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    return {
      statusCode: 200,
      headers: { ...cors, "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ error: "Internal error", detail: String(err) }),
    };
  }
}
