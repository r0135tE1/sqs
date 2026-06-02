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
})
