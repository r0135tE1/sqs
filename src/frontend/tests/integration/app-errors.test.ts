import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../../app/App.vue'
import { okJson, errJson, makeFetchMock, settle, installFetchMock, findButtonByText } from '../helpers/fetchMock'

describe('App error and edge-case flows', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    localStorage.clear()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('shows username-taken error on signup conflict', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    fetchMock.on('/auth/register', errJson(409, { detail: 'taken' }))

    const wrapper = mount(App)
    await settle()

    await findButtonByText(wrapper, 'Sign Up').trigger('click')
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle()

    expect(wrapper.find('.error-box').text()).toContain('Username already taken')
    expect(localStorage.getItem('authToken')).toBeNull()
  })

  it('shows network error in signup form when fetch fails', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    // /auth/register handler that rejects (network failure)
    installFetchMock(async (url) => {
      if (url.includes('/auth/register')) throw new Error('Network')
      if (url.includes('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      return okJson({})
    })

    const wrapper = mount(App)
    await settle()

    await findButtonByText(wrapper, 'Sign Up').trigger('click')
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle()

    expect(wrapper.find('.error-box').text()).toContain('Network error')
  })

  it('shows generic login error on non-401 backend response', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    fetchMock.on('/auth/login', errJson(500, { detail: 'server boom' }))

    const wrapper = mount(App)
    await settle()

    await findButtonByText(wrapper, 'Log In').trigger('click')
    await wrapper.find('#login-username').setValue('marinus')
    await wrapper.find('#login-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle()

    expect(wrapper.find('.error-box').text()).toContain('server boom')
  })

  it('shows session-expired warning toast when GameBoard emits 401', async () => {
    localStorage.setItem('authToken', 'expired-token')
    localStorage.setItem('username', 'marinus')

    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    fetchMock.on('/highscores/me', errJson(401))

    const wrapper = mount(App)
    // Use plain flushPromises so the 4-second toast-dismiss timer doesn't fire
    // and clear the message before we assert.
    for (let i = 0; i < 5; i++) await flushPromises()

    expect(wrapper.text()).toContain('Session expired')
    expect(localStorage.getItem('authToken')).toBeNull()
  })

  it('prevents double-submit on the login form', async () => {
    let loginCalls = 0
    installFetchMock(async (url) => {
      if (url.includes('/auth/login')) {
        loginCalls++
        // Slow login — never resolves so we can spam clicks
        return await new Promise<Response>(() => {})
      }
      if (url.includes('/game/session')) return okJson({ session_id: 's1' })
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] })
      return okJson({})
    })

    const wrapper = mount(App)
    await settle()

    await findButtonByText(wrapper, 'Log In').trigger('click')
    await wrapper.find('#login-username').setValue('marinus')
    await wrapper.find('#login-password').setValue('password123')

    // Submit three times rapidly
    await wrapper.find('form').trigger('submit')
    await wrapper.find('form').trigger('submit')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    // Only one in-flight call despite three submits
    expect(loginCalls).toBe(1)
  })
})
