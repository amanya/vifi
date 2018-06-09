<template>
  <section class="section section-padding-large">
    <div class="container">
    <div class="columns">
    <div class="column">
    </div>
    <div class="column is-half">
      <form class="form-signin" @submit.prevent="login">
        <div class="field">
          <div class="notification is-danger" v-if="error">{{ error }}</div>
          <p class="control has-icons-left has-icons-right">
            <input v-model="email" class="input is-large" type="email" placeholder="Email">
            <span class="icon is-large is-left">
              <font-awesome-icon :icon="envelopeIcon" size="xs" />
            </span>
          </p>
        </div>
        <div class="field">
          <p class="control has-icons-left">
            <input v-model="password" class="input is-large" type="password" placeholder="Password">
            <span class="icon is-large is-left">
              <font-awesome-icon :icon="lockIcon" size="xs" />
            </span>
          </p>
        </div>
        <div v-if="loginError" class="notification is-danger">
          Invalid username or password
        </div>
        <div class="field">
          <p class="control">
            <button class="button is-success is-large">
              Login
            </button>
          </p>
        </div>
      </form>
    </div>
    <div class="column">
    </div>
    </div>
    </div>
  </section>
</template>

<script>
import FontAwesomeIcon from '@fortawesome/vue-fontawesome'
import { faLock, faEnvelope } from '@fortawesome/fontawesome-free-solid'

export default {
  name: 'Login',
  components: {
    FontAwesomeIcon
  },
  data() {
    return {
      email: '',
      password: '',
      error: false
    }
  },
  computed: {
    loginError() {
      return this.$store.state.auth.error
    },
    envelopeIcon() {
      return faEnvelope
    },
    lockIcon() {
      return faLock
    }
  },
  methods: {
    login() {
      this.$store.dispatch('login', { email: this.email, password: this.password })
    }
  }
}
</script>

<style lang="css">
</style>
