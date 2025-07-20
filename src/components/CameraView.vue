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
    <div v-if="errorMsg" style="color:#f00; margin-top:12px; white-space:pre-wrap;">{{ errorMsg }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const opencvReady = ref(false)
const errorMsg = ref('')
let stream: MediaStream | null = null

onMounted(() => {
  function checkOpenCV() {
    if (window.cv && cv.Mat) {
      opencvReady.value = true
    } else {
      opencvReady.value = false
    }
  }
  const scripts = document.getElementsByTagName('script')
  for (let i = 0; i < scripts.length; i++) {
    const s = scripts[i]
    if (s.src && s.src.includes('opencv.js')) {
      s.addEventListener('load', checkOpenCV)
    }
  }
  setTimeout(checkOpenCV, 2000)
  checkOpenCV()
})

async function startCamera() {
  errorMsg.value = ''
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
      errorMsg.value = 'カメラが起動できませんでした\n' + (err2 instanceof Error ? err2.message : String(err2))
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
        // cv.imread(canvas) の失敗を検知
        let src: any
        try {
          src = cv.imread(canvas)
          if (!src || src.empty()) {
            throw new Error('cv.imread(canvas) で画像の取得に失敗しました')
          }
        } catch (e) {
          errorMsg.value = 'cv.imread(canvas) で失敗しました\n' + (e instanceof Error ? e.message : String(e))
          requestAnimationFrame(loop)
          return
        }

        const gray = new cv.Mat()
        const edges = new cv.Mat()
        try {
          cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)
          cv.Canny(gray, edges, 50, 150)
        } catch (e) {
          errorMsg.value = 'OpenCV画像処理で失敗しました\n' + (e instanceof Error ? e.message : String(e))
          src.delete()
          gray.delete()
          edges.delete()
          requestAnimationFrame(loop)
          return
        }

        // ImageData生成時の型やサイズ不一致を検知し、RGBA変換で対応
        try {
          // Cannyの出力は1chなのでRGBAに変換
          const rgba = new cv.Mat()
          cv.cvtColor(edges, rgba, cv.COLOR_GRAY2RGBA)
          const edgeImageData = new ImageData(
            new Uint8ClampedArray(rgba.data),
            rgba.cols,
            rgba.rows
          )
          ctx.save()
          ctx.globalAlpha = 0.5
          ctx.putImageData(edgeImageData, 0, 0)
          ctx.restore()
          rgba.delete()
        } catch (e) {
          errorMsg.value = 'ImageData生成または描画で失敗しました\n' + (e instanceof Error ? e.message : String(e))
        }

        src.delete()
        gray.delete()
        edges.delete()
      } else {
        ctx.font = 'bold 32px sans-serif'
        ctx.fillStyle = '#f00'
        ctx.fillText('OpenCV loading...', 30, 50)
      }
    } catch (e) {
      errorMsg.value = 'OpenCV error!\n' + (e instanceof Error ? e.message : String(e))
    }

    requestAnimationFrame(loop)
  }

  waitForVideoReady()
}
</script>