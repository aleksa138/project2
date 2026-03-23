export default async function handler(req: any, res: any) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Only POST allowed" });
    }

    const { url, login, password } = req.body;

    // 👉 пока делаем стабильный mock (чтобы всё работало)
    // потом можно подключить реальный парсинг

    const result = {
      "Математика": {
        grades: [5, 4, 3, 5],
        avg: 4.25
      },
      "Физика": {
        grades: [4, 4, 5],
        avg: 4.33
      },
      "Английский": {
        grades: [5, 5, 4],
        avg: 4.67
      }
    };

    return res.status(200).json(result);

  } catch (e: any) {
    return res.status(500).json({ error: e.message });
  }
}