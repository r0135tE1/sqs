import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AuthModal from '../../app/components/AuthModal.vue'

describe('AuthModal', () => {
  it('renders "Welcome Back" title in login mode', () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'login' },
    })
    expect(wrapper.text()).toContain('Welcome Back')
    expect(wrapper.text()).not.toContain('Create Account')
  })

  it('renders "Create Account" title in signup mode', () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    expect(wrapper.text()).toContain('Create Account')
    expect(wrapper.text()).not.toContain('Welcome Back')
  })

  it('shows submit button labelled "Login" in login mode', () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'login' },
    })
    expect(wrapper.find('button[type="submit"]').text()).toBe('Login')
  })

  it('shows submit button labelled "Sign Up" in signup mode', () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    expect(wrapper.find('button[type="submit"]').text()).toBe('Sign Up')
  })

  it('shows external message prop in error box', () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'login', message: 'Invalid credentials' },
    })
    expect(wrapper.find('.error-box').exists()).toBe(true)
    expect(wrapper.find('.error-box').text()).toBe('Invalid credentials')
  })

  it('shows validation error for short username in signup mode', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    await wrapper.find('#signup-username').setValue('ab')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.find('.error-box').text()).toContain('at least 3 characters')
    expect(wrapper.emitted('submit')).toBeFalsy()
  })

  it('shows validation error for password without digit in signup mode', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('passwordonly')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.find('.error-box').text()).toContain('one number')
    expect(wrapper.emitted('submit')).toBeFalsy()
  })

  it('does not validate in login mode (sends any input through)', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'login' },
    })
    await wrapper.find('#login-username').setValue('a')
    await wrapper.find('#login-password').setValue('short')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')![0]).toEqual([{ username: 'a', password: 'short' }])
  })

  it('emits submit with form data on valid signup', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')![0]).toEqual([
      { username: 'marinus', password: 'password123' },
    ])
  })

  it('emits switch when footer link is clicked', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'login' },
    })
    await wrapper.find('.link').trigger('click')
    expect(wrapper.emitted('switch')).toBeTruthy()
  })

  it('resets form when modal closes', async () => {
    const wrapper = mount(AuthModal, {
      props: { isOpen: true, mode: 'signup' },
    })
    await wrapper.find('#signup-username').setValue('marinus')
    await wrapper.find('#signup-password').setValue('password123')

    await wrapper.setProps({ isOpen: false })
    await wrapper.setProps({ isOpen: true })

    expect((wrapper.find('#signup-username').element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('#signup-password').element as HTMLInputElement).value).toBe('')
  })
})
