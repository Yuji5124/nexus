export function searchAssets(assets, filters = {}) {
  const words = String(filters.query || filters.q || '').toLowerCase().split(/\s+/).filter(Boolean);
  const tags = Array.isArray(filters.tags) ? filters.tags : String(filters.tags || '').split(',').filter(Boolean);
  return assets.map(asset => {
    const text = [asset.name, asset.category, asset.subcategory, asset.description, ...(asset.tags || []), ...(asset.recommendedFor || [])].join(' ').toLowerCase();
    return { asset, score: words.reduce((n, word) => n + (text.includes(word) ? 1 : 0), 0) };
  }).filter(({asset, score}) => (!words.length || score > 0)
    && (!filters.category || filters.category === 'all' || asset.category === filters.category)
    && (!filters.format || filters.format === 'all' || asset.format.toLowerCase() === filters.format.toLowerCase())
    && tags.every(tag => (asset.tags || []).some(t => t.toLowerCase() === tag.toLowerCase()))
    && (!filters.maxTriangles || (asset.triangles != null && asset.triangles <= Number(filters.maxTriangles)))
    && (filters.animated == null || asset.animated === filters.animated)
    && (!filters.license || filters.license === 'all' || asset.license === filters.license))
    .sort((a,b) => b.score-a.score || a.asset.name.localeCompare(b.asset.name)).map(({asset}) => asset);
}
