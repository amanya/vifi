<template>
  <nav class="level">
    <div class="level-item" v-for="(values, type, index) in layers" :key="index">
      <div>
      <table class="table">
        <thead>
          <tr>
            <th colspan="2">{{ type }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(value, layer, index) in values" :key="index">
            <th>{{ layer }}</th>
            <td>{{ value }}</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </nav>
</template>

<script>
import globalAxios from 'axios'
export default {
  name: 'SensorModal',
  props: ['sensor'],
  data() {
    return {
      layers: []
    }
  },
  methods: {
    fetchMetrics() {
      const authHeader = {
        Authorization: 'Bearer ' + this.$store.state.auth.idToken
      }
      globalAxios
        .get(`/api/v1/sensors/${this.sensor.id}/last-metrics/`, { headers: authHeader })
        .then(response => response.data)
        .then(data => {
          const layers = {}
          data.forEach(m => {
            const magnitude = this.sensor.magnitudes.filter(i => i.id === m.magnitude_id)[0]
            if (!(magnitude.type in layers)) {
              layers[magnitude.type] = {}
            }
            layers[magnitude.type][magnitude.layer] = m.value
          })
          this.layers = layers
        })
    }
  },
  created() {
    this.fetchMetrics()
  }
}
</script>
