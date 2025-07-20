<template>
  <div>
    <button v-if="!cameraActive" @click="startCamera">📸 カメラを起動</button>
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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
let stream: MediaStream | null = null

// OpenCV.jsのロード待ち
function waitUntilOpenCVReady(): Promise<void> {
  return new Promise((resolve) => {
    const check = () => {
      if ((window as any).cv && (window as any).cv.Mat) resolve()
      else setTimeout(check, 100)
    }
    check()
  })
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { exact: "environment" } }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      cameraActive.value = true
      await waitUntilOpenCVReady()
      startDrawingLoop()
    }
  } catch (err) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.value) {
        videoRef.value.srcObject = stream
        await videoRef.value.play()
        cameraActive.value = true
        await waitUntilOpenCVReady()
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

    if (window.cv && cv.Mat) {
      // --- OpenCV処理 ---
      const src = new cv.Mat(canvas.height, canvas.width, cv.CV_8UC4)
      const gray = new cv.Mat()
      const edges = new cv.Mat()

      let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      src.data.set(imageData.data)

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
      // OpenCV未ロード時もcanvasにテキストを描画
      ctx.font = 'bold 32px sans-serif'
      ctx.fillStyle = '#f00'
      ctx.fillText('OpenCV loading...', 30, 50)
    }

    requestAnimationFrame(loop)
  }

  waitForVideoReady()
}
</script>