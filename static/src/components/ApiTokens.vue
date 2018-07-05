<template>
  <div>
    <h1 class="title">API Tokens</h1>
    <p v-for="apiToken in apiTokens()" :key="apiToken.id">
      {{ apiToken.description }} | {{ apiToken.token }}
    </p>
  </div>
</template>
<script>
import { mapState } from 'vuex'
export default {
  name: 'ApiTokens',
  data() {
    return {
      ...mapState({
        apiTokens: state => state.apiTokens.apiTokens
      })
    }
  },
  created() {
    this.$store.dispatch('fetchApiTokens')
  }
}
</script>
