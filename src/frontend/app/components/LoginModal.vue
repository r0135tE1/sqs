<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center z-50 px-4">
    <div class="absolute inset-0 bg-black/60 z-40" @click="$emit('close')" />
    <div :class="['relative rounded-2xl p-8 w-full max-w-md z-50 shadow-2xl border transition-colors duration-300', t.modal]">

      <div class="flex justify-between items-center mb-6">
        <div :class="['text-2xl font-bold', t.textPrimary]">Welcome Back</div>
        <button @click="$emit('close')" :class="['text-2xl leading-none transition-colors cursor-pointer', t.closeBtn]">×</button>
      </div>

      <div v-if="message" :class="['mb-5 p-3 rounded-lg text-sm border', t.errorBox]">
        {{ message }}
      </div>

      <form @submit.prevent="submit" class="flex flex-col gap-4">
        <div>
          <label for="login-username" :class="['block text-sm font-medium mb-1.5', t.label]">Username</label>
          <input id="login-username" v-model="form.username" type="text" placeholder="Enter your username" autocomplete="username"
                 :class="['w-full rounded-lg px-4 py-3 text-sm border outline-none transition-colors focus:ring-2 focus:ring-sky-500 focus:border-transparent', t.input]"
                 required />
        </div>
        <div>
          <label for="login-password" :class="['block text-sm font-medium mb-1.5', t.label]">Password</label>
          <input id="login-password" v-model="form.password" type="password" placeholder="Enter your password" autocomplete="current-password"
                 :class="['w-full rounded-lg px-4 py-3 text-sm border outline-none transition-colors focus:ring-2 focus:ring-sky-500 focus:border-transparent', t.input]"
                 required />
        </div>
        <button type="submit" class="w-full bg-sky-600 text-white py-3 rounded-lg hover:bg-sky-700 transition-colors font-semibold mt-1">
          Login
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, toRef } from "vue"
import { useModalTheme } from "../composables/useModalTheme"

const props = defineProps<{ isOpen: boolean; message?: string; isDark?: boolean }>()
const emit = defineEmits(["close", "submit"])

const t = useModalTheme(toRef(props, "isDark"))

const form = ref({ username: "", password: "" })

function submit() {
  emit("submit", form.value)
}
</script>
