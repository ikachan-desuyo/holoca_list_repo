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
    <div v-if="debugStatus" style="margin-top:12px; color:#f66;">
      Debug: {{ debugStatus }}
    </div>
    <canvas
      v-show="cameraActive"
      ref="debugCanvasRef"
      style="display:block; margin-top:8px; width:100%; max-width:400px; border:1px dashed #f66;"
    ></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { matchFeatures } from '../utils/matcher'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const debugCanvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const matchedCard = ref<{ name: string; image_url: string } | null>(null)
const debugStatus = ref('')
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
  const debugCanvas = debugCanvasRef.value!
  const video = videoRef.value!
  const ctx = canvas.getContext('2d')!
  const debugCtx = debugCanvas.getContext('2d')!

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  debugCanvas.width = video.videoWidth
  debugCanvas.height = video.videoHeight

  await waitUntilOpenCVReady()

  const src = new cv.Mat(canvas.height, canvas.width, cv.CV_8UC4)
  const gray = new cv.Mat()
  const edges = new cv.Mat()
  const cap = new cv.VideoCapture(video)

  const loop = () => {
    cap.read(src)
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)
    debugStatus.value = 'Canny edge detection...'
    cv.Canny(gray, edges, 50, 150)

    // エッジ画像をデバッグcanvasに表示
    cv.imshow(debugCanvas, edges)

    debugStatus.value = 'Finding contours...'
    const contours = new cv.MatVector()
    const hierarchy = new cv.Mat()
    cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      ctx.font = 'bold 32px sans-serif'
      ctx.fillStyle = '#00f'
      ctx.fillText('hololive card reading', 30, 50)


    let detected = false
    let foundRect = false

    for (let i = 0; i < contours.size(); i++) {
      const contour = contours.get(i)
      const rect = cv.boundingRect(contour)
      const aspectRatio = rect.height / rect.width
      const targetRatio = 88 / 63
      const tolerance = 0.2
      const area = rect.width * rect.height

      // 全ての矩形を細い赤枠で描画
      ctx.strokeStyle = '#f66'
      ctx.lineWidth = 1
      ctx.strokeRect(rect.x, rect.y, rect.width, rect.height)

      // 矩形情報をcanvasにテキスト描画
      ctx.font = '12px sans-serif'
      ctx.fillStyle = '#f66'
      ctx.fillText(
        `AR:${aspectRatio.toFixed(2)} A:${area}`,
        rect.x,
        rect.y > 12 ? rect.y - 2 : rect.y + 12
      )

      // カード候補なら太い枠＆色変更
      if (Math.abs(aspectRatio - targetRatio) < tolerance && area > 5000) {
        foundRect = true
        ctx.strokeStyle = getRandomColor()
        ctx.lineWidth = 3
        ctx.strokeRect(rect.x, rect.y, rect.width, rect.height)

        ctx.font = 'bold 14px sans-serif'
        ctx.fillStyle = '#0c0'
        ctx.fillText('CARD?', rect.x, rect.y + 20)

        debugStatus.value = 'Card-like rectangle found. Matching features...'
        // ...以下略...
      }
      contour.delete()
    }

    edges.delete()
    contours.delete()
    hierarchy.delete()

    if (!foundRect) {
      debugStatus.value = 'No card-like rectangle found (aspect ratio mismatch)'
    }
    if (!detected) {
      matchedCard.value = null
    }

    requestAnimationFrame(loop)
  }

  loop()
}
</script>