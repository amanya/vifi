import globalAxios from 'axios'

export default {
  state: {
    loading: false,
    error: false,
    loaded: false,
    vineyards: [],
    selectedVineyard: {},
    sensorsState: []
  },
  getters: {
    getSelectedVineyard: state => {
      if (state.selectedVineyard) {
        return state.selectedVineyard
      }
    }
  },
  mutations: {
    vineyardsFetchStart(state) {
      state.loading = true
      state.error = false
      state.vineyards = []
      state.loaded = false
    },
    vineyardsFetchSuccess(state, vineyards) {
      state.loading = false
      state.error = false
      state.vineyards = vineyards
      state.loaded = true
    },
    vineyardsFetchError(state) {
      state.loading = false
      state.error = true
      state.vneyards = []
      state.loaded = false
    },
    setSelectedVineyard(state, selectedVineyard) {
      state.selectedVineyard = selectedVineyard
    },
    setSensorsState(state, sensorsState) {
      state.sensorsState = sensorsState
    }
  },
  actions: {
    loadVineyards({ commit, dispatch }) {
      commit('vineyardsFetchStart')
      const authHeader = {
        Authorization: 'Bearer ' + localStorage.getItem('token')
      }
      globalAxios
        .get('/api/v1/vineyards/', { headers: authHeader })
        .then(response => response.data)
        .then(data => commit('vineyardsFetchSuccess', data.vineyards))
        .catch(error => {
          console.log(error)
          commit('vineyardsFetchError')
          commit('clearAuthData')
        })
    },
    setSelectedVineyard({ commit, dispatch }) {
      const selectedVineyard = localStorage.getItem('selectedVineyard') || this.state.vineyards.vineyards[0]
      commit('setSelectedVineyard', selectedVineyard)
    },
    setSensorsState({ commit }) {
      const sensorsState =
        localStorage.getItem('sensorsState') ||
        this.state.vineyards.selectedVineyard.sensors.map((sensor, _) => {
          let layers = { id: sensor.id }
          sensor.magnitudes.forEach(magnitude => {
            layers[magnitude.layer] = true
          })
          return layers
        })
      commit('setSensorsState', sensorsState)
    },
    updateSensorState({ commit }, selectedLayers) {
      const newSensorsState = this.state.vineyards.sensorsState
      const index = newSensorsState.map(ss => ss.id).indexOf(selectedLayers.id)
      newSensorsState.splice(index, 1, selectedLayers)
      commit('setSensorsState', newSensorsState)
    }
  }
}
