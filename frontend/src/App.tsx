import { useState } from 'react'
import { Container, Box, Typography, TextField, Button, Paper, ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar, Avatar } from '@mui/material'
import QuizSession from './components/QuizSession'
import SchoolIcon from '@mui/icons-material/School'

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#f50057',
      light: '#ff4081',
      dark: '#c51162',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      color: '#1a237e',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 24px',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '&:hover fieldset': {
              borderColor: '#2196f3',
            },
          },
        },
      },
    },
  },
})

function App() {
  const [username, setUsername] = useState('')
  const [quizId, setQuizId] = useState('')
  const [isJoined, setIsJoined] = useState(false)

  const handleJoin = () => {
    if (username.trim() && quizId.trim()) {
      setIsJoined(true)
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar 
          position="static" 
          sx={{ 
            background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
            boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
          }}
        >
          <Toolbar>
            <SchoolIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Vocabulary Quiz App
            </Typography>
            {isJoined && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar 
                  sx={{ 
                    bgcolor: 'white',
                    color: theme.palette.primary.main,
                    fontWeight: 600,
                  }}
                >
                  {username.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                  {username}
                </Typography>
              </Box>
            )}
          </Toolbar>
        </AppBar>

        <Box sx={{ flexGrow: 1 }}>
          {!isJoined ? (
            <Container maxWidth="sm">
              <Box
                sx={{
                  minHeight: 'calc(100vh - 64px)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: 3,
                  py: 4,
                }}
              >
                <Paper
                  elevation={4}
                  sx={{
                    p: 5,
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 3,
                    background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
                    borderRadius: 3,
                  }}
                >
                  <Typography 
                    variant="h4" 
                    component="h1" 
                    align="center" 
                    gutterBottom
                    sx={{
                      background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
                      backgroundClip: 'text',
                      textFillColor: 'transparent',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      mb: 3,
                    }}
                  >
                    Welcome to Quiz App
                  </Typography>
                  <TextField
                    fullWidth
                    label="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Enter Quiz ID"
                    value={quizId}
                    onChange={(e) => setQuizId(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleJoin()}
                    variant="outlined"
                    sx={{ mb: 3 }}
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleJoin}
                    disabled={!username.trim() || !quizId.trim()}
                    size="large"
                    sx={{
                      background: 'linear-gradient(45deg, #2196f3 30%, #21CBF3 90%)',
                      boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #1976d2 30%, #1E88E5 90%)',
                      },
                    }}
                  >
                    Join Quiz
                  </Button>
                </Paper>
              </Box>
            </Container>
          ) : (
            <QuizSession username={username} quizId={quizId} />
          )}
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App
