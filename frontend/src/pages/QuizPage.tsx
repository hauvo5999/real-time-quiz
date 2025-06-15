import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Box, Button, Typography, Snackbar, Alert } from '@mui/material';
import Leaderboard from '../components/Leaderboard';

interface QuizParams {
  quizId: string;
}

const QuizPage: React.FC = () => {
  const { quizId } = useParams<QuizParams>();
  const [token, setToken] = useState<string>('');
  const [currentUserId, setCurrentUserId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get token and user ID from your auth system
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('userId');
    
    if (!storedToken || !storedUserId) {
      setError('Please log in to view the quiz');
      return;
    }

    setToken(storedToken);
    setCurrentUserId(storedUserId);
  }, []);

  // Simulate score updates (for testing)
  const simulateScoreUpdate = () => {
    if (!quizId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/score/${quizId}?token=${token}`);
    
    ws.onopen = () => {
      // Send random score between 0 and 100
      const randomScore = Math.floor(Math.random() * 100);
      ws.send(JSON.stringify({ score: randomScore }));
      ws.close();
    };

    ws.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      setError('Failed to update score');
    };
  };

  if (!token || !currentUserId || !quizId) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Quiz Session
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={simulateScoreUpdate}
          sx={{ mb: 2 }}
        >
          Simulate Score Update
        </Button>
      </Box>

      <Leaderboard
        quizId={quizId}
        token={token}
        currentUserId={currentUserId}
      />

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default QuizPage; 