import { useState } from 'react'
import { Container, Box, Typography, TextField, Button, Paper } from '@mui/material'
import { QuizSession } from './components/QuizSession'

function App() {
  const [username, setUsername] = useState('')
  const [quizId, setQuizId] = useState('')
  const [isJoined, setIsJoined] = useState(false)

  const handleJoin = () => {
    if (username.trim() && quizId.trim()) {
      setIsJoined(true)
    }
  }

  if (!isJoined) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <Typography variant="h4" component="h1" align="center" gutterBottom>
              Welcome to Quiz App
            </Typography>
            <TextField
              fullWidth
              label="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
            />
            <TextField
              fullWidth
              label="Enter Quiz ID"
              value={quizId}
              onChange={(e) => setQuizId(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
            />
            <Button
              fullWidth
              variant="contained"
              onClick={handleJoin}
              disabled={!username.trim() || !quizId.trim()}
            >
              Join Quiz
            </Button>
          </Paper>
        </Box>
      </Container>
    )
  }

  return <QuizSession username={username} quizId={quizId} />
}

export default App
