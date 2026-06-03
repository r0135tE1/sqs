import { test, expect } from '@playwright/test'

/**
 * Auth round-trip: register, auto-login, then reload and verify the session
 * survives.
 *
 * This is the one E2E test that's genuinely irreplaceable by integration tests —
 * it proves:
 *   - the JWT issued by the backend can actually be persisted in localStorage
 *   - the persisted token is picked up correctly on next page load
 *   - the backend recognizes the same token after a fresh request
 *
 * Mocks would give us false confidence here: they'd happily return whatever
 * token we want and accept anything on reload.
 */
test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
  await page.reload()
})

test('register, auto-login, and persist session across reload', async ({ page }) => {
  // Unique username so the test is repeatable without DB cleanup
  const username = `e2e_${Date.now()}_${Math.floor(Math.random() * 1000)}`
  const password = 'password123'

  // Step 1: open sign-up modal
  await page.getByRole('button', { name: 'Sign Up' }).click()
  await expect(page.getByText('Create Account')).toBeVisible()

  // Step 2: fill and submit
  await page.locator('#signup-username').fill(username)
  await page.locator('#signup-password').fill(password)
  // The form has its own "Sign Up" submit button; use the one inside the form
  await page.locator('form').getByRole('button', { name: 'Sign Up' }).click()

  // Step 3: after signup, backend auto-logs in → nav shows the username
  await expect(page.locator('.username')).toHaveText(username, { timeout: 10_000 })
  await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible()

  // Step 4: a token should be stored
  const tokenAfterLogin = await page.evaluate(() => localStorage.getItem('authToken'))
  expect(tokenAfterLogin).toBeTruthy()
  expect(tokenAfterLogin!.length).toBeGreaterThan(20) // sanity check it's an actual JWT

  // Step 5: reload the page and check the user is still logged in
  await page.reload()
  await expect(page.locator('.username')).toHaveText(username, { timeout: 10_000 })

  // Step 6: the backend should still accept the token. The Highscores button
  // is only shown when authenticated AND clicking it triggers a backend call.
  await page.getByRole('button', { name: 'Highscores' }).click()
  await expect(page.getByText('Top Highscores')).toBeVisible()

  // Step 7: logout clears state and persists the cleared state
  await page.getByRole('button', { name: '×', exact: true }).click() // close highscores modal
  await page.getByRole('button', { name: 'Logout' }).click()

  await expect(page.getByText('Log in to save your scores')).toBeVisible()
  const tokenAfterLogout = await page.evaluate(() => localStorage.getItem('authToken'))
  expect(tokenAfterLogout).toBeNull()
})
