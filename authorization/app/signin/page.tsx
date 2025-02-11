"use client";

import React, { useState, useEffect } from "react";
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
  Skeleton,
} from "@mui/material";

export default function SignIn() {
  const [csrfToken, setCsrfToken] = useState<string>("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(true); // Loading state for CSRF token
  const [isSubmitting, setIsSubmitting] = useState(false); // Loading state for form submission

  const router = useRouter();

  useEffect(() => {
    async function fetchToken() {
      const token = await getCsrfToken();
      setCsrfToken(token || "");
      setIsLoading(false); // Stop loading once token is fetched
    }
    fetchToken();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true); // Start loading for form submission
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
    setIsSubmitting(false); // Stop loading after submission
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 40% 40%, rgba(255,203,148,0.7) 0%, rgba(255,182,193,0.6) 40%, rgba(255,168,255,0.4) 70%)",
      }}
    >
      <AppBar position="static" sx={{ background: "#1976d2" }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Keyword News - Sign In
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
          {isLoading ? (
            // Skeleton loading for form fields
            <>
              <Skeleton variant="rectangular" height={56} />
              <Skeleton variant="rectangular" height={56} />
              <Skeleton variant="rectangular" height={36} width="100%" />
              <Skeleton variant="rectangular" height={36} width="100%" />
              <Skeleton variant="rectangular" height={36} width="100%" />
            </>
          ) : (
            // Actual form fields
            <>
              <TextField
                label="Email"
                variant="outlined"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
              />
              <TextField
                label="Password"
                variant="outlined"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Signing in..." : "Sign in with Email"}
              </Button>
              <Button
                variant="outlined"
                onClick={() => signIn("google", { callbackUrl: "/home" })}
                disabled={isSubmitting}
              >
                Sign in with Google
              </Button>
              <Button
                variant="outlined"
                onClick={() => signIn("github", { callbackUrl: "/home" })}
                disabled={isSubmitting}
              >
                Sign in with GitHub
              </Button>
              <Button
                variant="text"
                onClick={() => router.push("/signup")}
                disabled={isSubmitting}
              >
                Don&apos;t have an account? Sign Up
              </Button>
            </>
          )}
        </Box>
      </Container>
    </Box>
  );
}