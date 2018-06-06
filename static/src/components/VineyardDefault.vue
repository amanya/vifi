<template>
  <div></div>
</template>
<script>
export default {
  name: 'VineyardDefault',
  created() {
    this.$router.replace({ name: 'soil-stats', params: { id: this.$route.params.id } })
  }
}
</script>
