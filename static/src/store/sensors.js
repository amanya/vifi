import globalAxios from 'axios'

const state = {
  sensors: []
}

const mutations = {
  sensorsFetch(state, sensors) {
    state.sensors.concat(state.sensors, sensors)
  }
}

const getters = {
  getMetricsByLayerAndType: state => (sensorId, layer, type) => {
    if (state.sensors) {
      const sensor = state.sensors.filter(sensor => sensor.id === sensorId)
      const magnitudes = sensor.magnitudes
        .filter(magnitude => magnitude.layer === layer)
        .filter(magnitude => magnitude.type === type)
      return magnitudes
    }
  }
}

const actions = {
  sensorsLoad({ commit, dispatch }, url) {
    const authHeader = {
      Authorization: 'Bearer ' + localStorage.getItem('token')
    }
    globalAxios
      .get(url, { headers: authHeader })
      .then(response => response.data)
      .then(data => {
        commit('sensorsFetch', data.sensors)
      })
      .catch(error => {
        console.log(error)
        commit('clearAuthData')
      })
  }
}

export default {
  state,
  getters,
  mutations,
  actions
}
