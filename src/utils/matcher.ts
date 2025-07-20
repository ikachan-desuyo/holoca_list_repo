export function matchFeatures(
  inputDescriptors: number[][],
  referenceData: { name: string; image_url: string; descriptors: number[][] }[]
): { name: string; image_url: string } | null {
  let bestMatch = null
  let minDistance = Infinity

  for (const card of referenceData) {
    const refDescriptors = card.descriptors
    // 距離計算
    let sum = 0
    const len = Math.min(inputDescriptors.length, refDescriptors.length)
    for (let i = 0; i < len; i++) {
      const d1 = inputDescriptors[i]
      const d2 = refDescriptors[i]
      sum += Math.sqrt(
        Math.pow(d1[0] - d2[0], 2) +
        Math.pow(d1[1] - d2[1], 2) +
        Math.pow(d1[2] - d2[2], 2)
      )
    }
    const avgDist = sum / len
    if (avgDist < minDistance) {
      minDistance = avgDist
      bestMatch = card
    }
  }

  return bestMatch
}