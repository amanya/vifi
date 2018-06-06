import Vue from 'vue'
import Vuex from 'vuex'

import auth from './auth'
import vineyards from './vineyards'
import metrics from './metrics'
import alerts from './alerts'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth,
    vineyards,
    metrics,
    alerts
  }
})
