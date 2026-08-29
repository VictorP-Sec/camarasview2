import sharp from 'sharp';

export default async function handler(req, res) {
  const { code } = req.query;
  if (!code) return res.status(400).json({ error: 'code required' });

  const url = `https://movilidad.alicante.es/sites/default/files/camara/${code}.jpg`;

  try {
    const resp = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://movilidad.alicante.es/camaras',
      },
    });
    if (!resp.ok) return res.status(resp.status).send('Upstream error');

    const buf = Buffer.from(await resp.arrayBuffer());

    const upscaled = await sharp(buf)
      .resize(1796, 1012, { kernel: 'lanczos3' })
      .jpeg({ quality: 92 })
      .toBuffer();

    res.setHeader('Content-Type', 'image/jpeg');
    res.setHeader('Cache-Control', 'public, s-maxage=120, max-age=60, stale-while-revalidate');
    res.send(upscaled);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
