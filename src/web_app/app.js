new Vue({
  el: '#app',
  data: {
    ws: null,
    message: '',
    messages: [],
    demonstrationMessages: [],
    stockDataExample: null,
    status: 'Disconnected',
    wsUrl: 'ws://localhost:8000/connect/websocket/{user_id}/{device_id}/',
    userId: new URLSearchParams(window.location.search).get('user_id'),
    selectedInterval: '',
    requestStatus: '',
    unknownMessages: []
  },
  methods: {
    connectWebSocket() {
      this.status = 'Connecting...';
      const deviceId = this.generateUUID();
      const urlWithUserIdAndDeviceId = this.wsUrl.replace('{user_id}', this.userId).replace('{device_id}', deviceId);
      this.ws = new WebSocket(urlWithUserIdAndDeviceId);

      this.ws.onopen = () => {
        this.status = 'Connected';
        console.log('WebSocket connection opened');
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data) {
          if (data.actual_data) {
            this.handleStockData(data.actual_data);
          }
          if (data.demonstration_data) {
            this.handleDemonstrationData(data.demonstration_data);
          }
          if (data.stock_data_example) {
            this.handleStockDataExample(data.stock_data_example);
          }
          if (data.aggregation_result) {
            this.handleAggregationResult(data.aggregation_result);
          }
        }
      };

      this.ws.onclose = () => {
        this.status = 'Disconnected';
        console.log('WebSocket connection closed');
      };

      this.ws.onerror = (error) => {
        this.status = 'Error';
        console.error('WebSocket error:', error);
      };
    },
    sendMessage() {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(this.message);
        this.message = ''; // Clear input after sending
      } else {
        console.warn('WebSocket is not connected.');
      }
    },
    generateUUID() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    },
    handleStockData(stockData) {
      this.messages = stockData.map(stock => ({
        ticker: stock.ticker,
        volume: stock.results[0].v,
        avgPrice: stock.results[0].vw,
        openPrice: stock.results[0].o,
        closePrice: stock.results[0].c,
        highPrice: stock.results[0].h,
        lowPrice: stock.results[0].l,
        timestamp: new Date(stock.results[0].t).toLocaleTimeString()
      }));
    },
    handleDemonstrationData(demoData) {
      this.demonstrationMessages = demoData.map(stock => ({
        ticker: stock.ticker,
        volume: stock.results[0].v,
        avgPrice: stock.results[0].vw,
        openPrice: stock.results[0].o,
        closePrice: stock.results[0].c,
        highPrice: stock.results[0].h,
        lowPrice: stock.results[0].l,
        timestamp: new Date(stock.results[0].t).toLocaleTimeString()
      }));
    },
    handleStockDataExample(stockDataExample) {
      this.stockDataExample = {
        stock_id: stockDataExample.stock_id,
        name: stockDataExample.name,
        company_name: stockDataExample.company_name
      };
    },
    handleUnknownMessages(message) {
      this.unknownMessages.push(message);
    },
    handleAggregationResult(aggregationResult) {
      if (!aggregationResult.length) {
        this.requestStatus = 'No data available for the selected interval.';
        return;
      }

      // Prepare data
      const timestamps = aggregationResult.map(item => new Date(item.start_timestamp));
      const labels = timestamps.map(date => date.toISOString());
      const closingPrices = aggregationResult.map(item => item.closing_price);
      const openingPrices = aggregationResult.map(item => item.opening_price);
      const maxPrices = aggregationResult.map(item => item.max_highest_price);
      const minPrices = aggregationResult.map(item => item.min_lowest_price);

      // Determine time unit
      const minTimeDiff = Math.min(...timestamps.slice(1).map((date, i) => date - timestamps[i]));

      let timeUnit = 'minute';
      if (minTimeDiff >= 86400000) { // 1 day in milliseconds
        timeUnit = 'day';
      } else if (minTimeDiff >= 3600000) { // 1 hour in milliseconds
        timeUnit = 'hour';
      }

      const data = {
        labels: labels,
        datasets: [
          {
            label: 'Closing Price',
            data: closingPrices,
            borderColor: '#FF5733',
            backgroundColor: 'rgba(255, 87, 51, 0.2)',
            fill: false,
            tension: 0.1
          },
          {
            label: 'Opening Price',
            data: openingPrices,
            borderColor: '#33FF57',
            backgroundColor: 'rgba(51, 255, 87, 0.2)',
            fill: false,
            tension: 0.1
          },
          {
            label: 'Max Price',
            data: maxPrices,
            borderColor: '#3377FF',
            backgroundColor: 'rgba(51, 119, 255, 0.2)',
            fill: false,
            tension: 0.1
          },
          {
            label: 'Min Price',
            data: minPrices,
            borderColor: '#FF33A2',
            backgroundColor: 'rgba(255, 51, 162, 0.2)',
            fill: false,
            tension: 0.1
          }
        ]
      };

      this.updateChart(data, timeUnit);
    },
    updateChart(data, timeUnit) {
      if (this.chart) {
        this.chart.data = data;
        this.chart.update();
      } else {
        const ctx = document.getElementById('stockChart').getContext('2d');
        this.chart = new Chart(ctx, {
          type: 'line',
          data: data,
          options: {
            responsive: true,
            scales: {
              x: {
                beginAtZero: false,
                title: {
                  display: true,
                  text: 'Time'
                },
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 20
                },
                time: {
                  unit: timeUnit,
                  displayFormats: {
                    day: 'MMM D',
                    hour: 'hA',
                    minute: 'h:mm A'
                  }
                }
              },
              y: {
                beginAtZero: false,
                title: {
                  display: true,
                  text: 'Price'
                },
                ticks: {
                  callback: function(value) {
                    return value.toFixed(2);
                  }
                }
              }
            },
            plugins: {
              legend: {
                display: true,
                position: 'top'
              },
              tooltip: {
                callbacks: {
                  label: function(tooltipItem) {
                    return tooltipItem.dataset.label + ': ' + tooltipItem.raw.toFixed(2);
                  }
                }
              }
            }
          }
        });
      }
    },
    requestAggregation() {
      if (this.ws && this.ws.readyState === WebSocket.OPEN && this.stockDataExample && this.selectedInterval) {
        const request = {
          action: 'aggregate_data',
          aggregation_params: {
            stock_id: this.stockDataExample.stock_id,
            interval: this.selectedInterval,
            user_id: this.userId
          }
        };
        this.ws.send(JSON.stringify(request));
        this.requestStatus = 'Запрос отправлен';

        // Clear request status after 2 seconds
        setTimeout(() => {
          this.requestStatus = '';
        }, 2000);
      } else {
        this.requestStatus = 'Please select an interval and ensure WebSocket is connected.';
      }
    }
  },
  created() {
    this.connectWebSocket();
  }
});
