<template>
  <v-app>
    <v-content>
      <v-container id="container">
        <v-toolbar dark color="primary" app>
          <v-toolbar-title class="headline text-uppercase">
            <router-link to="/" class="toolbar-title">
              <span class="nicelink">PCAP ANALYZER</span>
            </router-link>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn
            flat
            href="https://github.com/Te-k/pcap_web_analyzer"
            target="_blank"
          >
            <span class="mr-2">Latest Release</span>
          </v-btn>
        </v-toolbar>

        <v-content>
          <router-view/>
        </v-content>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  components: {
  },
  data () {
    return {
    }
  },
  mounted() {
  }
}
</script>

<style>
.nicelink {
  color: #fff;
  text-decoration:none;
}
</style>
