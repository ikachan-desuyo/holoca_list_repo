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
import { ref } from 'vue'

// DOM参照
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()

// 状態管理
const cameraActive = ref(false)
const matchedCard = ref<{ name: string; image_url: string } | null>(null)

// カメラ起動処理
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
      console.log('✅ カメラ起動成功')

      // このあと OpenCV.js の処理や認識ループを追加する予定
      // → detectLoop() などの関数はステップ②で定義
    }
  } catch (err) {
    console.error('❌ カメラ起動失敗:', err)
    alert(
      'カメラが起動できませんでした。\nHTTPS接続か端末の権限設定を確認してください。'
    )
  }
}
</script>