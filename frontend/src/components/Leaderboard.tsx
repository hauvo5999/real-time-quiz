import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
  Stack,
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech';
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  score: number;
}

interface LeaderboardProps {
  quizId: string;
  token: string;
  currentUserId: string;
}

interface WebSocketMessage {
  type: string;
  data: LeaderboardEntry[];
}

const Leaderboard: React.FC<LeaderboardProps> = ({ quizId, token, currentUserId }) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const websocket = new WebSocket(
      `ws://localhost:8000/ws/leaderboard/${quizId}?token=${token}`
    );

    websocket.onopen = () => {
      console.log('Connected to leaderboard WebSocket');
    };

    websocket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        if (data.type === 'leaderboard') {
          setLeaderboard(data.data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('Disconnected from leaderboard WebSocket');
    };

    setWs(websocket);

    // Cleanup on unmount
    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close();
      }
    };
  }, [quizId, token]);

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <EmojiEventsIcon sx={{ color: 'gold' }} />;
      case 2:
        return <MilitaryTechIcon sx={{ color: 'silver' }} />;
      case 3:
        return <WorkspacePremiumIcon sx={{ color: '#cd7f32' }} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto', p: 2 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" align="center" gutterBottom>
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
                    backgroundColor: entry.user_id === currentUserId ? 'action.hover' : 'inherit',
                    '&:hover': { backgroundColor: 'action.hover' },
                  }}
                >
                  <TableCell>
                    <Stack direction="row" spacing={1} alignItems="center">
                      {entry.rank <= 3 ? (
                        getRankIcon(entry.rank)
                      ) : (
                        <Typography>{entry.rank}</Typography>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography>{entry.username}</Typography>
                      {entry.user_id === currentUserId && (
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
    </Box>
  );
};

export default Leaderboard; 