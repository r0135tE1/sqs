import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../../app/App.vue'
import { okJson, errJson, makeFetchMock, settle as settleApp, installFetchMock, findButtonByText } from '../helpers/fetchMock'

describe('App integration flows', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    localStorage.clear()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('signs up a new user and shows them as logged in', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({
      question_id: 'q-1',
      flag_svg: '<svg></svg>',
      options: ['A', 'B', 'C', 'D'],
    }))
    fetchMock.on('/auth/register', okJson({}))
    fetchMock.on('/auth/login', okJson({ access_token: 'jwt-token' }))
    fetchMock.on('/highscores/me', okJson({ score: 0 }))

    const wrapper = mount(App)
    await settleApp(wrapper)

    expect(wrapper.text()).not.toContain('marinus')

    // Open sign-up modal
    await findButtonByText(wrapper, 'Sign Up').trigger('click')

    // Fill and submit form
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settleApp(wrapper)

    // After successful signup → login → token stored, username in nav
    expect(localStorage.getItem('authToken')).toBe('jwt-token')
    expect(localStorage.getItem('username')).toBe('marinus')
    expect(wrapper.find('.username').text()).toBe('marinus')
  })

  it('shows an error message when login fails', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({
      question_id: 'q-1',
      flag_svg: '<svg></svg>',
      options: ['A', 'B', 'C', 'D'],
    }))
    fetchMock.on('/auth/login', errJson(401, { detail: 'wrong password' }))

    const wrapper = mount(App)
    await settleApp(wrapper)

    await findButtonByText(wrapper, 'Log In').trigger('click')
    await wrapper.find('#login-username').setValue('marinus')
    await wrapper.find('#login-password').setValue('wrongpassword')
    await wrapper.find('form').trigger('submit')
    await settleApp(wrapper)

    expect(wrapper.find('.error-box').text()).toContain('Invalid username or password')
    expect(localStorage.getItem('authToken')).toBeNull()
  })

  it('shows login prompt to anonymous user after a wrong answer with score > 0', async () => {
    const fetchMock = makeFetchMock()
    let answerCallCount = 0

    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({
      question_id: 'q-1',
      flag_svg: '<svg></svg>',
      options: ['Germany', 'France', 'Italy', 'Spain'],
    }))
    fetchMock.onMatching((url) => {
      if (!url.endsWith('/game/answer')) return null
      answerCallCount++
      // First answer correct (streak = 1), second answer wrong.
      return answerCallCount === 1
        ? okJson({ correct: true, score: 1, correct_answer: 'Germany' })
        : okJson({ correct: false, score: 0, correct_answer: 'Germany' })
    })

    const wrapper = mount(App)
    await settleApp(wrapper)

    // Correct answer
    await wrapper.find('.answer-btn').trigger('click')
    await settleApp(wrapper)
    // Click "Next" to dismiss result strip
    await wrapper.find('.result-btn').trigger('click')
    await settleApp(wrapper)

    // Wrong answer
    await wrapper.find('.answer-btn').trigger('click')
    await settleApp(wrapper)

    // Login prompt should appear
    expect(wrapper.text()).toContain('Save your high score')
  })

  it('clears game state and shows logged-out UI after logout', async () => {
    localStorage.setItem('authToken', 'existing-token')
    localStorage.setItem('username', 'marinus')

    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({
      question_id: 'q-1',
      flag_svg: '<svg></svg>',
      options: ['A', 'B', 'C', 'D'],
    }))
    fetchMock.on('/highscores/me', okJson({ score: 42 }))

    const wrapper = mount(App)
    await settleApp(wrapper)

    expect(wrapper.text()).toContain('marinus')

    await findButtonByText(wrapper, 'Logout').trigger('click')
    await settleApp(wrapper)

    expect(localStorage.getItem('authToken')).toBeNull()
    expect(localStorage.getItem('username')).toBeNull()
    expect(wrapper.text()).not.toContain('marinus')
    expect(wrapper.text()).toContain('Log in to save your scores')
  })

  it('shows a "new highscore" toast after the backend reports a new best', async () => {
    localStorage.setItem('authToken', 'existing-token')
    localStorage.setItem('username', 'marinus')

    const fetchMock = makeFetchMock()
    let answerCallCount = 0

    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({
      question_id: 'q-1',
      flag_svg: '<svg></svg>',
      options: ['Germany', 'France', 'Italy', 'Spain'],
    }))
    // POST /highscores/ — register before /highscores/me so /me wins on substring
    fetchMock.on('/highscores/', okJson({ highscore: 1, is_new_best: true }))
    fetchMock.on('/highscores/me', okJson({ score: 0 }))
    fetchMock.onMatching((url) => {
      if (!url.endsWith('/game/answer')) return null
      answerCallCount++
      return answerCallCount === 1
        ? okJson({ correct: true, score: 1, correct_answer: 'Germany' })
        : okJson({ correct: false, score: 0, correct_answer: 'Germany' })
    })

    const wrapper = mount(App)
    await settleApp(wrapper)

    // Correct
    await wrapper.find('.answer-btn').trigger('click')
    await settleApp(wrapper)
    await wrapper.find('.result-btn').trigger('click')
    await settleApp(wrapper)
    // Wrong → triggers save. Use plain flushPromises so the 3s toast-timeout
    // doesn't get advanced — it would clear the message before we assert.
    await wrapper.find('.answer-btn').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('New high score')
  })
})
