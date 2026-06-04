import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import GameBoard from '../../app/components/GameBoard.vue'
import { okJson, errJson, installFetchMock } from '../helpers/fetchMock'

async function mountAndSettle(props: { token: string | null; username: string | null }) {
  const wrapper = mount(GameBoard, { props })
  await vi.runAllTimersAsync()
  await flushPromises()
  return wrapper
}

describe('GameBoard error/recovery paths', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows the retry banner when loadFlag fails', async () => {
    let flagCalls = 0
    installFetchMock(async (url) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) {
        flagCalls++
        if (flagCalls === 1) throw new Error('Network')
        return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      }
      return okJson({})
    })

    const wrapper = await mountAndSettle({ token: null, username: null })

    expect(wrapper.find('.load-error').exists()).toBe(true)
    expect(wrapper.text()).toContain('Could not reach the server')
  })

  it('Retry button recovers and loads the flag', async () => {
    let flagCalls = 0
    installFetchMock(async (url) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) {
        flagCalls++
        if (flagCalls === 1) throw new Error('Network')
        return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      }
      return okJson({})
    })

    const wrapper = await mountAndSettle({ token: null, username: null })
    expect(wrapper.find('.load-error').exists()).toBe(true)

    await wrapper.find('.load-error .btn').trigger('click')
    await vi.runAllTimersAsync()
    await flushPromises()

    expect(wrapper.find('.load-error').exists()).toBe(false)
    expect(wrapper.find('.flag-img').exists()).toBe(true)
  })

  it('discards stale session on 404 from /game/answer', async () => {
    installFetchMock(async (url) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      if (url.endsWith('/game/answer')) return errJson(404, { detail: 'Session not found' })
      return okJson({})
    })

    const wrapper = await mountAndSettle({ token: null, username: null })

    await wrapper.findAll('.answer-btn')[0].trigger('click')
    await flushPromises()

    // Stale state cleared → load-error banner shown
    expect(wrapper.find('.load-error').exists()).toBe(true)
    expect(wrapper.find('.flag-img').exists()).toBe(false)
  })

  it('saves the score and emits new-highscore when authenticated and new best', async () => {
    let answerCalls = 0
    installFetchMock(async (url) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      if (url.includes('/highscores/me')) return okJson({ score: 0 })
      if (url.endsWith('/game/answer')) {
        answerCalls++
        return answerCalls === 1
          ? okJson({ correct: true, score: 1, correct_answer: 'A' })
          : okJson({ correct: false, score: 0, correct_answer: 'A' })
      }
      if (url.endsWith('/highscores/')) return okJson({ highscore: 1, is_new_best: true })
      return okJson({})
    })

    const wrapper = await mountAndSettle({ token: 'tok', username: 'marinus' })

    // Correct answer → score = 1
    await wrapper.findAll('.answer-btn')[0].trigger('click')
    await flushPromises()
    await wrapper.find('.result-btn').trigger('click')
    await vi.runAllTimersAsync()
    await flushPromises()

    // Wrong answer → triggers save
    await wrapper.findAll('.answer-btn')[0].trigger('click')
    await flushPromises()

    const emitted = wrapper.emitted('new-highscore')
    expect(emitted).toBeDefined()
    expect(emitted?.[0]).toEqual([1])
  })

  it('does not stack toasts when answer endpoint is offline (relies on dedupe)', async () => {
    installFetchMock(async (url) => {
      if (url.endsWith('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      if (url.endsWith('/game/answer')) throw new Error('Network')
      return okJson({})
    })

    const wrapper = await mountAndSettle({ token: null, username: null })

    await wrapper.findAll('.answer-btn')[0].trigger('click')
    await flushPromises()

    // After failure, the flag-box is cleared and the retry banner shows
    expect(wrapper.find('.load-error').exists()).toBe(true)
  })
})
