import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HighscoresModal from '../../app/components/HighscoresModal.vue'
import { okJson, errJson, installFetchMock } from '../helpers/fetchMock'

describe('HighscoresModal', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('does not render when isOpen is false', () => {
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: false, token: 'fake-token' },
    })
    expect(wrapper.find('.modal').exists()).toBe(false)
  })

  it('shows spinner while loading', async () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.spinner').exists()).toBe(true)
    expect(wrapper.text()).toContain('Loading')
  })

  it('shows error state when fetch fails', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(errJson(500))
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    expect(wrapper.find('.spinner').exists()).toBe(false)
    expect(wrapper.text()).toContain('Failed to load highscores')
  })

  it('shows generic "Something went wrong" on unexpected error', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => { throw new SyntaxError('invalid JSON') },
    })
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('shows error on network exception', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network down'))
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Network error')
  })

  it('shows empty state when no highscores exist', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(okJson([]))
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('No highscores yet')
  })

  it('renders all entries with their scores', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      okJson([
        { username: 'alice', score: 50 },
        { username: 'bob', score: 30 },
        { username: 'carol', score: 10 },
      ])
    )
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    const rows = wrapper.findAll('.list-row')
    expect(rows).toHaveLength(3)
    expect(rows[0]?.text()).toContain('alice')
    expect(rows[0]?.text()).toContain('50')
    expect(rows[2]?.text()).toContain('carol')
  })

  it('applies rank-gold/silver/bronze classes to top 3', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      okJson([
        { username: 'first', score: 100 },
        { username: 'second', score: 50 },
        { username: 'third', score: 25 },
        { username: 'fourth', score: 10 },
      ])
    )
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    const ranks = wrapper.findAll('.rank')
    expect(ranks[0]?.classes()).toContain('rank-gold')
    expect(ranks[1]?.classes()).toContain('rank-silver')
    expect(ranks[2]?.classes()).toContain('rank-bronze')
    expect(ranks[3]?.classes()).toContain('rank-default')
  })

  it('emits close on backdrop click', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(okJson([]))
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: true, token: 'fake-token' },
    })
    await flushPromises()
    await wrapper.find('.modal-backdrop').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('refetches when isOpen transitions to true', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson([]))
    installFetchMock(fetchMock)
    const wrapper = mount(HighscoresModal, {
      props: { isOpen: false, token: 'fake-token' },
    })
    expect(fetchMock).not.toHaveBeenCalled()

    await wrapper.setProps({ isOpen: true })
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('sends Authorization header with token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson([]))
    installFetchMock(fetchMock)
    mount(HighscoresModal, {
      props: { isOpen: true, token: 'my-jwt-token' },
    })
    await flushPromises()
    const callArgs = fetchMock.mock.calls[0]
    expect(callArgs?.[1]?.headers?.Authorization).toBe('Bearer my-jwt-token')
  })
})
