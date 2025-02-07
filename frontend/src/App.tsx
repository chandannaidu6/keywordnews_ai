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
} from "@mui/material";
import TextBox from "./components/TextBox";

type Article = {
  title: string;
  summary: string;
  url: string;
  source: string;
};

type SearchResponse = {
  keyword: string;
  articles: Article[];
};

const App = () => {
  const [articles, setArticles] = useState<Article[]>([]);

  const handleResults = (res: SearchResponse) => {
    setArticles(res.articles);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        // Example radial gradient:
        background: `
          radial-gradient(
            circle at 40% 40%,
            rgba(255, 203, 148, 0.7) 0%,
            rgba(255, 182, 193, 0.6) 40%,
            rgba(255, 168, 255, 0.4) 70%
          )
        `,
      }}
    >
      {/* Header / AppBar */}
      <AppBar
        position="static"
        sx={{
          background: "linear-gradient(90deg, #2196F3 0%, #21CBF3 100%)",
        }}
      >
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Keyword News
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="md" sx={{ mt: 4 }}>
        {/* Hero Section */}
        <Box textAlign="center" my={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Stay Informed
          </Typography>
          <Typography variant="h6" color="textSecondary">
            Discover the latest news articles by simply searching for a keyword.
          </Typography>
        </Box>

        {/* Search Component */}
        <TextBox onResults={handleResults} />

        {/* Articles Display */}
        <Box mt={4}>
          <Grid container spacing={4}>
            {articles.map((article, index) => (
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
};

export default App;
