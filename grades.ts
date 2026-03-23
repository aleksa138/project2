import fetch from "node-fetch";

export default async function handler(req: any, res: any) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    const { url, login, password } = req.body;

    // =========================
    // COOKIE SESSION
    // =========================
    let cookies = "";

    // Получаем initial cookies
    const initRes = await fetch(url, {
      method: "GET"
    });

    cookies = initRes.headers.get("set-cookie") || "";

    // =========================
    // LOGIN
    // =========================
    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookies
      },
      body: `login=${login}&password=${password}`
    });

    // =========================
    // GET PAGE
    // =========================
    const pageRes = await fetch(url, {
      headers: {
        "Cookie": cookies
      }
    });

    const html = await pageRes.text();

    // =========================
    // PARSING (regex)
    // =========================
    const result: any = {};

    const matches = [...html.matchAll(/([А-Яа-яA-Za-z ]+)<\/td>.*?(\d(?:,\d)*)/g)];

    for (const m of matches) {
      const subject = m[1].trim();
      const grades = (m[2].match(/\d/g) || []).map(Number);

      if (!grades.length) continue;

      const avg = grades.reduce((a, b) => a + b, 0) / grades.length;

      result[subject] = {
        grades,
        avg: Number(avg.toFixed(2))
      };
    }

    if (Object.keys(result).length === 0) {
      return res.json({
        error: "Не удалось распарсить. Нужна адаптация под HTML ЭлЖура"
      });
    }

    return res.json(result);

  } catch (e: any) {
    return res.status(500).json({ error: e.message });
  }
}