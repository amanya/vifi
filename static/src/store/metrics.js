import globalAxios from 'axios'

const state = {
  metrics: {},
  selectedMagnitudes: {}
}

const getters = {
  getMetricsByLayer: state => magnitudes => {
    if (state.metrics) {
      const ids = magnitudes.map((magnitude, idx) => magnitude.id)
      return state.metrics.filter(metric => metric.magnitude_id.indexOf(ids) >= 0)
    }
  }
}

const mutations = {
  metricsFetch(state, sensorId, magnitudeId, metrics) {
    if (!metrics) {
      return
    }
    const parsedMetrics = []
    metrics.forEach(function(metric) {
      parsedMetrics.push({ timestamp: metric.timestamp, value: metric.value })
    })
    state.metrics[magnitudeId] = parsedMetrics
    state.selectedmagnitudes[sensorId][magnitudeId]['Surface'] = true
    state.selectedmagnitudes[sensorId][magnitudeId]['Depth 1'] = true
    state.selectedmagnitudes[sensorId][magnitudeId]['Depth 2'] = true
  },
  updateSelectedMagnitudes(state, sensorId, layer, selected) {
    this.selectedMagnitudes[sensorId][layer] = selected
  }
}

const actions = {
  metricsLoad({ commit, dispatch }, urls) {
    const authHeader = {
      Authorization: 'Bearer ' + localStorage.getItem('token')
    }
    urls.forEach(function(metricsUrl) {
      globalAxios
        .get(metricsUrl.url, { headers: authHeader })
        .then(response => response.data)
        .then(data => {
          commit('metricsFetch', {
            sensorId: metricsUrl.sensorId,
            magnitudId: metricsUrl.magnitudeId,
            metrics: data.metrics
          })
        })
        .catch(error => {
          console.log(error)
          commit('clearAuthData')
        })
    })
  }
}

export default {
  state,
  getters,
  mutations,
  actions
}
