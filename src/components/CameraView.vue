<template>
  <div>
    <!-- カメラ起動ボタン -->
    <button v-if="!cameraActive" @click="startCamera">📸 カメラを起動</button>

    <!-- カメラ映像 -->
    <video
      v-show="cameraActive"
      ref="videoRef"
      autoplay
      muted
      playsinline
      style="width:100%; max-width:400px; border:1px solid #ccc;"
    ></video>

    <!-- 認識結果用 canvas（後続ステップで使用） -->
    <canvas
      v-show="cameraActive"
      ref="canvasRef"
      style="display:block; margin-top:12px; width:100%; max-width:400px;"
    ></canvas>

    <!-- 認識されたカードの表示 -->
    <div v-if="matchedCard" style="margin-top:16px;">
      <h3>認識されたカード：{{ matchedCard.name }}</h3>
      <img :src="matchedCard.image_url" style="width:200px; border-radius:8px;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const matchedCard = ref<{ name: string; image_url: string } | null>(null)

let stream: MediaStream | null = null

// カメラ起動
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
      startDetectionLoop()
    }
  } catch (err) {
    alert('カメラ起動に失敗しました（HTTPS接続や権限をご確認ください）')
  }
}

// 認識ループ（canvasに枠を描画）
function startDetectionLoop() {
  const canvas = canvasRef.value
  const video = videoRef.value
  if (!canvas || !video) return

  const ctx = canvas.getContext('2d')!
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const loop = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // 💡 仮の矩形領域（中央のエリアを毎回描画する例）
    const rectWidth = canvas.width * 0.6
    const rectHeight = canvas.height * 0.75
    const rectX = (canvas.width - rectWidth) / 2
    const rectY = (canvas.height - rectHeight) / 2

    ctx.strokeStyle = '#00ff88'
    ctx.lineWidth = 4
    ctx.strokeRect(rectX, rectY, rectWidth, rectHeight)

    requestAnimationFrame(loop)
  }

  loop()
}
</script>