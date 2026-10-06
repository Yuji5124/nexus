const common = {
  type: "model",
  format: "GLB",
  free: true,
  downloadable: true,
  author: "See source page",
  polygonCount: null,
  fileSize: null
};

// Provider adapters can replace this catalog without changing the API or UI.
export const catalog = [
  {
    ...common,
    id: "polyhaven-tree-apple-01",
    title: "Tree Apple 01",
    provider: "Poly Haven",
    license: "CC0",
    tags: ["nature", "tree", "low poly", "outdoor"],
    thumbnail: "https://cdn.polyhaven.com/asset_img/thumbs/tree_apple_01.png?width=512",
    sourceUrl: "https://polyhaven.com/a/tree_apple_01",
    modelUrl: "https://dl.polyhaven.org/file/ph-assets/Models/gltf/1k/tree_apple_01/tree_apple_01.gltf"
  },
  {
    ...common,
    id: "polyhaven-rock-tall-01",
    title: "Rock Tall 01",
    provider: "Poly Haven",
    license: "CC0",
    tags: ["nature", "rock", "environment"],
    thumbnail: "https://cdn.polyhaven.com/asset_img/thumbs/rock_tall_01.png?width=512",
    sourceUrl: "https://polyhaven.com/a/rock_tall_01",
    modelUrl: "https://dl.polyhaven.org/file/ph-assets/Models/gltf/1k/rock_tall_01/rock_tall_01.gltf"
  },
  {
    ...common,
    id: "ambientcg-plants-001",
    title: "Potted Plant 001",
    provider: "ambientCG",
    license: "CC0",
    tags: ["nature", "plant", "interior", "prop"],
    thumbnail: "https://ambientcg.com/get?file=Plants001-PNG&preview=1",
    sourceUrl: "https://ambientcg.com/view?id=Plants001",
    modelUrl: null
  },
  {
    ...common,
    id: "kenney-platformer-kit",
    title: "Platformer Kit",
    provider: "Kenney",
    license: "CC0 1.0",
    tags: ["platform", "game", "environment", "pack"],
    type: "pack",
    thumbnail: "https://kenney.nl/assets/assetpacks/platformer-kit.png",
    sourceUrl: "https://kenney.nl/assets/platformer-kit",
    modelUrl: null
  },
  {
    ...common,
    id: "blenderkit-free-chair",
    title: "Modern Chair",
    provider: "BlenderKit Free",
    license: "Free - check terms",
    free: true,
    tags: ["furniture", "chair", "interior"],
    thumbnail: "https://assets.blenderkit.com/thumbnail/placeholder.png",
    sourceUrl: "https://www.blenderkit.com/asset-gallery-detail/modern-chair/",
    modelUrl: null
  },
  {
    ...common,
    id: "quaternius-props-pack",
    title: "Universal Nature Pack",
    provider: "Quaternius",
    license: "CC0",
    tags: ["nature", "props", "stylized", "pack"],
    thumbnail: "https://quaternius.com/img/UniversalNature/UniversalNature.jpg",
    sourceUrl: "https://quaternius.com/packs/ultimatenature.html",
    modelUrl: null
  }
];
