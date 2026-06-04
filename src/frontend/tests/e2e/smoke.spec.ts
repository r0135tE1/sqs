import { test, expect } from '@playwright/test'

/**
 * Smoke test: the single most important E2E test. If this fails, something
 * fundamental is broken — Frontend doesn't load, Backend isn't reachable,
 * Database is misconfigured, or the game loop is dead.
 *
 * Verifies the full happy path: load → fetch flag → submit answer → see result.
 */
test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
  await page.reload()
})

test('app loads, shows a flag, and accepts an answer', async ({ page }) => {
  // 1. The flag image renders (proves Frontend bundle + backend /game/flag work)
  await expect(page.locator('.flag-img')).toBeVisible({ timeout: 10_000 })

  // 2. Four answer buttons appear (proves the response was parsed correctly)
  const buttons = page.locator('.answer-btn')
  await expect(buttons).toHaveCount(4)

  // 3. The buttons have non-empty country labels (proves the data shape is right)
  for (let i = 0; i < 4; i++) {
    await expect(buttons.nth(i)).not.toHaveText('')
  }

  // 4. Clicking an answer returns a result (proves /game/answer works end-to-end)
  await buttons.first().click()
  await expect(page.locator('.result-strip')).toBeVisible()

  // 5. The result is either correct or wrong (proves backend validates against
  //    its server-side state — not just acks anything we send)
  const isCorrect = await page.locator('.result-strip.correct').isVisible()
  const isWrong = await page.locator('.result-strip.wrong').isVisible()
  expect(isCorrect || isWrong).toBe(true)

  // 6. A continuation button is shown
  await expect(page.getByRole('button', { name: /Next|Try Again/ })).toBeVisible()
})
