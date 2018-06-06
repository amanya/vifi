<script>
import Vue from 'vue'
import globalAxios from 'axios'
import { Line } from 'vue-chartjs'

export default {
  name: 'Chart',
  extends: Line,
  props: ['magnitudes'],
  data() {
    return {
      collectedMetrics: {},
      colors: ['#273B40', '#436871', '#6094A0', '#84B2BE', '#ADCCD3', '#D6E5E9']
    }
  },
  computed: {
    labels() {
      if (this.collectedMetrics[0]) {
        const labels = this.collectedMetrics[0].map(function(metric, idx) {
          return Date.parse(metric.timestamp)
        })
        return labels
      }
    }
  },
  methods: {
    fetchMetrics() {
      const authHeader = {
        Authorization: 'Bearer ' + localStorage.getItem('token')
      }
      const proms = this.magnitudes.map((m, idx) => {
        return globalAxios
          .get('/api/v1/magnitudes/' + m.id + '/metrics/', {
            headers: authHeader
          })
          .then(response => response.data)
          .then(data => {
            const propName = m.sensor_id + '-' + m.layer + '-' + m.type
            if (!this.collectedMetrics.hasOwnProperty(propName)) {
              Vue.set(this.collectedMetrics, propName, [])
            }
            this.collectedMetrics[propName] = this.collectedMetrics[propName].concat(data.metrics)
          })
          .catch(error => {
            console.log(error)
          })
      })
      return Promise.all(proms)
    },
    drawGraph() {
      this.collectedMetrics = []
      this.fetchMetrics()
        .then(() => {
          const datasets = Object.keys(this.collectedMetrics).map((k, idx) => {
            return {
              label: k,
              fill: false,
              backgroundColor: this.colors[idx],
              data: this.collectedMetrics[k]
                .map(metric => {
                  return {
                    x: Date.parse(metric.timestamp),
                    y: metric.value
                  }
                })
                .sort((a, b) => {
                  if (a.x < b.x) return -1
                  if (a.x > b.x) return 1
                  return 0
                })
            }
          })

          console.log(datasets)

          const data = {
            datasets: datasets
          }

          const options = {
            bounds: 'ticks',
            scales: {
              xAxes: [
                {
                  type: 'time',
                  distribution: 'linear'
                }
              ]
            },
            responsive: true,
            maintainAspectRatio: false
          }

          this.renderChart(data, options)
        })
        .catch(error => {
          console.log(error)
        })
    }
  },
  watch: {
    magnitudes: function(val) {
      this.drawGraph()
    }
  },
  mounted() {
    this.drawGraph()
  }
}
</script>
