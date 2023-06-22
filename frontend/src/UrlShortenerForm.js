import React, { useState } from 'react';
import './UrlShortenerForm.css';

const UrlShortenerForm = () => {
    const [url, setUrl] = useState('');
    const [expiration, setExpiration] = useState('');
    const [shortenedUrl, setShortenedUrl] = useState('');
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      console.log("submit!!!!!!!")
      try {
        const response = await fetch('http://34.202.83.150:8080/api/shorten', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url,
            expiration,
          }),
        });
        console.log("try to call API")
        const data = await response.json();
        console.log(data)
        // Assuming the response contains a property named "shortUrl"
        setShortenedUrl(data.shortUrl);
      } catch (error) {
        console.error('Error:', error);
      }
    };
  
    return (
      <div className="url-shortener-container">
        <h2>URL Shortener</h2>
        <form className="url-shortener-form" onSubmit={handleSubmit}>
          <label>
            URL:
            <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} />
          </label>
          <br />
          <label>
            Expiration Time:
            <input type="text" value={expiration} onChange={(e) => setExpiration(e.target.value)} />
          </label>
          <br />
          <button type="submit">Shorten URL</button>
        </form>
        {shortenedUrl && (
          <div className="shortened-url-container">
            <h3>Shortened URL:</h3>
            <a href={shortenedUrl} target="_blank" rel="noopener noreferrer">
              {shortenedUrl}
            </a>
          </div>
        )}
      </div>
    );
  };
  
  export default UrlShortenerForm;