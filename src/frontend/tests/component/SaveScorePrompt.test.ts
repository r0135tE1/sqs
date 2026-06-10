import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SaveScorePrompt from '../../app/components/SaveScorePrompt.vue'

function findButtonByText(wrapper: ReturnType<typeof mount>, text: string) {
  const button = wrapper.findAll('button').find((b) => b.text() === text)
  if (!button) throw new Error(`Button "${text}" not found`)
  return button
}

describe('SaveScorePrompt', () => {
  it('does not render when isOpen is false', () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: false } })
    expect(wrapper.find('.modal').exists()).toBe(false)
  })

  it('renders the call-to-action when open', () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: true } })
    expect(wrapper.text()).toContain('Save your high score')
  })

  it('emits signup when "Sign Up" is clicked', async () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: true } })
    await findButtonByText(wrapper, 'Sign Up').trigger('click')
    expect(wrapper.emitted('signup')).toBeTruthy()
  })

  it('emits login when "Log in" is clicked', async () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: true } })
    await findButtonByText(wrapper, 'Log in').trigger('click')
    expect(wrapper.emitted('login')).toBeTruthy()
  })

  it('emits dismiss when "Continue without saving" is clicked', async () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: true } })
    await findButtonByText(wrapper, 'Continue without saving').trigger('click')
    expect(wrapper.emitted('dismiss')).toBeTruthy()
  })

  it('emits dismiss when the backdrop is clicked', async () => {
    const wrapper = mount(SaveScorePrompt, { props: { isOpen: true } })
    await wrapper.find('.modal').trigger('click')
    expect(wrapper.emitted('dismiss')).toBeTruthy()
  })
})
