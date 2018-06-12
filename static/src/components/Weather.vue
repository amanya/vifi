<template>
  <div>
    <header>
      <h1 class="title">{{ vineyard.name }}'s weather</h1>
    </header>
  </div>
</template>
<script>
import { mapState } from 'vuex'
export default {
  name: 'Weather',
  computed: {
    ...mapState({
      vineyards: state => state.vineyards.vineyards
    }),
    vineyard() {
      return this.vineyards.filter(vineyard => vineyard.id === parseInt(this.$route.params.id))[0]
    }
  }
}
</script>
