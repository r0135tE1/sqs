import { describe, expect, it } from "vitest";
import { ref } from "vue";
import { useModalTheme } from "../composables/useModalTheme";

describe("useModalTheme", () => {
  it("returns dark theme when isDark is true", () => {
    const t = useModalTheme(ref(true));
    expect(t.value.modal).toContain("slate-800");
    expect(t.value.textPrimary).toBe("text-slate-100");
    expect(t.value.input).toContain("slate-700");
    expect(t.value.errorBox).toContain("rose-900");
  });

  it("returns light theme when isDark is false", () => {
    const t = useModalTheme(ref(false));
    expect(t.value.modal).toContain("white");
    expect(t.value.textPrimary).toBe("text-gray-900");
    expect(t.value.input).toContain("bg-white");
    expect(t.value.errorBox).toContain("red-50");
  });

  it("is reactive — updates when isDark changes", () => {
    const isDark = ref(false);
    const t = useModalTheme(isDark);
    expect(t.value.modal).toContain("white");
    isDark.value = true;
    expect(t.value.modal).toContain("slate-800");
  });

  it("returns undefined isDark as light theme", () => {
    const t = useModalTheme(ref(undefined));
    expect(t.value.modal).toContain("white");
  });
});
