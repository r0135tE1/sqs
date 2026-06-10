import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import BaseModal from '../../app/components/BaseModal.vue'

describe('BaseModal', () => {
  it('does not render when isOpen is false', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: false } })
    expect(wrapper.find('.modal').exists()).toBe(false)
  })

  it('renders when isOpen is true', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true } })
    expect(wrapper.find('.modal').exists()).toBe(true)
  })

  it('renders the title when provided', () => {
    const wrapper = mount(BaseModal, {
      props: { isOpen: true, title: 'Hello World' },
    })
    expect(wrapper.text()).toContain('Hello World')
    expect(wrapper.find('.close-btn').exists()).toBe(true)
  })

  it('does not render header when title is omitted', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true } })
    expect(wrapper.find('.modal-header').exists()).toBe(false)
    expect(wrapper.find('.close-btn').exists()).toBe(false)
  })

  it('emits close when backdrop is clicked', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    await wrapper.find('.modal-backdrop').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close when close button is clicked', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    await wrapper.find('.close-btn').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('renders slot content', () => {
    const wrapper = mount(BaseModal, {
      props: { isOpen: true },
      slots: { default: '<p class="custom">slot content</p>' },
    })
    expect(wrapper.find('.custom').exists()).toBe(true)
    expect(wrapper.find('.custom').text()).toBe('slot content')
  })

  // ── Accessibility ─────────────────────────────────────────────

  it('exposes dialog ARIA attributes and labels the title', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'Hello' } })
    const dialog = wrapper.find('.modal')
    expect(dialog.attributes('role')).toBe('dialog')
    expect(dialog.attributes('aria-modal')).toBe('true')
    const labelledby = dialog.attributes('aria-labelledby')
    expect(labelledby).toBeTruthy()
    expect(wrapper.find('.modal-title').attributes('id')).toBe(labelledby)
  })

  it('omits aria-labelledby when there is no title', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true } })
    expect(wrapper.find('.modal').attributes('aria-labelledby')).toBeUndefined()
  })

  it('emits close when Escape is pressed', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    await wrapper.find('.modal').trigger('keydown', { key: 'Escape' })
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('moves focus into the dialog when it opens', async () => {
    const wrapper = mount(BaseModal, {
      props: { isOpen: false, title: 'X' },
      attachTo: document.body,
    })
    await wrapper.setProps({ isOpen: true })
    await flushPromises()
    expect(document.activeElement).toBe(wrapper.find('.modal').element)
    wrapper.unmount()
  })

  it('traps Tab focus within the dialog', async () => {
    const wrapper = mount(BaseModal, {
      props: { isOpen: true, title: 'X' },
      slots: { default: '<button class="last-btn">Last</button>' },
      attachTo: document.body,
    })

    const closeBtn = wrapper.find('.close-btn').element as HTMLButtonElement
    const lastBtn = wrapper.find('.last-btn').element as HTMLButtonElement

    // Tab from the last focusable wraps back to the first (close button).
    lastBtn.focus()
    await wrapper.find('.modal').trigger('keydown', { key: 'Tab' })
    expect(document.activeElement).toBe(closeBtn)

    // Shift+Tab from the first focusable wraps to the last.
    closeBtn.focus()
    await wrapper.find('.modal').trigger('keydown', { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(lastBtn)

    wrapper.unmount()
  })
})
