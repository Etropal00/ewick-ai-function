export async function handler(event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const { idea, system } = JSON.parse(event.body || "{}");

  const body = {
    contents: [
      {
        role: "user",
        parts: [
          {
            text: `Transform this idea into a single-line, production-ready prompt in English (cinematic, camera, lighting, textures): "${idea}"`
          }
        ]
      }
    ],
    systemInstruction: { parts: [{ text: system || "" }] },
  };

  const res = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" +
      process.env.GOOGLE_API_KEY,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }
  );

  const data = await res.json();

  return {
    statusCode: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  };
}
