class WebSocketService {
  private static instance: WebSocketService;
  private leaderboardWs: WebSocket | null = null;
  private scoreWs: WebSocket | null = null;

  private constructor() {}

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  connectToLeaderboard(quizId: string, onMessage: (data: any) => void) {
    if (this.leaderboardWs) {
      this.leaderboardWs.close();
    }

    this.leaderboardWs = new WebSocket(
      // `ws://localhost:8000/ws/leaderboard/${quizId}?token=${token}`
      `ws://localhost:8000/ws/leaderboard/quiz/${quizId}`
    );

    this.leaderboardWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.leaderboardWs.onerror = (error) => {
      console.error('Leaderboard WebSocket error:', error);
    };

    this.leaderboardWs.onclose = () => {
      console.log('Leaderboard WebSocket closed');
    };
  }

  connectToScore(quizId: string, userId: string) {
    if (this.scoreWs) {
      this.scoreWs.close();
    }

    this.scoreWs = new WebSocket(
      // `ws://localhost:8000/ws/score/${quizId}?token=${token}`
      `ws://localhost:8000/ws/quiz/${quizId}/user/${userId}`
    );

    this.scoreWs.onerror = (error) => {
      console.error('Score WebSocket error:', error);
    };

    this.scoreWs.onclose = () => {
      console.log('Score WebSocket closed');
    };
  }

  updateScore(score: number) {
    if (this.scoreWs && this.scoreWs.readyState === WebSocket.OPEN) {
      this.scoreWs.send(JSON.stringify({ score }));
    }
  }

  disconnect() {
    if (this.leaderboardWs) {
      this.leaderboardWs.close();
      this.leaderboardWs = null;
    }
    if (this.scoreWs) {
      this.scoreWs.close();
      this.scoreWs = null;
    }
  }
}

export const websocketService = WebSocketService.getInstance(); 