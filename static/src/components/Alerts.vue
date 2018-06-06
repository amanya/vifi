<template>
  <div>
    <h1 class="title">Alerts</h1>
    <div class="field">
      <label class="checkbox">
        <input type="checkbox" @click="showUnacknowledged = !showUnacknowledged">
        Show unacknowledged
      </label>
    </div>
    <div v-if="unAckAlerts || showUnacknowledged">
      <div v-if="!alert.acknowledged || showUnacknowledged" v-for="alert in alerts()" :key="alert.id" class="notification" :class="levels[alert.priority]">
        <button class="delete" aria-label="delete" @click="acknowledge($event, alert.id)"></button>
        <p v-html="alert.content"></p>
        <nav class="level">
          <div class="level-left">
            <div class="level-item">
              <strong>{{ alert.origin }}</strong>
            </div>
          </div>
          <div class="level-right">
            <div class="level-item">
              <p>{{ alert.created_at }}</p>
            </div>
          </div>
        </nav>
      </div>
    </div>
    <div v-else>
      <h2 class="subtitle">No alerts, hooray!</h2>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Alerts',
  data() {
    return {
      ...mapState({
        alerts: state => state.alerts.alerts
      }),
      levels: {
        Info: 'is-info',
        Warning: 'is-warning',
        Danger: 'is-danger'
      },
      showUnacknowledged: false
    }
  },
  computed: {
    ...mapGetters({
      unAckAlerts: 'unAckAlerts'
    })
  },
  methods: {
    acknowledge(event, id) {
      this.$store.dispatch('acknowledge', id)
    },
    xshowUnacknowledged(event, state) {
      this.showUnacknowledged = !state
    }
  },
  created() {
    this.$store.dispatch('fetchAlerts')
  }
}
</script>
