export function matchFeatures(
  inputDescriptors: any,
  referenceData: any[],
  cv: any
): { name: string; image_url: string } | null {
  let bestMatch = null
  let highestScore = 0

  for (const card of referenceData) {
    const refDescriptors = cv.matFromArray(card.descriptors, cv.CV_8U) // JSON配列から復元
    const matcher = new cv.BFMatcher(cv.NORM_HAMMING, false)
    const matches = new cv.DMatchVector()

    matcher.match(inputDescriptors, refDescriptors, matches)

    const score = matches.size()
    if (score > highestScore) {
      highestScore = score
      bestMatch = card
    }

    refDescriptors.delete()
    matcher.delete()
    matches.delete()
  }

  return bestMatch
}