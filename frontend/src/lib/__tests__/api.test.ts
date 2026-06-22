import { describe, it, expect } from "vitest";
import { AxiosError } from "axios";
import { extractErrorMessage } from "../api";

describe("extractErrorMessage", () => {
  it("extracts the FastAPI 'detail' field when present", () => {
    const error = new AxiosError("Request failed");
    error.response = {
      data: { detail: "Incorrect email or password." },
      status: 401,
      statusText: "Unauthorized",
      headers: {},
      config: {} as never,
    };
    expect(extractErrorMessage(error)).toBe("Incorrect email or password.");
  });

  it("falls back to a session-expired message for a 401 with no detail", () => {
    const error = new AxiosError("Request failed");
    error.response = {
      data: {},
      status: 401,
      statusText: "Unauthorized",
      headers: {},
      config: {} as never,
    };
    expect(extractErrorMessage(error)).toMatch(/session has expired/i);
  });

  it("returns a network message when there is no response at all", () => {
    const error = new AxiosError("Network Error");
    error.response = undefined;
    expect(extractErrorMessage(error)).toMatch(/could not reach the server/i);
  });

  it("returns a generic message for non-axios errors", () => {
    expect(extractErrorMessage(new Error("boom"))).toBe("Something went wrong. Please try again.");
  });
});
