import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useNotifications } from '../../app/composables/useNotifications'

describe('useNotifications', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Composable holds module-level state — clear it between tests
    const { notifications } = useNotifications()
    notifications.value = []
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('adds notifications with the correct type and message', () => {
    const notify = useNotifications()
    notify.success('saved!')
    notify.error('boom')
    notify.warning('careful')
    notify.highscore('🎉')

    expect(notify.notifications.value).toHaveLength(4)
    expect(notify.notifications.value[0]).toMatchObject({ type: 'success', message: 'saved!' })
    expect(notify.notifications.value[1]).toMatchObject({ type: 'error', message: 'boom' })
    expect(notify.notifications.value[2]).toMatchObject({ type: 'warning', message: 'careful' })
    expect(notify.notifications.value[3]).toMatchObject({ type: 'highscore', message: '🎉' })
  })

  it('auto-dismisses notifications after their default duration', () => {
    const notify = useNotifications()
    notify.success('hi')
    expect(notify.notifications.value).toHaveLength(1)

    vi.advanceTimersByTime(2500) // success default
    expect(notify.notifications.value).toHaveLength(0)
  })

  it('respects a custom duration', () => {
    const notify = useNotifications()
    notify.error('long-lived', 10_000)

    vi.advanceTimersByTime(5000)
    expect(notify.notifications.value).toHaveLength(1)

    vi.advanceTimersByTime(5000)
    expect(notify.notifications.value).toHaveLength(0)
  })

  it('dismiss() removes a notification by id', () => {
    const notify = useNotifications()
    const id = notify.success('hi')
    expect(notify.notifications.value).toHaveLength(1)

    notify.dismiss(id)
    expect(notify.notifications.value).toHaveLength(0)
  })

  it('dismiss() is a no-op for unknown ids', () => {
    const notify = useNotifications()
    notify.success('a')
    expect(notify.notifications.value).toHaveLength(1)

    notify.dismiss('unknown-id')
    expect(notify.notifications.value).toHaveLength(1)
  })

  it('dedupes by type+message and resets the existing timer', () => {
    const notify = useNotifications()
    const id1 = notify.error('Network down')

    vi.advanceTimersByTime(2000)

    // Same message again — should NOT add a second notification but reset timer
    const id2 = notify.error('Network down')
    expect(id2).toBe(id1)
    expect(notify.notifications.value).toHaveLength(1)

    // Original timer would have fired at 4000ms; reset at 2000 → new dismiss at 6000
    vi.advanceTimersByTime(2500) // total elapsed since reset: 2500, would have died if original timer
    expect(notify.notifications.value).toHaveLength(1)

    vi.advanceTimersByTime(2000) // total: 4500ms after reset, > 4000 default
    expect(notify.notifications.value).toHaveLength(0)
  })

  it('does NOT dedupe across different types with the same message', () => {
    const notify = useNotifications()
    notify.error('Saved')
    notify.success('Saved')
    expect(notify.notifications.value).toHaveLength(2)
  })

  it('persists when duration is 0 (no auto-dismiss)', () => {
    const notify = useNotifications()
    notify.error('forever', 0)
    vi.advanceTimersByTime(60_000)
    expect(notify.notifications.value).toHaveLength(1)
  })
})
