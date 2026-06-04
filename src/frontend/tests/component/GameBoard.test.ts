import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import GameBoard from '../../app/components/GameBoard.vue'
import { okJson } from '../helpers/fetchMock'

function mockHappyPath() {
  const fetchMock = vi.fn(async (url: string) => {
    if (url.endsWith('/game/session')) return okJson({ session_id: 'sess-123' })
    if (url.includes('/game/flag')) {
      return okJson({
        question_id: 'q-1',
        flag_svg: '<svg></svg>',
        options: ['Germany', 'France', 'Italy', 'Spain'],
      })
    }
    if (url.includes('/highscores/me')) return okJson({ score: 7 })
    if (url.endsWith('/game/answer')) {
      return okJson({ correct: true, score: 1, correct_answer: 'Germany' })
    }
    if (url.endsWith('/highscores/')) return okJson({ highscore: 7, is_new_best: false })
    return okJson({})
  })
  globalThis.fetch = fetchMock as unknown as typeof fetch
  return fetchMock
}

// Helper to fully mount and resolve all timers + promises (loadFlag has 200ms delay)
async function mountAndSettle(props: { token: string | null; username: string | null }) {
  const wrapper = mount(GameBoard, { props })
  await vi.runAllTimersAsync()
  await flushPromises()
  return wrapper
}

describe('GameBoard', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows skeleton while flag is loading', () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}))
    const wrapper = mount(GameBoard, { props: { token: null, username: null } })
    expect(wrapper.find('.skeleton-flag').exists()).toBe(true)
    expect(wrapper.findAll('.skeleton-button')).toHaveLength(4)
  })

  it('renders flag and answer buttons after loading', async () => {
    mockHappyPath()
    const wrapper = await mountAndSettle({ token: null, username: null })
    expect(wrapper.find('.flag-img').exists()).toBe(true)
    expect(wrapper.findAll('.answer-btn')).toHaveLength(4)
  })

  it('shows "Log in to track..." when user is anonymous', () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}))
    const wrapper = mount(GameBoard, { props: { token: null, username: null } })
    expect(wrapper.text()).toContain('Log in to track')
  })

  it('shows highscore label when user is authenticated', () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}))
    const wrapper = mount(GameBoard, {
      props: { token: 'fake-token', username: 'marinus' },
    })
    expect(wrapper.text()).toContain('Highscore')
    expect(wrapper.text()).not.toContain('Log in to track')
  })

  it('displays — for highscore when personalBest is null', () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}))
    const wrapper = mount(GameBoard, {
      props: { token: 'fake-token', username: 'marinus' },
    })
    expect(wrapper.text()).toContain('—')
  })

  it('emits session-expired when /highscores/me returns 401', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 'sess-1' })
      if (url.includes('/game/flag')) {
        return okJson({
          question_id: 'q-1',
          flag_svg: '<svg></svg>',
          options: ['A', 'B', 'C', 'D'],
        })
      }
      if (url.includes('/highscores/me')) {
        return { ok: false, status: 401, json: async () => ({}) }
      }
      return okJson({})
    })
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const wrapper = await mountAndSettle({
      token: 'expired-token',
      username: 'marinus',
    })
    expect(wrapper.emitted('session-expired')).toBeTruthy()
  })

  it('disables answer buttons after submitting', async () => {
    mockHappyPath()
    const wrapper = await mountAndSettle({ token: null, username: null })

    await wrapper.findAll('.answer-btn')[0]!.trigger('click')
    await flushPromises()

    const buttons = wrapper.findAll('.answer-btn')
    buttons.forEach((b) => {
      expect((b.element as HTMLButtonElement).disabled).toBe(true)
    })
  })

  it('shows correct result strip after correct answer', async () => {
    mockHappyPath()
    const wrapper = await mountAndSettle({ token: null, username: null })

    await wrapper.findAll('.answer-btn')[0]!.trigger('click')
    await flushPromises()

    expect(wrapper.find('.result-strip').exists()).toBe(true)
    expect(wrapper.find('.result-strip.correct').exists()).toBe(true)
    expect(wrapper.text()).toContain('Correct')
  })

  it('shows wrong result strip and correct answer when answer is wrong', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 'sess-1' })
      if (url.includes('/game/flag')) {
        return okJson({
          question_id: 'q-1',
          flag_svg: '<svg></svg>',
          options: ['A', 'B', 'C', 'D'],
        })
      }
      if (url.endsWith('/game/answer')) {
        return okJson({ correct: false, score: 0, correct_answer: 'A' })
      }
      return okJson({})
    })
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const wrapper = await mountAndSettle({ token: null, username: null })
    await wrapper.findAll('.answer-btn')[0]!.trigger('click')
    await flushPromises()

    expect(wrapper.find('.result-strip.wrong').exists()).toBe(true)
    expect(wrapper.text()).toContain('A')
  })

  it('marks correct answer green and selected wrong answer red after wrong submission', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 'sess-1' })
      if (url.includes('/game/flag')) {
        return okJson({
          question_id: 'q-1',
          flag_svg: '<svg></svg>',
          options: ['Germany', 'France', 'Italy', 'Spain'],
        })
      }
      if (url.endsWith('/game/answer')) {
        return okJson({ correct: false, score: 0, correct_answer: 'Germany' })
      }
      return okJson({})
    })
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const wrapper = await mountAndSettle({ token: null, username: null })
    // Click "France" (wrong); "Germany" is correct.
    const buttons = wrapper.findAll('.answer-btn')
    const franceBtn = buttons.find((b) => b.text() === 'France')!
    await franceBtn.trigger('click')
    await flushPromises()

    const germanyBtn = wrapper.findAll('.answer-btn').find((b) => b.text() === 'Germany')!
    expect(germanyBtn.classes()).toContain('correct')
    const franceAfter = wrapper.findAll('.answer-btn').find((b) => b.text() === 'France')!
    expect(franceAfter.classes()).toContain('wrong')
  })
})
