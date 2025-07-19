import fs from 'fs'
import fetch from 'node-fetch'
import { createCanvas, loadImage } from 'canvas'

// OpenCV.jsをHTML経由で読み込む方法もあるけど、ここでは疑似的に流れだけ記述

async function extractORBDescriptors(imageUrl, name) {
  const img = await loadImage(imageUrl)
  const canvas = createCanvas(img.width, img.height)
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0)

  // ↓ 本来はOpenCV.jsのMatに変換してORB処理する
  // ここでは仮処理で、画像サイズ・色平均だけ抽出（PoC用ダミー）
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
  const targetCard = {
    name: '星街すいせい',
    image_url: 'https://hololive-card.vercel.app/card_images/001.jpg',
  }

  const result = await extractORBDescriptors(targetCard.image_url, targetCard.name)
  fs.writeFileSync('./features.json', JSON.stringify([result], null, 2))
  console.log('features.json を出力しました 🎉')
}

main()