<template>
  <v-container fluid>
    <v-layout row>
        <v-flex xs12 md6 offset-md3>
          <div v-if="status != 'AnalysisStatus.DONE'">
            <p>analysis in progress</p>
                <v-progress-circular
                  :size="50"
                  color="primary"
                  indeterminate
                ></v-progress-circular>
          </div>
          <div v-if="status == 'AnalysisStatus.DONE'">
            <div v-if="result == 'AnalysisResult.NOTHING'">
              <v-card class="elevation-12">
                <v-toolbar dark color="success">
                  <v-toolbar-title>Nothing Found</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                  <br/>
                  <p>No connection to known malicious infrastructure was found.</p>
                  <p>Upload Date: {{created}}</p>
                  <v-btn color="info" to="/start">Analyze a New File</v-btn>
                </v-card-text>
              </v-card>
            </div>
            <div v-if="result == 'AnalysisResult.MALICIOUS'">
              <v-card class="elevation-12">
                <v-toolbar dark color="error">
                  <v-toolbar-title>Malicious Activity Identified</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                    <br/>
                    <p>Several malicious indicators were found:</p>
                    <ul id="example-1">
                      <li v-for="item in alerts" :key="item.indicator">
                          <i>{{ item.indicator }}</i> - {{ item.event }}
                      </li>
                    </ul>
                    <v-btn color="info" to="/start">Analyze a New File</v-btn>
                </v-card-text>
              </v-card>
            </div>
            <div v-if="result == 'AnalysisResult.ERROR'">
              <v-card class="elevation-12">
                <v-toolbar dark color="warning">
                  <v-toolbar-title>A Weird Error Happened</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                  <br/>
                  <p>We are sorry, an unexpected error happened during the analysis :(. The pcap file was still deleted but impossible to tell you if anything was found or not.</p>
                  <v-btn color="info" to="/start">Analyze a New File</v-btn>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </v-flex>
      </v-layout>
  </v-container>
</template>

<script>
import * as axios from 'axios'
export default {
  name: 'Analysis',
  data () {
    return {
      uid: null,
      status: null,
      result: null,
      created: '',
      alerts: []
    }
  },
  methods: {
    update () {
      axios
        .get('/analysis/' + this.uid)
        .then((response) => {
          this.status = response['data']['status']
          this.result = response['data']['result']
          this.alerts = response['data']['alerts']
          this.created = response['data']['created']
          if (this.status != 'AnalysisStatus.DONE') {
            setTimeout(this.update, 2000);
          }
        }
        )
    }
  },
  mounted () {
    this.uid = this.$route.params.id
    this.update()
  }
}
</script>
<style>
</style>
