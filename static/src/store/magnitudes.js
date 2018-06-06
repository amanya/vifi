import globalAxios from 'axios'

const state = {
  magnitudes: []
}

const getters = {
  getMagnitudesByLayer: state => (sensorId, layer) => {
    if (state.magnitudes) {
      return state.magnitudes
        .filter(magnitude => magnitude.sensor_id === sensorId)
        .filter(magnitude => magnitude.layer === layer)
    }
  },
  getMagnitudesByType: state => type => {
    if (state.magnitudes) return state.magnitudes.filter(magnitude => magnitude.type === type)
  }
}

const mutations = {
  magnitudesFetch(state, magnitudes) {
    state.magnitudes = magnitudes
  }
}

const actions = {
  magnitudesLoad({ commit, dispatch }, urls) {
    const authHeader = {
      Authorization: 'Bearer ' + localStorage.getItem('token')
    }
    urls.forEach(function(magnitudesUrl) {
      globalAxios
        .get(magnitudesUrl.url, { headers: authHeader })
        .then(response => response.data)
        .then(data => {
          commit('magnitudesFetch', data.magnitudes)
          dispatch(
            'metricsLoad',
            data.magnitudes.map(function(magnitude, idx) {
              return {
                sensorId: magnitudesUrl.id,
                magnitudeId: magnitude.id,
                url: magnitude.metrics_url
              }
            })
          )
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
