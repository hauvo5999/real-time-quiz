import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
  Chip,
  Alert,
} from '@mui/material';

interface QuizParams {
  quizId: string;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  score: number;
}

const QuizSession: React.FC = () => {
  const { quizId } = useParams<QuizParams>();
  const [username, setUsername] = useState('');
  const [isJoined, setIsJoined] = useState(false);
  const [answer, setAnswer] = useState('');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Join quiz session
  const handleJoin = () => {
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    // In a real app, you would validate with the server
    setIsJoined(true);
    connectWebSocket();
  };

  // Connect to WebSocket for real-time updates
  const connectWebSocket = () => {
    if (!quizId) return;

    const websocket = new WebSocket(
      `ws://localhost:8000/ws/leaderboard/${quizId}?username=${username}`
    );

    websocket.onopen = () => {
      console.log('Connected to quiz session');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'leaderboard') {
          setLeaderboard(data.data);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please try again.');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  };

  // Submit answer
  const handleSubmitAnswer = () => {
    if (!answer.trim()) {
      setError('Please enter your answer');
      return;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'answer',
        answer: answer.trim()
      }));
      setAnswer('');
    } else {
      setError('Connection lost. Please refresh the page.');
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  if (!isJoined) {
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            Join Quiz Session
          </Typography>
          <Stack spacing={3}>
            <TextField
              label="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              fullWidth
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleJoin}
              fullWidth
            >
              Join Quiz
            </Button>
          </Stack>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Stack spacing={4}>
        {/* Answer Section */}
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Submit Your Answer
          </Typography>
          <Stack direction="row" spacing={2}>
            <TextField
              label="Your answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              fullWidth
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmitAnswer}
              sx={{ minWidth: 120 }}
            >
              Submit
            </Button>
          </Stack>
        </Paper>

        {/* Leaderboard Section */}
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Live Leaderboard
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Rank</TableCell>
                  <TableCell>Player</TableCell>
                  <TableCell align="right">Score</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaderboard.map((entry) => (
                  <TableRow
                    key={entry.user_id}
                    sx={{
                      backgroundColor: entry.username === username ? 'action.hover' : 'inherit',
                    }}
                  >
                    <TableCell>{entry.rank}</TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Typography>{entry.username}</Typography>
                        {entry.username === username && (
                          <Chip
                            label="You"
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        )}
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">{entry.score}</Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
      </Stack>
    </Container>
  );
};

export default QuizSession; 