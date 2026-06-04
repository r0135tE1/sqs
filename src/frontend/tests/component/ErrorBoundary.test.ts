import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent, onMounted, h } from 'vue'
import ErrorBoundary from '../../app/components/ErrorBoundary.vue'

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // onErrorCaptured logs via console.error — silence it for clean test output
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders the default slot when no error occurs', () => {
    const wrapper = mount(ErrorBoundary, {
      slots: { default: '<div class="child">child content</div>' },
    })
    expect(wrapper.find('.child').exists()).toBe(true)
    expect(wrapper.find('.error-fallback').exists()).toBe(false)
  })

  it('shows the fallback UI when a child component throws', async () => {
    const Throwing = defineComponent({
      setup() {
        onMounted(() => {
          throw new Error('boom')
        })
        return () => h('div')
      },
    })

    const wrapper = mount(ErrorBoundary, {
      slots: { default: () => h(Throwing) },
    })

    await flushPromises()

    expect(wrapper.find('.error-fallback').exists()).toBe(true)
    expect(wrapper.text()).toContain('Something went wrong')
    expect(wrapper.find('button.btn').text()).toBe('Try again')
  })

  it('resets the error state when "Try again" is clicked', async () => {
    let shouldThrow = true
    const ConditionalThrower = defineComponent({
      setup() {
        onMounted(() => {
          if (shouldThrow) throw new Error('boom')
        })
        return () => h('div', { class: 'child-was-here' })
      },
    })

    const wrapper = mount(ErrorBoundary, {
      slots: { default: () => h(ConditionalThrower) },
    })

    await flushPromises()
    expect(wrapper.find('.error-fallback').exists()).toBe(true)

    // Disable the throw so the next mount succeeds
    shouldThrow = false
    await wrapper.find('button.btn').trigger('click')
    await flushPromises()

    // After reset, the slot is rendered again successfully
    expect(wrapper.find('.error-fallback').exists()).toBe(false)
    expect(wrapper.find('.child-was-here').exists()).toBe(true)
  })
})
