<template>
  <div>
    <button v-if="!cameraActive && opencvReady" @click="startCamera">📸 カメラを起動</button>
    <video ref="videoRef" autoplay muted playsinline style="display:none"></video>
    <canvas
      ref="canvasRef"
      style="display:block; margin-top:12px; width:100%; max-width:400px; border:1px solid #ccc;"
    ></canvas>
    <div v-if="!opencvReady" style="color:#f00; margin-top:12px;">OpenCV.js 読み込み中...</div>
    <div v-if="errorMsg" style="color:#f00; margin-top:12px; white-space:pre-wrap;">{{ errorMsg }}</div>
    <div v-if="recognizedCard" style="color:#080; margin-top:12px;">認識結果: {{ recognizedCard }}</div>
    <button v-if="cameraActive && opencvReady" @click="onRecognize">カード認識する</button>
    <!-- ▼ 特徴点可視化セレクタと画像表示を追加 -->
    <div style="margin-top:24px;">
      <label>特徴点可視化カード選択：</label>
      <select v-model="selectedFeatureIdx">
        <option v-for="(feature, idx) in features" :key="feature.image_url" :value="idx">
          {{ feature.image_url ? feature.image_url.split('/').pop() : feature.name || idx }}
        </option>
      </select>
      <div v-if="selectedFeatureIdx !== null && features[selectedFeatureIdx]">
        <img
          :src="features[selectedFeatureIdx].image_url"
          :alt="features[selectedFeatureIdx].name"
          ref="featureImgRef"
          style="max-width:300px; display:block; margin:12px 0; border:1px solid #ccc;"
          @load="drawKeypoints"
        />
        <canvas
          ref="featureKeyCanvasRef"
          style="max-width:300px; display:block; margin-bottom:12px; border:1px solid #ccc;"
        ></canvas>
      </div>
    </div>
    <!-- ▲ ここまで -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraActive = ref(false)
const opencvReady = ref(false)
const errorMsg = ref('')
const features = ref<any[]>([])
const recognizedCard = ref('')
let stream: MediaStream | null = null

// ▼ 特徴点可視化用
const selectedFeatureIdx = ref<number | null>(null)
const featureImgRef = ref<HTMLImageElement>()
const featureKeyCanvasRef = ref<HTMLCanvasElement>()
// ▲

onMounted(async () => {
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

  // features.jsonの読み込み（Vite/GitHub Pages対応）
  try {
    const baseUrl = import.meta.env.BASE_URL || '/'
    let idx = 1
    let allFeatures: any[] = []
    while (true) {
      const url = `${baseUrl}features${idx}.json`
      try {
        const res = await fetch(url)
        if (!res.ok) break
        const data = await res.json()
        if (!Array.isArray(data) || data.length === 0) break
        allFeatures = allFeatures.concat(data)
        idx++
      } catch {
        break
      }
    }
    features.value = allFeatures
    if (features.value.length > 0) selectedFeatureIdx.value = 0
  } catch (e) {
    errorMsg.value = 'features*.jsonの読み込みに失敗しました\n' + (e instanceof Error ? e.message : String(e))
  }
})

function onRecognize() {
  if (!cameraActive.value || !opencvReady.value || !canvasRef.value) return
  const canvas = canvasRef.value
  let gray: any
  try {
    const src = cv.imread(canvas)
    gray = new cv.Mat()
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY)
    src.delete()
  } catch (e) {
    errorMsg.value = '認識用画像取得失敗\n' + (e instanceof Error ? e.message : String(e))
    return
  }
  recognizeCard(gray)
  gray.delete()
}

// ▼ 特徴点可視化処理
function drawKeypoints() {
  const idx = selectedFeatureIdx.value
  if (idx === null || !features.value[idx] || !featureImgRef.value || !featureKeyCanvasRef.value) return
  const img = featureImgRef.value
  const canvas = featureKeyCanvasRef.value
  const ctx = canvas.getContext('2d')!
  // 画像サイズにcanvasを合わせる
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
  // 特徴点を描画
  const keypoints = features.value[idx].keypoints || []
  ctx.save()
  ctx.strokeStyle = 'red'
  ctx.lineWidth = 2
  for (const kp of keypoints) {
    // ORBの場合 [x, y, size, angle, response, octave, class_id] など
    const x = kp[0], y = kp[1]
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.stroke()
  }
  ctx.restore()
}
// セレクト変更時や画像ロード時に再描画
watch(selectedFeatureIdx, () => setTimeout(drawKeypoints, 0))
// ▲

async function startCamera() {
  errorMsg.value = ''
  recognizedCard.value = ''
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
        // --- OpenCV画像処理 ---
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

        // エッジ画像をRGBAに変換して重ね描画
        try {
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

// カード認識処理
function recognizeCard(gray: any) {
  // ORB特徴量抽出
  const orb = new cv.ORB()
  const keypoints = new cv.KeyPointVector()
  const descriptors = new cv.Mat()
  orb.detectAndCompute(gray, new cv.Mat(), keypoints, descriptors)

  let bestMatchIdx = -1
  let bestMatchCount = 0

  for (let idx = 0; idx < features.value.length; idx++) {
    const feature = features.value[idx]
    // DB側のdescriptorsをMatに変換
    const dbDescArr = feature.descriptors.flat()
    const dbDescriptors = cv.matFromArray(
      feature.descriptors.length,
      feature.descriptors[0].length,
      cv.CV_8U,
      dbDescArr
    )
    const bf = new cv.BFMatcher(cv.NORM_HAMMING, true)
    const matches = new cv.DMatchVector()
    bf.match(descriptors, dbDescriptors, matches)
    if (matches.size() > bestMatchCount) {
      bestMatchCount = matches.size()
      bestMatchIdx = idx
    }
    dbDescriptors.delete()
    matches.delete()
    bf.delete()
  }

  descriptors.delete()
  keypoints.delete()
  orb.delete()

  if (bestMatchIdx >= 0 && bestMatchCount > 10) { // マッチ数閾値は適宜調整
    recognizedCard.value = features.value[bestMatchIdx].name + `（マッチ数: ${bestMatchCount}）`
  } else {
    recognizedCard.value = '認識できませんでした'
  }
}
</script>