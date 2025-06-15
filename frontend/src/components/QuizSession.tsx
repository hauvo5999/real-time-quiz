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
  useTheme,
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

export default function QuizSession({ username, quizId }: QuizSessionProps) {
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

  const theme = useTheme()

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
              <Paper
                elevation={4}
                sx={{
                  p: 4,
                  background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
                  borderRadius: 3,
                }}
              >
                <Stack spacing={3}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography 
                      variant="h5" 
                      sx={{ 
                        fontWeight: 600,
                        color: theme.palette.primary.main,
                      }}
                    >
                      Current Question
                    </Typography>
                    <Chip
                      label={`Time Left: ${timeLeft}s`}
                      color={timeLeft <= 10 ? 'error' : 'primary'}
                      icon={timeLeft <= 10 ? <CircularProgress size={20} color="inherit" /> : undefined}
                      sx={{
                        fontWeight: 600,
                        boxShadow: timeLeft <= 10 ? '0 0 10px rgba(211, 47, 47, 0.3)' : 'none',
                      }}
                    />
                  </Box>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontSize: '1.1rem',
                      lineHeight: 1.6,
                      color: theme.palette.text.primary,
                    }}
                  >
                    {currentQuestion.text}
                  </Typography>
                  <FormControl component="fieldset">
                    <FormLabel 
                      component="legend"
                      sx={{ 
                        color: theme.palette.primary.main,
                        fontWeight: 600,
                        mb: 2,
                      }}
                    >
                      Select your answer:
                    </FormLabel>
                    <RadioGroup
                      value={selectedAnswer}
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                    >
                      {currentQuestion.answers.map((answer) => (
                        <FormControlLabel
                          key={answer.id}
                          value={answer.id}
                          control={
                            <Radio 
                              sx={{
                                '&.Mui-checked': {
                                  color: theme.palette.primary.main,
                                },
                              }}
                            />
                          }
                          label={answer.text}
                          sx={{
                            mb: 1,
                            p: 1,
                            borderRadius: 1,
                            transition: 'all 0.2s',
                            '&:hover': {
                              backgroundColor: 'rgba(33, 150, 243, 0.04)',
                            },
                          }}
                        />
                      ))}
                    </RadioGroup>
                  </FormControl>
                  <Button
                    variant="contained"
                    onClick={handleSubmitAnswer}
                    disabled={!selectedAnswer}
                    fullWidth
                    size="large"
                    sx={{
                      background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
                      boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                      fontWeight: 600,
                      py: 1.5,
                      '&:hover': {
                        background: 'linear-gradient(45deg, #1976d2 30%, #1E88E5 90%)',
                      },
                    }}
                  >
                    Submit Answer
                  </Button>
                </Stack>
              </Paper>
            ) : null
          ) : (
            <Paper
              elevation={4}
              sx={{
                p: 5,
                textAlign: 'center',
                background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
                borderRadius: 3,
              }}
            >
              <Stack spacing={4} alignItems="center">
                <CelebrationIcon 
                  sx={{ 
                    fontSize: 80,
                    color: theme.palette.primary.main,
                    filter: 'drop-shadow(0 0 10px rgba(33, 150, 243, 0.3))',
                  }} 
                />
                <Typography 
                  variant="h4" 
                  sx={{ 
                    fontWeight: 600,
                    background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
                    backgroundClip: 'text',
                    textFillColor: 'transparent',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Quiz completed!
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: theme.palette.text.secondary,
                    fontWeight: 500,
                  }}
                >
                  Your Score: {userScore}
                </Typography>
              </Stack>
            </Paper>
          )}

          {/* Leaderboard */}
          <Paper
            elevation={4}
            sx={{
              p: 3,
              background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
              borderRadius: 3,
            }}
          >
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 2,
                fontWeight: 600,
                color: theme.palette.primary.main,
              }}
            >
              Leaderboard
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Rank</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Player</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaderboard.map((entry) => (
                    <TableRow
                      key={entry.username}
                      sx={{
                        backgroundColor: entry.username === username ? 'rgba(33, 150, 243, 0.08)' : 'inherit',
                        '&:hover': {
                          backgroundColor: 'rgba(33, 150, 243, 0.04)',
                        },
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
            variant="filled"
            sx={{
              width: '100%',
              boxShadow: '0 3px 5px 2px rgba(0, 0, 0, 0.1)',
            }}
          >
            {notification?.message}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  )
}
