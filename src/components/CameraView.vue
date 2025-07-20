<template>
  <div>
    <button v-if="!cameraActive" @click="startCamera">📸 カメラを起動</button>
    <video
      v-show="cameraActive"
      ref="videoRef"
      autoplay
      muted
      playsinline
      style="width:100%; max-width:400px; border:1px solid #ccc;"
    ></video>
    <canvas
      v-show="cameraActive"
      ref="canvasRef"
      style="display:block; margin-top:12px; width:100%; max-width:400px;"
    ></canvas>
    <div v-if="cameraActive && !matchedCard" style="margin-top:16px; color:#888;">
      Recognizing card...
    </div>
    <div v-if="matchedCard" style="margin-top:16px;">
      <h3>認識されたカード：{{ matchedCard.name }}</h3>
      <img :src="matchedCard.image_url" style="width:200px; border-radius:8px;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { matchFeatures } from '../utils/matcher'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const matchedCard = ref<{ name: string; image_url: string } | null>(null)
let stream: MediaStream | null = null

// features.jsonをfetchで読み込む
const features = ref<any[]>([])
onMounted(async () => {
  const res = await fetch('/features.json')
  features.value = await res.json()
})

// 特徴量抽出関数
function extractDescriptorsFromImageData(imageData: ImageData) {
  const descriptors = []
  for (let i = 0; i < imageData.data.length; i += 4 * 1000) {
    descriptors.push([
      imageData.data[i],
      imageData.data[i + 1],
      imageData.data[i + 2],
    ])
  }
  return descriptors
}

// カメラ起動処理
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { exact: "environment" } }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
      await startDetectionLoop()
    }
  } catch (err) {
    // fallback: フロントカメラも許可
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.value) {
        videoRef.value.srcObject = stream
        cameraActive.value = true
        await startDetectionLoop()
      }
    } catch (err2) {
      alert('カメラが起動できませんでした（HTTPS接続や権限設定をご確認ください）')
      console.error('Camera error:', err2)
    }
  }
}

// OpenCV準備待機
function waitUntilOpenCVReady(): Promise<void> {
  return new Promise((resolve) => {
    const check = () => {
      if (window.cv && cv.Mat) resolve()
      else setTimeout(check, 100)
    }
    check()
  })
}

// ランダムな色を返す関数
function getRandomColor() {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}

// カード検出＆推定ループ
async function startDetectionLoop() {
  const canvas = canvasRef.value!
  const video = videoRef.value!
  const ctx = canvas.getContext('2d')!

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  await waitUntilOpenCVReady()

  const src = new cv.Mat(canvas.height, canvas.width, cv.CV_8UC4)
  const gray = new cv.Mat()
  const cap = new cv.VideoCapture(video)

  const loop = () => {
    cap.read(src)
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)

    const edges = new cv.Mat()
    cv.Canny(gray, edges, 50, 150)

    const contours = new cv.MatVector()
    const hierarchy = new cv.Mat()
    cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    let detected = false

    for (let i = 0; i < contours.size(); i++) {
      const contour = contours.get(i)
      const rect = cv.boundingRect(contour)
      const aspectRatio = rect.height / rect.width // ←縦/横
      const targetRatio = 88 / 63 // ≒ 1.3968
      const tolerance = 0.2

      if (Math.abs(aspectRatio - targetRatio) < tolerance) {
        detected = true
        ctx.strokeStyle = getRandomColor()
        ctx.lineWidth = 3
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height)

        // カード領域を切り出して特徴量抽出＆推定
        const cardImageData = ctx.getImageData(rect.x, rect.y, rect.width, rect.height)
        const descriptors = extractDescriptorsFromImageData(cardImageData)
        if (features.value.length > 0) {
          const bestMatch = matchFeatures(descriptors, features.value)
          if (bestMatch) {
            matchedCard.value = { name: bestMatch.name, image_url: bestMatch.image_url }
          }
        }
      }
      contour.delete()
    }

    edges.delete()
    contours.delete()
    hierarchy.delete()

    // 検出できなかった場合はmatchedCardをnullに
    if (!detected) {
      matchedCard.value = null
    }

    requestAnimationFrame(loop)
  }

  loop()
}
</script>