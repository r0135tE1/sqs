import { test, expect } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  // Each test starts with a fresh app state.
  await page.goto('/')
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
  await page.reload()
})

test('app loads and shows a flag with 4 answer options', async ({ page }) => {
  await expect(page.locator('.flag-img')).toBeVisible({ timeout: 5000 })
  await expect(page.locator('.answer-btn')).toHaveCount(4)
})

test('anonymous user is invited to log in', async ({ page }) => {
  await expect(page.getByText('Log in to track your high score')).toBeVisible()
})

test('clicking an answer reveals correct/wrong feedback', async ({ page }) => {
  await expect(page.locator('.flag-img')).toBeVisible({ timeout: 5000 })
  await page.locator('.answer-btn').first().click()

  await expect(page.locator('.result-strip')).toBeVisible()
  await expect(page.getByRole('button', { name: /Next|Try Again/ })).toBeVisible()
})

test('signup creates an account and logs the user in', async ({ page }) => {
  const username = `e2e_${Date.now()}`
  await page.getByRole('button', { name: 'Sign Up' }).click()
  await page.locator('#signup-username').fill(username)
  await page.locator('#signup-password').fill('password123')
  await page.getByRole('button', { name: 'Sign Up', exact: true }).last().click()

  await expect(page.locator('.username')).toHaveText(username, { timeout: 5000 })
  await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible()
})

test('login with wrong password shows an error', async ({ page }) => {
  await page.getByRole('button', { name: 'Log In' }).click()
  await page.locator('#login-username').fill('nonexistent_user_abc')
  await page.locator('#login-password').fill('wrongpassword')
  await page.getByRole('button', { name: 'Login', exact: true }).click()

  await expect(page.locator('.error-box')).toBeVisible()
  await expect(page.locator('.error-box')).toContainText(/Invalid username or password|Login failed/)
})

test('anonymous user sees signup prompt after wrong answer with score', async ({ page }) => {
  await expect(page.locator('.flag-img')).toBeVisible({ timeout: 5000 })

  /**
   * Click "Next"/"Try Again" and wait until the new flag is actually rendered.
   * waitForResponse alone fires when headers arrive, but Vue still needs a
   * tick to assign flag.value and re-render. The most reliable signal is
   * that the flag image's `src` (the base64 SVG data URL) has actually changed.
   */
  async function advanceToNextFlag() {
    const oldSrc = (await page.locator('.flag-img').getAttribute('src')) ?? ''
    await page.locator('.result-btn').click()
    await expect(page.locator('.flag-img')).not.toHaveAttribute('src', oldSrc, {
      timeout: 5000,
    })
    await expect(page.locator('.result-strip')).toBeHidden()
  }

  // Try answers until we get one right to set up score > 0
  let gotCorrect = false
  for (let attempt = 0; attempt < 5 && !gotCorrect; attempt++) {
    await page.locator('.answer-btn').first().click()
    await expect(page.locator('.result-strip')).toBeVisible()
    gotCorrect = await page.locator('.result-strip.correct').isVisible()
    await advanceToNextFlag()
  }

  if (!gotCorrect) {
    test.skip(true, 'Could not get a correct answer in 5 attempts to set up prompt scenario')
  }

  // Now answer until wrong — first button is likely wrong since flag changed
  for (let i = 0; i < 4; i++) {
    await page.locator('.answer-btn').first().click()
    await expect(page.locator('.result-strip')).toBeVisible()
    if (await page.locator('.result-strip.wrong').isVisible()) break
    await advanceToNextFlag()
  }

  await expect(page.getByText('Save your high score!')).toBeVisible()
})

test('highscores modal opens for logged-in user and shows leaderboard', async ({ page }) => {
  // Sign up a fresh user
  const username = `e2e_hs_${Date.now()}`
  await page.getByRole('button', { name: 'Sign Up' }).click()
  await page.locator('#signup-username').fill(username)
  await page.locator('#signup-password').fill('password123')
  await page.getByRole('button', { name: 'Sign Up', exact: true }).last().click()
  await expect(page.locator('.username')).toBeVisible()

  await page.getByRole('button', { name: 'Highscores' }).click()
  await expect(page.getByText('Top Highscores')).toBeVisible()
})
