new Vue({
  el: '#login',
  data: {
    username: '',
    status: ''
  },
  methods: {
    async authorizeUser() {
      if (!this.username) {
        this.status = 'Please enter your name.';
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/authorize/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: this.username })
        });

        if (!response.ok) {
          throw new Error('Authorization failed');
        }

        const data = await response.json();
        const userId = data.user_id;

        // Переходим на страницу с WebSocket
        window.location.href = `app.html?user_id=${userId}`;
      } catch (error) {
        this.status = `Error: ${error.message}`;
      }
    }
  }
});
