import React from "react";
import { getCsrfToken } from "next-auth/react";
import SignInClient from "./SignInClient";

export default async function SignInPage() {
  const csrfToken = await getCsrfToken();
  return <SignInClient csrfToken={csrfToken || ""} />;
}
