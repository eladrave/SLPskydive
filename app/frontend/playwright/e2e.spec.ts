import { test, expect } from '@playwright/test'

test('placeholder e2e', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await expect(page).toHaveTitle(/SLPskydive/)
})
