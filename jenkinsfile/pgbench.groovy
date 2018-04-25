#!/usr/bin/env groovy

def pipeline_id = env.BUILD_ID
println "Current pipeline job build id is '${pipeline_id}'"
def node_label = 'CCI && ansible-2.3'
def pgbench_test = PGBENCH_TEST.toString().toUpperCase()

// run pgbench scale test
stage ('pgbench_scale_test') {
          if ( pgbench_test == "TRUE") {
                currentBuild.result = "SUCCESS"
		node('CCI && US') {
                        // get properties file
                        if (fileExists("pgbench.properties")) {
                                println "pgbench_scale_test.properties file exist... deleting it..."
                                sh "rm pgbench.properties"
                        }
                        // get properties file - from test location 
                        // in SCALE-CI there will be defined PGBENCH_SCALE_TEST_PROPERTY_FILE 
                        // for now just keep it as is -- 

                        sh "wget https://raw.githubusercontent.com/ekuric/openshift/master/postgresql/pgbench.properties"
                        // sh "wget ${PGBENCH_SCALE_TEST_PROPERTY_FILE}"
                        sh "cat pgbench.properties"
			def pgbench_scale_test_properties = readProperties file: "pgbench.properties"
                        def namespace = pgbench_scale_test_properties['namespace']
                        def transactions = pgbench_scale_test_properties['transactions']
                        def template = pgbench_scale_test_properties['template']
			def vgsize = pgbench_scale_test_properties['vgsize']
			def memsize = pgbench_scale_test_properties['memsize']
			def iterations = pgbench_scale_test_properties['iterations']
			def mode = pgbench_scale_test_properties['mode']
			def clients = pgbench_scale_test_properties['clients']
			def scaling = pgbench_scale_test_properties['scaling']
                        def pbenchconfig = pgbench_scale_test_properties['pbenchconfig']
                        def storageclass = pgbench_scale_test_properties['storageclass']


			
                        // debug info
			println "----------USER DEFINED OPTIONS-------------------"
			println "-------------------------------------------------"
			println "-------------------------------------------------"
                        println "NAMESPACE: '${namespace}'"
                        println "TRANSACTIONS: '${transactions}'"
                        println "TEMPLATE: '${template}'"
			println "VGSIZE: '${vgsize}'"
			println "MEMSIZE: '${memsize}'"
			println "ITERATIONS: '${iterations}'"
			println "MODE: '${mode}'"
			println "CLIENTS: '${clients}'"
			println "SCALING: '${scaling}'"
                        println "PBENCHCONFIG: '${pbenchconfig}'"
                        println "STORAGECLASS: '${storageclass}'" 

	                println "-------------------------------------------------"
			println "-------------------------------------------------"


                        // Runing pgbench stress test
                        // PGBENCH_SCALE_TEST is actually name of jenkins job - it must be configured in advance 
                        try {
                           pgbench_build = build job: 'PGBENCH_SCALE_TEST',
                                parameters: [   [$class: 'LabelParameterValue', name: 'node', label: node_label ], 
                                                [$class: 'StringParameterValue', name: 'NAMESPACE', value: namespace ],
                                                [$class: 'StringParameterValue', name: 'TRANSACTIONS', value: transactions ],
                                                [$class: 'StringParameterValue', name: 'TEMPLATE', value: template ],
                                                [$class: 'StringParameterValue', name: 'VGSIZE',value: vgsize],
                                                [$class: 'StringParameterValue', name: 'MEMSIZE', value: memsize], 
                                                [$class: 'StringParameterValue', name: 'ITERATIONS', value: iterations],
                                                [$class: 'StringParameterValue', name: 'MODE', value: mode],
                                                [$class: 'StringParameterValue', name: 'CLIENTS', value: clients],
                                                [$class: 'StringParameterValue', name: 'SCALING', value: scaling], 
                                                [$class: 'StringParameterValue', name: 'PBENCHCONFIG', value: pbenchconfig],
                                                [$class: 'StringParameterValue', name: 'STORAGECLASS', value: storageclass]]
                        } catch ( Exception e) {
                        echo "PGBENCH_SCALE_TEST Job failed with the following error: "
                        echo "${e.getMessage()}"
			     echo "Sending an email"
                        mail(
                                to: 'ekuric@redhat.com',
                                subject: 'pgbench-scale-test job failed',
                                body: """\
                                        Encoutered an error while running the pgbench-scale-test job: ${e.getMessage()}\n\n
                                        Jenkins job: ${env.BUILD_URL}
                        """)
                        currentBuild.result = "FAILURE"
                        sh "exit 1"
                        }
                       // println "PGBENCH_SCALE_TEST build ${nodevertical_build.getNumber()} completed successfully"
                }
        }
}
