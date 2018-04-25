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
                        def NAMESPACE = pgbench_scale_test_properties['NAMESPACE']
                        def TRANSACTIONS = pgbench_scale_test_properties['TRANSACTIONS']
                        def TEMPLATE = pgbench_scale_test_properties['TEMPLATE']
			def VGSIZE = pgbench_scale_test_properties['VGSIZE']
			def MEMSIZE = pgbench_scale_test_properties['MEMSIZE']
			def ITERATIONS = pgbench_scale_test_properties['ITERATIONS']
			def MODE = pgbench_scale_test_properties['MODE']
			def CLIENTS = pgbench_scale_test_properties['CLIENTS']
			def SCALING = pgbench_scale_test_properties['SCALING']
                        def PBENCHCONFIG = pgbench_scale_test_properties['PBENCHCONFIG']
                        def STORAGECLASS = pgbench_scale_test_properties['STORAGECLASS']


			
                        // debug info
			println "----------USER DEFINED OPTIONS-------------------"
			println "-------------------------------------------------"
			println "-------------------------------------------------"
                        println "NAMESPACE: '${NAMESPACE}'"
                        println "TRANSACTIONS: '${TRANSACTIONS}'"
                        println "TEMPLATE: '${TEMPLATE}'"
			println "VGSIZE: '${VGSIZE}'"
			println "MEMSIZE: '${MEMSIZE}'"
			println "ITERATIONS: '${ITERATIONS}'"
			println "MODE: '${MODE}'"
			println "CLIENTS: '${CLIENTS}'"
			println "SCALING: '${SCALING}'"
                        println "PBENCHCONFIG: '${PBENCHCONFIG}'"
                        println "STORAGECLASS: '${STORAGECLASS}'" 

	                println "-------------------------------------------------"
			println "-------------------------------------------------"


                        // Runing pgbench stress test
                        // PGBENCH_SCALE_TEST is actually name of jenkins job - it must be configured in advance 
			// [$class: 'LabelParameterValue', name: 'node', label: node_label ], 
                        try {
                           pgbench_build = build job: 'PGBENCH_SCALE_TEST',
                                parameters: [    
                                                [$class: 'StringParameterValue', name: 'NAMESPACE', value: NAMESPACE ],
                                                [$class: 'StringParameterValue', name: 'TRANSACTIONS', value: TRANSACTIONS ],
                                                [$class: 'StringParameterValue', name: 'TEMPLATE', value: TEMPLATE ],
                                                [$class: 'StringParameterValue', name: 'VGSIZE',value: VGSIZE ],
                                                [$class: 'StringParameterValue', name: 'MEMSIZE', value: MEMSIZE ], 
                                                [$class: 'StringParameterValue', name: 'ITERATIONS', value: ITERATIONS ],
                                                [$class: 'StringParameterValue', name: 'MODE', value: MODE ],
                                                [$class: 'StringParameterValue', name: 'CLIENTS', value: CLIENTS ],
                                                [$class: 'StringParameterValue', name: 'SCALING', value: SCALING ], 
                                                [$class: 'StringParameterValue', name: 'PBENCHCONFIG', value: PBENCHCONFIG ],
                                                [$class: 'StringParameterValue', name: 'STORAGECLASS', value: STORAGECLASS ]]
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
                        println "PGBENCH_SCALE_TEST build ${pgbench_build.getNumber()} completed successfully"
                }
        }
}
