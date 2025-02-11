// app/signin/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { signIn, getCsrfToken } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  TextField,
  Button,
} from "@mui/material";

export default function SignIn() {
  const [csrfToken, setCsrfToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function fetchCsrf() {
      const token = await getCsrfToken();
      setCsrfToken(token || "");
    }
    fetchCsrf();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const res = await signIn("credentials", {
      redirect: false,
      email,
      password,
      callbackUrl: "/home",
    });

    if (res?.error) {
      alert("Sign in failed: " + res.error);
    } else if (res?.url) {
      router.push(res.url);
    }
  };

  if (!csrfToken) return <div>Loading...</div>;

  return (
    <Box sx={{ minHeight: "100vh",
        background: `radial-gradient(
        circle at 40% 40%,
        rgba(255, 203, 148, 0.7) 0%,
        rgba(255, 182, 193, 0.6) 40%,
        rgba(255, 168, 255, 0.4) 70%
      )`, }}>
      <AppBar position="static" sx={{ background: "#1976d2" }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Keyword News - Sign In
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
          <TextField
            label="Email"
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" variant="contained" color="primary">
            Sign in with Email
          </Button>
          <Button variant="outlined" onClick={() => signIn("google", { callbackUrl: "/home" })}>
            Sign in with Google
          </Button>
          <Button variant="outlined" onClick={() => signIn("github", { callbackUrl: "/home" })}>
            Sign in with GitHub
          </Button>
          <Button variant="text" onClick={() => router.push("/signup")}>
          Don&apos;t have an account? Sign Up
          </Button>
        </Box>
      </Container>
    </Box>
  );
}
