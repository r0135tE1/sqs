import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
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

  it('emits close when the backdrop (dialog itself) is clicked', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    // A click whose target is the <dialog> element (its ::backdrop), not the content.
    await wrapper.find('.modal').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('does not emit close when the content is clicked', async () => {
    const wrapper = mount(BaseModal, {
      props: { isOpen: true },
      slots: { default: '<p class="inside">hi</p>' },
    })
    await wrapper.find('.inside').trigger('click')
    expect(wrapper.emitted('close')).toBeFalsy()
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
  // Modality, focus trapping, and Escape are provided natively by the <dialog>
  // element (via showModal); those are browser behaviours not exercisable under
  // jsdom, so the tests below cover the markup and event wiring we own.

  it('renders a native <dialog> element labelled by its title', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'Hello' } })
    const dialog = wrapper.find('.modal')
    expect((dialog.element as HTMLElement).tagName).toBe('DIALOG')
    const labelledby = dialog.attributes('aria-labelledby')
    expect(labelledby).toBeTruthy()
    expect(wrapper.find('.modal-title').attributes('id')).toBe(labelledby)
  })

  it('omits aria-labelledby when there is no title', () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true } })
    expect(wrapper.find('.modal').attributes('aria-labelledby')).toBeUndefined()
  })

  it('emits close on the native cancel event (Escape)', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    await wrapper.find('.modal').trigger('cancel')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emits close on the native close event', async () => {
    const wrapper = mount(BaseModal, { props: { isOpen: true, title: 'X' } })
    await wrapper.find('.modal').trigger('close')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
