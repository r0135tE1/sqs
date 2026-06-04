import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../../app/App.vue'
import { okJson, errJson, makeFetchMock, settle } from '../helpers/fetchMock'

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
    await settle(wrapper)

    await wrapper.findAll('button').find((b) => b.text() === 'Sign Up')!.trigger('click')
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle(wrapper)

    expect(wrapper.find('.error-box').text()).toContain('Username already taken')
    expect(localStorage.getItem('authToken')).toBeNull()
  })

  it('shows network error in signup form when fetch fails', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    // /auth/register handler that rejects (network failure)
    globalThis.fetch = vi.fn(async (url: string) => {
      if (url.includes('/auth/register')) throw new Error('Network')
      if (url.includes('/game/session')) return okJson({ session_id: 's1' }) as unknown as Response
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }) as unknown as Response
      return okJson({}) as unknown as Response
    }) as unknown as typeof fetch

    const wrapper = mount(App)
    await settle(wrapper)

    await wrapper.findAll('button').find((b) => b.text() === 'Sign Up')!.trigger('click')
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle(wrapper)

    expect(wrapper.find('.error-box').text()).toContain('Network error')
  })

  it('shows generic login error on non-401 backend response', async () => {
    const fetchMock = makeFetchMock()
    fetchMock.on('/game/session', okJson({ session_id: 's1' }))
    fetchMock.on('/game/flag', okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }))
    fetchMock.on('/auth/login', errJson(500, { detail: 'server boom' }))

    const wrapper = mount(App)
    await settle(wrapper)

    await wrapper.findAll('button').find((b) => b.text() === 'Log In')!.trigger('click')
    await wrapper.find('#login-username').setValue('marinus')
    await wrapper.find('#login-password').setValue('password123')
    await wrapper.find('form').trigger('submit')
    await settle(wrapper)

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
    globalThis.fetch = vi.fn(async (url: string) => {
      if (url.includes('/auth/login')) {
        loginCalls++
        // Slow login — never resolves so we can spam clicks
        return await new Promise<Response>(() => {})
      }
      if (url.includes('/game/session')) return okJson({ session_id: 's1' }) as unknown as Response
      if (url.includes('/game/flag')) return okJson({ question_id: 'q', flag_svg: '<svg></svg>', options: ['A', 'B', 'C', 'D'] }) as unknown as Response
      return okJson({}) as unknown as Response
    }) as unknown as typeof fetch

    const wrapper = mount(App)
    await settle(wrapper)

    await wrapper.findAll('button').find((b) => b.text() === 'Log In')!.trigger('click')
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
