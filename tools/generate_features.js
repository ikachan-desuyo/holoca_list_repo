import fs from 'fs'
import fetch from 'node-fetch'
import { createCanvas, loadImage } from 'canvas'

const CARD_DATA_URL = 'https://raw.githubusercontent.com/ikachan-desuyo/holoca_list_repo/main/json_file/card_data.json'

async function extractDescriptors(imageUrl, name) {
  const img = await loadImage(imageUrl)
  const canvas = createCanvas(img.width, img.height)
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0)

  const imageData = ctx.getImageData(0, 0, img.width, img.height)
  const descriptors = []

  for (let i = 0; i < imageData.data.length; i += 4 * 1000) {
    descriptors.push([
      imageData.data[i],
      imageData.data[i + 1],
      imageData.data[i + 2],
    ])
  }

  return {
    name,
    image_url: imageUrl,
    descriptors,
  }
}

async function main() {
  const res = await fetch(CARD_DATA_URL)
  const cardData = await res.json()

  const results = []

  for (const card of cardData) {
    try {
      const { name, image_url } = card
      const feature = await extractDescriptors(image_url, name)
      results.push(feature)
      console.log(`✅ ${name} done`)
    } catch (err) {
      console.warn(`⚠️ ${card.name} failed: ${err.message}`)
    }
  }

  fs.writeFileSync('./features.json', JSON.stringify(results, null, 2))
  console.log(`🎉 features.json を ${results.length} 件で出力しました`)
}

main()