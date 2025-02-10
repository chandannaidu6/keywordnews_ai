import React from "react";
import { signIn, getCsrfToken } from "next-auth/react";
import { GetServerSideProps } from "next";

interface SignInProps {
  csrfToken?: string;
}

export default function SignIn({ csrfToken="" }: SignInProps) {
  return (
    <div>
      <h1>Sign In</h1>
      <form method="post" action="/api/auth/callback/credentials">
        <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
        <label>
          Email:
          <input name="email" type="text" />
        </label>
        <br />
        <label>
          Password:
          <input name="password" type="password" />
        </label>
        <br />
        <button type="submit">Sign in with Email</button>
      </form>
      <hr />
      <button onClick={() => signIn("google", { callbackUrl: "http://localhost:3000" })}>
        Sign in with Google
      </button>
      <button onClick={() => signIn("github", { callbackUrl: "http://localhost:3000" })}>
        Sign in with GitHub
      </button>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const csrfToken = await getCsrfToken(context);
  return {
    props: { csrfToken },
  };
};
