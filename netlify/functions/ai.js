// netlify/functions/ai.js
export async function handler(event) {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
  };

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

    // ✅ modèle stable et accessible publiquement
    const url = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`;

    const body = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `Transform this idea into a single-line, production-ready cinematic prompt (camera, lighting, texture, tone): "${idea}". Context: ${system}`,
            },
          ],
        },
      ],
    };

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    // ✅ Nettoyage : extraire uniquement le texte
    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ||
      "No text generated.";

    return {
      statusCode: 200,
      headers: { ...cors, "Content-Type": "application/json" },
      body: JSON.stringify({ text }), // 👈 renvoie seulement le texte
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({
        error: "Internal error",
        detail: String(err),
      }),
    };
  }
}
