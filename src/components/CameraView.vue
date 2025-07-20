<template>
  <div>
    <button v-if="!cameraActive && opencvReady" @click="startCamera">📸 カメラを起動</button>
    <video
      ref="videoRef"
      autoplay
      muted
      playsinline
      style="display:none"
    ></video>
    <canvas
      ref="canvasRef"
      style="display:block; margin-top:12px; width:100%; max-width:400px; border:1px solid #ccc;"
    ></canvas>
    <div v-if="!opencvReady" style="color:#f00; margin-top:12px;">OpenCV.js 読み込み中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const opencvReady = ref(false)
let stream: MediaStream | null = null

onMounted(() => {
  // OpenCV.jsのonloadイベントでロード検知
  function checkOpenCV() {
    if (window.cv && cv.Mat) {
      opencvReady.value = true
    } else {
      opencvReady.value = false
    }
  }
  // scriptタグを探してonloadを設定
  const scripts = document.getElementsByTagName('script')
  for (let i = 0; i < scripts.length; i++) {
    const s = scripts[i]
    if (s.src && s.src.includes('opencv.js')) {
      s.addEventListener('load', checkOpenCV)
    }
  }
  // 念のため2秒後にも再チェック
  setTimeout(checkOpenCV, 2000)
  // 初回も一応チェック
  checkOpenCV()
})

async function startCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      cameraActive.value = true
      startDrawingLoop()
    }
  } catch (err) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.value) {
        videoRef.value.srcObject = stream
        await videoRef.value.play()
        cameraActive.value = true
        startDrawingLoop()
      }
    } catch (err2) {
      alert('カメラが起動できませんでした')
      console.error('Camera error:', err2)
    }
  }
}

function startDrawingLoop() {
  const video = videoRef.value!
  const canvas = canvasRef.value!
  const ctx = canvas.getContext('2d')!

  function waitForVideoReady() {
    if (video.videoWidth > 0 && video.videoHeight > 0) {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      loop()
    } else {
      requestAnimationFrame(waitForVideoReady)
    }
  }

  function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    try {
      if (window.cv && cv.Mat) {
        const src = cv.imread(canvas)
        const gray = new cv.Mat()
        const edges = new cv.Mat()

        cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)
        cv.Canny(gray, edges, 50, 150)

        const edgeImageData = new ImageData(
          new Uint8ClampedArray(edges.data),
          edges.cols,
          edges.rows
        )
        ctx.save()
        ctx.globalAlpha = 0.5
        ctx.putImageData(edgeImageData, 0, 0)
        ctx.restore()

        src.delete()
        gray.delete()
        edges.delete()
      } else {
        ctx.font = 'bold 32px sans-serif'
        ctx.fillStyle = '#f00'
        ctx.fillText('OpenCV loading...', 30, 50)
      }
    } catch (e) {
      ctx.font = 'bold 32px sans-serif'
      ctx.fillStyle = '#f00'
      ctx.fillText('OpenCV error!', 30, 80)
      console.error(e)
    }

    requestAnimationFrame(loop)
  }

  waitForVideoReady()
}
</script>