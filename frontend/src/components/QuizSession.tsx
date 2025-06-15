import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Box,
  Typography,
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
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  CircularProgress,
  Snackbar,
  Divider,
} from '@mui/material'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech'
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import CelebrationIcon from '@mui/icons-material/Celebration'

interface LeaderboardEntry {
  username: string
  score: number
  rank: number
}

interface Answer {
  id: string
  text: string
}

interface Question {
  id: string
  text: string
  time_limit: number
  answers: Answer[]
}

interface QuizSessionProps {
  username: string
  quizId: string
}

interface Notification {
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

export function QuizSession({ username, quizId }: QuizSessionProps) {
  const [answer, setAnswer] = useState('')
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [error, setError] = useState<string | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<string>('')
  const [timeLeft, setTimeLeft] = useState<number>(0)
  const [notification, setNotification] = useState<Notification | null>(null)
  const [isQuizComplete, setIsQuizComplete] = useState(false)
  const [userScore, setUserScore] = useState(0)
  const [userRank, setUserRank] = useState<number | null>(null)
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket with username
    ws.current = new WebSocket(`ws://localhost:8000/ws/quiz/${quizId}?username=${encodeURIComponent(username)}`)

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'leaderboard_update') {
          setLeaderboard(data.data)
          // Update user's score and rank
          const userEntry = data.data.find((entry: LeaderboardEntry) => entry.username === username)
          if (userEntry) {
            setUserScore(userEntry.score)
            setUserRank(userEntry.rank)
          }
        } else if (data.type === 'question') {
          setCurrentQuestion(data.data)
          setTimeLeft(data.data.time_limit)
          setSelectedAnswer('')
        } else if (data.type === 'answer_result') {
          // Show notification for answer result
          setNotification({
            message: data.data.message,
            type: data.data.correct ? 'success' : 'error',
            duration: 2000  // Reduced duration to make it less intrusive
          })
          
          // Move to next question after a short delay
          setTimeout(() => {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
              ws.current.send(JSON.stringify({
                type: 'request_next_question'
              }))
            }
          }, 1000)  // Wait 1 second before requesting next question
        } else if (data.type === 'quiz_complete') {
          setIsQuizComplete(true)
          setNotification({
            message: data.data.message,
            type: 'info',
            duration: 5000
          })
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
  }, [quizId, username])

  // Timer effect
  useEffect(() => {
    if (!timeLeft || !currentQuestion) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          handleSubmitAnswer()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [timeLeft, currentQuestion])

  const handleSubmitAnswer = () => {
    if (!selectedAnswer || !currentQuestion) return

    // Send answer to server
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      console.log('Sending answer to server:', {
        question_id: currentQuestion.id,
        answer_id: selectedAnswer
      })
      ws.current.send(JSON.stringify({
        type: 'submit_answer',
        data: {
          question_id: currentQuestion.id,
          answer_id: selectedAnswer
        },
      }))
      setSelectedAnswer('')
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

  const getCompletionMessage = () => {
    if (!userRank) return "Quiz completed!"
    
    switch (userRank) {
      case 1:
        return "Congratulations! You're the winner! 🏆"
      case 2:
        return "Great job! You came in second place! 🥈"
      case 3:
        return "Well done! You came in third place! 🥉"
      default:
        return `Quiz completed! You finished in ${userRank}th place!`
    }
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Stack spacing={4}>
          {/* Current Question or Quiz Completion */}
          {!isQuizComplete ? (
            currentQuestion ? (
              <Paper elevation={3} sx={{ p: 3 }}>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h5">Current Question</Typography>
                    <Chip
                      label={`Time Left: ${timeLeft}s`}
                      color={timeLeft <= 10 ? 'error' : 'primary'}
                      icon={timeLeft <= 10 ? <CircularProgress size={20} color="inherit" /> : undefined}
                    />
                  </Box>
                  <Typography variant="body1">{currentQuestion.text}</Typography>
                  <FormControl component="fieldset">
                    <FormLabel component="legend">Select your answer:</FormLabel>
                    <RadioGroup
                      value={selectedAnswer}
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                    >
                      {currentQuestion.answers.map((answer) => (
                        <FormControlLabel
                          key={answer.id}
                          value={answer.id}
                          control={<Radio />}
                          label={answer.text}
                        />
                      ))}
                    </RadioGroup>
                  </FormControl>
                  <Button
                    variant="contained"
                    onClick={handleSubmitAnswer}
                    disabled={!selectedAnswer}
                    fullWidth
                  >
                    Submit Answer
                  </Button>
                </Stack>
              </Paper>
            ) : null
          ) : (
            <Paper elevation={3} sx={{ p: 4 }}>
              <Stack spacing={3} alignItems="center">
                <CelebrationIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                <Typography variant="h4" color="primary" align="center">
                  You completed the quiz!
                </Typography>
                <Divider sx={{ width: '100%' }} />
                <Stack spacing={2} sx={{ width: '100%', maxWidth: 400 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Your Score:</Typography>
                    <Typography variant="h4" color="primary.main">{userScore}</Typography>
                  </Box>
                </Stack>
              </Stack>
            </Paper>
          )}

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
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getRankIcon(entry.rank)}
                          {entry.rank}
                        </Box>
                      </TableCell>
                      <TableCell>{entry.username}</TableCell>
                      <TableCell align="right">{entry.score}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Stack>
      </Box>

      {/* Notifications */}
      <Snackbar
        open={!!notification}
        autoHideDuration={notification?.duration || 3000}
        onClose={() => setNotification(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setNotification(null)}
          severity={notification?.type || 'info'}
          icon={notification?.type === 'success' ? <CheckCircleIcon /> : notification?.type === 'error' ? <CancelIcon /> : undefined}
          sx={{ width: '100%' }}
        >
          {notification?.message}
        </Alert>
      </Snackbar>

      {/* Error Alert */}
      {error && (
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      )}
    </Container>
  )
}
