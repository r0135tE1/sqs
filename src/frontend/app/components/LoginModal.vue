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
import { ref, computed } from "vue"

const props = defineProps<{ isOpen: boolean; message?: string; isDark?: boolean }>()
const emit = defineEmits(["close", "submit"])

const t = computed(() => props.isDark ? {
  modal:    "bg-slate-800 border-slate-700",
  textPrimary: "text-slate-100",
  label:    "text-slate-300",
  input:    "bg-slate-700 border-slate-600 text-slate-100 placeholder-slate-400",
  errorBox: "bg-rose-900/40 border-rose-700 text-rose-300",
  closeBtn: "text-slate-400 hover:text-slate-200",
} : {
  modal:    "bg-white border-gray-300",
  textPrimary: "text-gray-900",
  label:    "text-gray-700",
  input:    "bg-white border-gray-400 text-gray-900 placeholder-gray-400",
  errorBox: "bg-red-50 border-red-300 text-red-700",
  closeBtn: "text-gray-400 hover:text-gray-700",
})

const form = ref({ username: "", password: "" })

function submit() {
  emit("submit", form.value)
}
</script>
