"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  TextField,
  Button,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Skeleton,
} from "@mui/material";

export default function SignUp() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false); // Loading state for form submission

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true); // Start loading for form submission
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backendUrl) {
      alert("Backend URL not defined");
      return;
    }
    try {
      const res = await fetch(`${backendUrl}/api/auth/signup`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
        headers: { "Content-Type": "application/json" },
      });
      if (res.ok) {
        router.push("/signin");
      } else {
        const errorData = await res.json();
        alert("Signup failed: " + (errorData.detail || "Unknown error"));
      }
    } catch (err) {
      console.error("Error during signup:", err);
      alert("Signup failed: " + err);
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
            Keyword News - Sign Up
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          {isSubmitting ? (
            // Skeleton loading for form fields
            <>
              <Skeleton variant="rectangular" height={56} />
              <Skeleton variant="rectangular" height={56} />
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
                {isSubmitting ? "Signing up..." : "Sign Up"}
              </Button>
              <Button
                variant="text"
                onClick={() => router.push("/signin")}
                disabled={isSubmitting}
              >
                Already have an account? Sign In
              </Button>
            </>
          )}
        </Box>
      </Container>
    </Box>
  );
}