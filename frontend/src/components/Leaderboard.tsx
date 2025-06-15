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
  useTheme,
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
  const theme = useTheme();

  useEffect(() => {
    // Connect to WebSocket
    const websocket = new WebSocket(
    //   `ws://localhost:8000/ws/leaderboard/quiz/${quizId}?token=${token}`
      `ws://localhost:8000/ws/leaderboard/quiz/${quizId}`
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
      <Paper
        elevation={4}
        sx={{
          p: 4,
          background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
          borderRadius: 3,
        }}
      >
        <Typography 
          variant="h4" 
          align="center" 
          gutterBottom
          sx={{
            fontWeight: 600,
            background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
            backgroundClip: 'text',
            textFillColor: 'transparent',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 3,
          }}
        >
          Live Leaderboard
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600, color: theme.palette.primary.main }}>Rank</TableCell>
                <TableCell sx={{ fontWeight: 600, color: theme.palette.primary.main }}>Player</TableCell>
                <TableCell align="right" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leaderboard.map((entry) => (
                <TableRow
                  key={entry.user_id}
                  sx={{
                    backgroundColor: entry.user_id === currentUserId ? 'rgba(33, 150, 243, 0.08)' : 'inherit',
                    '&:hover': {
                      backgroundColor: 'rgba(33, 150, 243, 0.04)',
                    },
                  }}
                >
                  <TableCell>
                    <Stack direction="row" spacing={1} alignItems="center">
                      {entry.rank <= 3 ? (
                        <Box sx={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          filter: 'drop-shadow(0 0 5px rgba(0, 0, 0, 0.2))',
                        }}>
                          {getRankIcon(entry.rank)}
                        </Box>
                      ) : (
                        <Typography 
                          sx={{ 
                            fontWeight: 600,
                            color: theme.palette.text.secondary,
                          }}
                        >
                          {entry.rank}
                        </Typography>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography 
                        sx={{ 
                          fontWeight: entry.user_id === currentUserId ? 600 : 400,
                          color: entry.user_id === currentUserId ? theme.palette.primary.main : 'inherit',
                        }}
                      >
                        {entry.username}
                      </Typography>
                      {entry.user_id === currentUserId && (
                        <Chip
                          label="You"
                          size="small"
                          color="primary"
                          sx={{
                            fontWeight: 600,
                            boxShadow: '0 2px 4px rgba(33, 150, 243, 0.2)',
                          }}
                        />
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    <Typography 
                      sx={{ 
                        fontWeight: 600,
                        color: entry.rank <= 3 ? theme.palette.primary.main : 'inherit',
                      }}
                    >
                      {entry.score}
                    </Typography>
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