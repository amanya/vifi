<script>
import Vue from 'vue'
import globalAxios from 'axios'
import { Line } from 'vue-chartjs'
import { mapState } from 'vuex'

export default {
  name: 'Chart',
  extends: Line,
  props: ['magnitudes'],
  data() {
    return {
      collectedMetrics: {},
      colors: [
        'hsl(171, 100%, 41%)',
        'hsl(204, 86%, 53%)',
        'hsl(217, 71%, 53%)',
        'hsl(141, 71%, 48%)',
        'hsl(48, 100%, 67%)',
        'hsl(348, 100%, 61%)'
      ]
    }
  },
  computed: {
    ...mapState({
      token: state => state.auth.idToken
    }),
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
        Authorization: 'Bearer ' + this.token
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
              borderColor: this.colors[idx],
              borderWidth: 1,
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
