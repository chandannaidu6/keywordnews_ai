import React, { useState, ChangeEvent } from "react";
import { TextField, Button, Box } from "@mui/material";

export interface SearchResponse {
  keyword: string;
  articles: {
    title: string;
    summary: string;
    url: string;
    source: string;
  }[];
}

interface TextBoxProps {
  onResults?: (response: SearchResponse) => void;
  onSearchStart?: () => void; // Add this prop
}

export default function TextBox({ onResults, onSearchStart }: TextBoxProps) {
  const [keyword, setKeyword] = useState("");

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setKeyword(e.target.value);
  };

  async function callBackendAPI(inputKeyword: string) {
    if (onSearchStart) {
      onSearchStart(); // Notify parent that search has started
    }

    try {
      const response = await fetch(`https://chandannaidu0606--backend-fastapi-app-web.modal.run/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: inputKeyword }),
      });

      if (!response.ok) {
        console.error("Backend returned an error", response.statusText);
        return;
      }

      const data = (await response.json()) as SearchResponse;
      console.info("Received data from the backend", data);
      if (onResults) {
        onResults(data);
      }
    } catch (err) {
      console.error("Error calling the backend", err);
    }
  }

  const handleClick = () => {
    const trimmedKeyword = keyword.trim();
    if (trimmedKeyword) {
      callBackendAPI(trimmedKeyword);
    }
  };

  return (
    <Box display="flex" alignItems="center" justifyContent="center" gap={2} mt={2}>
      <TextField
        label="Search Keyword"
        variant="outlined"
        value={keyword}
        onChange={handleChange}
        sx={{ width: 300 }}
      />
      <Button variant="contained" color="primary" onClick={handleClick}>
        Search
      </Button>
    </Box>
  );
}