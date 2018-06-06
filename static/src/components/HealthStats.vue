<template>
  <div>
    <h1 class="title">Health stats</h1>
    <h2 class="subtitle">Last updated {{ lastUpdated }}</h2>
    <table class="table is-fullwidth">
      <thead>
        <th>Vineyard</th>
        <th>Oidi (%)</th>
        <th>Mildiu (%)</th>
      </thead>
      <tbody>
        <tr v-for="vineyard in vineyards" :key="vineyard.id">
          <th>{{ vineyard.name }}</th>
          <td>98</td>
          <td>99</td>
        </tr>
      </tbody>
    </table>
    <h2 class="subtitle">Historical stats</h2>
    <div class="columns">
      <div class="column">
        <div class="tile">
          <article class="tile notification is-primary">
            <br/>
            <br/>
            <br/>
            <br/>
            <br/>
            <br/>
          </article>
        </div>
      </div>
      <div class="column">
        <div class="tile">
          <article class="tile notification is-warning">
            <br/>
            <br/>
            <br/>
            <br/>
            <br/>
            <br/>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'HealthStats',
  computed: {
    ...mapState({
      vineyards: state => state.vineyards.vineyards
    }),
    lastUpdated() {
      return new Date()
    }
  }
}
</script>
