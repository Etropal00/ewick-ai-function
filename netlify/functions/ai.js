// netlify/functions/ai.js
export async function handler(event) {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
  };

  if (event.httpMethod === "OPTIONS")
    return { statusCode: 204, headers: cors, body: "" };

  if (event.httpMethod !== "POST")
    return { statusCode: 405, headers: cors, body: "Method Not Allowed" };

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

    // ✅ modèle compatible et stable
    const url = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`;

    const body = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `You are a creative cinematic prompt writer. 
Write a vivid, production-quality prompt in English based on this idea: "${idea}". 
Include camera angle, lighting, texture, emotion and background in one sentence.`,
            },
          ],
        },
      ],
      generationConfig: {
        temperature: 0.8,   // créativité
        maxOutputTokens: 200,
      },
      safetySettings: [
        { category: "HARM_CATEGORY_SEXUAL", threshold: "BLOCK_NONE" },
        { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_NONE" },
        { category: "HARM_CATEGORY_DEROGATORY", threshold: "BLOCK_NONE" },
      ],
    };

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ||
      "😅 L’IA n’a rien répondu. Essaie avec une phrase un peu plus détaillée (ex. « un robot jouant au hockey sous la neige au coucher du soleil »).";

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
      body: JSON.stringify({ text: "Oups, erreur interne. Réessaie tantôt." }),
