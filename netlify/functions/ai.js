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
        body: JSON.stringify({ text: "⚠️ Écris une idée avant de lancer la génération." }),
      };
    }

    const API_KEY = process.env.GOOGLE_API_KEY;
    if (!API_KEY) {
      return {
        statusCode: 500,
        headers: cors,
        body: JSON.stringify({ text: "Clé API manquante sur Netlify." }),
      };
    }

    // ✅ modèle stable et fiable
    const url = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`;

    const body = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `Create a vivid, cinematic English prompt based on this idea: "${idea}". 
Include details of camera style, lighting, texture, mood and tone. 
Write one single sentence.`,
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

    // ✅ Nettoyage + réponse par défaut
    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ||
      "😅 L’IA n’a rien répondu. Essaie avec une idée plus complète (ex. « un robot jouant au hockey sous la neige »).";

    return {
      statusCode: 200,
      headers: { ...cors, "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    };
  } catch (err) {
    console.error("Erreur Gemini:", err);
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ text: "Oups, erreur interne. Réessaie dans un instant." }),
    };
  }
}
