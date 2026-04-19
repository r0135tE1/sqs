import { describe, expect, it } from "vitest";
import { API_URL } from "../config";

describe("API_URL", () => {
  it("defaults to localhost:8000", () => {
    expect(API_URL).toBe("http://localhost:8000");
  });

  it("is a non-empty string", () => {
    expect(typeof API_URL).toBe("string");
    expect(API_URL.length).toBeGreaterThan(0);
  });
});
