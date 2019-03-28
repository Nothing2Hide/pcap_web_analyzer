<template>
  <v-container>
    <v-layout row wrap>
      <v-flex xs10 offset-xs1 md6 offset-md3 mb-5>
        <v-flex tag="h1" class="headline">Welcome on the PCAP Analysis Platform</v-flex>
        <v-flex>
        <v-layout column>
          <v-flex>
            <br/>
            <p>This platform allows to upload pcap file and check if there is any malicious activity based on a known list of malicious indicators. The accuracy of the detection only depends on the list of malicious indicators, it won't detect any unknown threat.</p>
          </v-flex>
          <v-flex>
            <p>The PCAP file is <i>not saved</i> after the analysis, the only data stored are the malicious indicators if anything malicious is found.</p>
          </v-flex>
          <v-flex>
            <v-btn color="info" to="/start">Start</v-btn>
          </v-flex>
        </v-layout>
      </v-flex>
      </v-flex>
      <v-flex xs10 offset-xs1 md6 offset-md3 >
        <div v-if="pcaps.length > 0">
        <h3>Previously Uploaded Samples</h3>
         <v-data-table
          :headers="headers"
          :items="pcaps"
          class="elevation-1"
        >
          <template v-slot:items="props">
            <td>{{ props.item.created }}</td>
            <td class="text-xs-left"> <v-chip v-if="props.item.result == 'AnalysisResult.MALICIOUS'" color="red" text-color="white">Malicious</v-chip><v-chip v-if="props.item.result == 'AnalysisResult.NOTHING'" color="green" text-color="white">Nothing Found</v-chip><v-chip label v-if="props.item.result == 'AnalysisResult.ERROR'">Error</v-chip></td>
            <td class="text-xs-left"><router-link :to="{name: 'Analysis', params: { id: props.item.id }}">Result</router-link></td>
          </template>
        </v-data-table>
        </div>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  name: 'Home',
  data () {
    return {
      pcaps: [],
      headers: [
        {text: 'Created', value: 'created'},
        {text: 'Result', value: 'result'},
        {text: 'Link', value: 'link'}
      ]
    }
  },
  mounted() {
    this.pcaps = JSON.parse(this.$localStorage.get('pcaps', null))
    if (this.pcaps === null) {
      this.$localStorage.set('pcaps', JSON.stringify([]));
      this.pcaps = []
    }
  }
}
</script>

<style>
</style>
