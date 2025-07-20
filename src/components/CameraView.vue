<template>
  <div>
    <button v-if="!cameraActive" @click="startCamera">📸 カメラを起動</button>
    <!-- デバッグ用にvideoを表示 -->
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

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { exact: "environment" } }
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

  // カメラ映像のサイズが取得できるまで待つ
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
    ctx.font = 'bold 32px sans-serif'
    ctx.fillStyle = '#00f'
    ctx.fillText('Hello Canvas!', 30, 50)
    if (cameraActive.value) {
      requestAnimationFrame(loop)
    }
  }

  waitForVideoReady()
}
</script>