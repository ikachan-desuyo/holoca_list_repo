<template>
  <div>
    <video ref="videoRef" autoplay muted playsinline></video>
    <canvas ref="canvasRef"></canvas>
    <div v-if="matchedCard">
      <p>カード認識：{{ matchedCard.name }}</p>
      <img :src="matchedCard.image_url" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { matchFeatures } from '../utils/matcher'
import featuresData from '../assets/features.json'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const matchedCard = ref<{ name: string; image_url: string } | null>(null)

onMounted(async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true })
  if (videoRef.value) videoRef.value.srcObject = stream

  const cv = await loadOpenCV() // ← WASM読み込み関数（省略可）
  const cap = new cv.VideoCapture(videoRef.value!)

  const detect = () => {
    const frame = new cv.Mat(videoRef.value!.videoHeight, videoRef.value!.videoWidth, cv.CV_8UC4)
    cap.read(frame)

    const roi = extractCardRegion(frame, cv) // ← 矩形検出（この関数は別途設計）

    if (roi) {
      const keypoints = new cv.KeyPointVector()
      const descriptors = new cv.Mat()
      const detector = new cv.ORB()
      detector.detectAndCompute(roi, new cv.Mat(), keypoints, descriptors)

      const matched = matchFeatures(descriptors, featuresData, cv)
      if (matched) matchedCard.value = matched
    }

    frame.delete()
    setTimeout(detect, 1000)
  }

  detect()
})
</script>