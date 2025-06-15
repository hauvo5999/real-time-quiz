import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
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
} from '@mui/material'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech'
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium'

interface LeaderboardEntry {
  username: string
  score: number
  rank: number
}

interface QuizSessionProps {
  username: string
}

export function QuizSession({ username }: QuizSessionProps) {
  const [answer, setAnswer] = useState('')
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [error, setError] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket(`ws://localhost:8000/ws/quiz/1/leaderboard`)

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'leaderboard_update') {
          setLeaderboard(data.data)
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    ws.current.onerror = () => {
      setError('Failed to connect to the server')
    }

    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close()
      }
    }
  }, [])

  const handleSubmitAnswer = () => {
    if (!answer.trim()) return

    // Send answer to server
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'submit_answer',
        data: {
          answer: answer.trim(),
        },
      }))
      setAnswer('')
    } else {
      setError('Connection lost. Please refresh the page.')
    }
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <EmojiEventsIcon sx={{ color: 'gold' }} />
      case 2:
        return <MilitaryTechIcon sx={{ color: 'silver' }} />
      case 3:
        return <WorkspacePremiumIcon sx={{ color: '#cd7f32' }} />
      default:
        return null
    }
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Stack spacing={4}>
          {/* Answer Submission */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Submit Your Answer
            </Typography>
            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                label="Your Answer"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmitAnswer()}
              />
              <Button
                variant="contained"
                onClick={handleSubmitAnswer}
                disabled={!answer.trim()}
              >
                Submit
              </Button>
            </Stack>
          </Paper>

          {/* Leaderboard */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Live Leaderboard
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Username</TableCell>
                    <TableCell align="right">Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaderboard.map((entry) => (
                    <TableRow
                      key={entry.username}
                      sx={{
                        backgroundColor:
                          entry.username === username ? 'action.hover' : 'inherit',
                      }}
                    >
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          {getRankIcon(entry.rank)}
                          <Typography>{entry.rank}</Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          {entry.username}
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
                      <TableCell align="right">{entry.score}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
        </Stack>
      </Box>
    </Container>
  )
} 