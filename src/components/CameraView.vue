<template>
  <div>
    <!-- カメラ起動ボタン -->
    <button v-if="!cameraActive" @click="startCamera">📸 カメラを起動</button>

    <!-- 映像表示 -->
    <video
      v-show="cameraActive"
      ref="videoRef"
      autoplay
      muted
      playsinline
      style="width:100%; max-width:400px; border:1px solid #ccc;"
    ></video>

    <!-- 認識枠描画 canvas -->
    <canvas
      v-show="cameraActive"
      ref="canvasRef"
      style="display:block; margin-top:12px; width:100%; max-width:400px;"
    ></canvas>

    <!-- 認識結果表示（後続ステップ用） -->
    <div v-if="matchedCard" style="margin-top:16px;">
      <h3>認識されたカード：{{ matchedCard.name }}</h3>
      <img :src="matchedCard.image_url" style="width:200px; border-radius:8px;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// DOM参照と状態
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const matchedCard = ref<{ name: string; image_url: string } | null>(null)

let stream: MediaStream | null = null

// カメラ起動処理
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
      await startDetectionLoop()
    }
  } catch (err) {
    alert('カメラが起動できませんでした（HTTPS接続や権限設定をご確認ください）')
    console.error('Camera error:', err)
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

// 矩形検出＆canvas描画ループ
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

    for (let i = 0; i < contours.size(); i++) {
      const contour = contours.get(i)
      const rect = cv.boundingRect(contour)

      const aspectRatio = rect.width / rect.height
      const targetRatio = 63 / 88
      const tolerance = 0.2

      if (Math.abs(aspectRatio - targetRatio) < tolerance) {
        ctx.strokeStyle = '#00ff88'
        ctx.lineWidth = 3
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height)
      }

      contour.delete()
    }

    edges.delete()
    contours.delete()
    hierarchy.delete()

    requestAnimationFrame(loop)
  }

  loop()
}
</script>