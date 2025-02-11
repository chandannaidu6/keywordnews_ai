"use client";

import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Skeleton,
  Avatar,
} from "@mui/material";
import TextBox, { SearchResponse } from "../../components/TextBox";
import { useSession } from "next-auth/react"; // Import useSession

type Article = {
  title: string;
  summary: string;
  url: string;
  source: string;
};

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false); // Loading state
  const { data: session } = useSession(); // Get user session

  const handleResults = (res: SearchResponse) => {
    setArticles(res.articles);
    setLoading(false); // Stop loading when results are received
  };

  const handleSearchStart = () => {
    setLoading(true); // Start loading when search begins
  };

  // Extract the first letter of the email
  const userEmail = session?.user?.email || "";
  const firstLetter = userEmail.charAt(0).toUpperCase();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: `radial-gradient(
          circle at 40% 40%,
          rgba(255, 203, 148, 0.7) 0%,
          rgba(255, 182, 193, 0.6) 40%,
          rgba(255, 168, 255, 0.4) 70%
        )`,
      }}
    >
      <AppBar
        position="static"
        sx={{ background: "linear-gradient(90deg, #2196F3 0%, #21CBF3 100%)" }}
      >
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Keyword News
          </Typography>
          {/* Display the first letter of the email in a circular Avatar */}
          {session?.user?.email && (
            <Avatar sx={{ bgcolor: "secondary.main" }}>{firstLetter}</Avatar>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box textAlign="center" my={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Stay Informed
          </Typography>
          <Typography variant="h6" color="textSecondary">
            Discover the latest news articles by simply searching for a keyword.
          </Typography>
        </Box>

        <TextBox onResults={handleResults} onSearchStart={handleSearchStart} />

        <Box mt={4}>
          <Grid container spacing={4}>
            {loading
              ? // Show skeleton loading while loading
                Array.from({ length: 4 }).map((_, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Card
                      sx={{
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Skeleton variant="text" width="80%" height={40} />
                        <Skeleton variant="text" width="100%" height={100} />
                      </CardContent>
                      <CardActions>
                        <Skeleton variant="rectangular" width={100} height={36} />
                      </CardActions>
                      <Box p={2}>
                        <Skeleton variant="text" width="60%" height={20} />
                      </Box>
                    </Card>
                  </Grid>
                ))
              : // Show actual articles when data is loaded
                articles.map((article, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Card
                      sx={{
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Typography gutterBottom variant="h5" component="h2">
                          {article.title}
                        </Typography>
                        <Typography>{article.summary}</Typography>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          color="primary"
                          href={article.url}
                          target="_blank"
                        >
                          Read More
                        </Button>
                      </CardActions>
                      <Box p={2}>
                        <Typography variant="caption" color="textSecondary">
                          Source: {article.source}
                        </Typography>
                      </Box>
                    </Card>
                  </Grid>
                ))}
          </Grid>
        </Box>
      </Container>
    </Box>
  );
}