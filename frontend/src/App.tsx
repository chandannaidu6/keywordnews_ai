// App.tsx
import React, { useState } from 'react';
import TextBox from './components/TextBox';
type Article = {
  title:string;
  summary:string;
  url:string;
  source:string;
}

type SearchResponse={
  keyword:string;
  articles:Article[];
};
const App = () => {
  const [articles,setArticles] = useState<Article[]>([]);

  const handleResults = (res:SearchResponse) => {
    setArticles(res.articles)
  }

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Keywordnews</h1>
      <TextBox onResults={handleResults} />
      <div>
        {articles.map((article, index) => (
          <div key={index} style={{ margin: '10px', textAlign: 'left' }}>
            <h3>{article.title}</h3>
            <p>{article.summary}</p>
            <a href={article.url} target="_blank" rel="noopener noreferrer">
              Read more
            </a>
            <p style={{ fontStyle: 'italic' }}>Source: {article.source}</p>
          </div>
        ))}
      </div>

    </div>
  );
};

export default App;
