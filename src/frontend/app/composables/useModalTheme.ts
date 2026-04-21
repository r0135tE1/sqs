import { computed, type Ref } from "vue";

export function useModalTheme(isDark: Ref<boolean | undefined>) {
  return computed(() => isDark.value ? {
    modal:       "bg-slate-800 border-slate-700",
    textPrimary: "text-slate-100",
    label:       "text-slate-300",
    input:       "bg-slate-700 border-slate-600 text-slate-100 placeholder-slate-400",
    errorBox:    "bg-rose-900/40 border-rose-700 text-rose-300",
    closeBtn:    "text-slate-400 hover:text-slate-200",
  } : {
    modal:       "bg-white border-gray-300",
    textPrimary: "text-gray-900",
    label:       "text-gray-700",
    input:       "bg-white border-gray-400 text-gray-900 placeholder-gray-400",
    errorBox:    "bg-red-50 border-red-300 text-red-700",
    closeBtn:    "text-gray-400 hover:text-gray-700",
  });
}
