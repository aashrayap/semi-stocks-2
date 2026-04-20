import { expect, test } from '@playwright/test'

test('default Signal Desk surface renders data contract counts', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Signal Desk' })).toBeVisible()
  await expect(page.getByText('Contextual Evidence Graph')).toBeVisible()
  await expect(page.getByText('Graph = shared evidence, not relationship flow.')).toBeVisible()
  await expect(page.locator('.stat').filter({ hasText: 'Companies' })).toBeVisible()
  await expect(page.locator('.stat').filter({ hasText: 'Rows' })).toBeVisible()
  await page.screenshot({ path: 'test-results/signal-desk-default.png', fullPage: true })
})

test('source-channel filter and edge selection keep semantics visible', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: /Source Channel/ }).click()
  await page.getByLabel(/Baker/).check()
  await expect(page.getByText('Source: Baker')).toBeVisible()
  await page.locator('svg.graph line.edge').first().evaluate(element => {
    element.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  })
  await expect(page.getByText(/This edge reflects shared evidence/)).toBeVisible()
  await page.screenshot({ path: 'test-results/signal-desk-baker-edge.png', fullPage: true })
})

test('empty state explains graph filter collapse', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: /Filters/ }).click()
  await page.getByLabel(/Include undated/).uncheck()
  await page.getByLabel('From').fill('2035-01-01')
  await page.getByRole('textbox', { name: 'To' }).fill('2035-12-31')
  await expect(page.getByText('No graph edges under current settings.')).toBeVisible()
  await page.screenshot({ path: 'test-results/signal-desk-empty.png', fullPage: true })
})
