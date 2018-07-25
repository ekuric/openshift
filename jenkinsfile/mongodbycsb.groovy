#!/usr/bin/env groovy

def pipeline_id = env.BUILD_ID
println "Current pipeline job build id is '${pipeline_id}'"
def node_label = 'CCI && ansible-2.3'
def mongodb_ycsb_test = MONGODB_YCSB_TEST.toString().toUpperCase()

// run pgbench scale test
stage ('mongoycsb_scale_test') {
          if ( mongodb_ycsb_test == "TRUE") {
                currentBuild.result = "SUCCESS"
		node('CCI && US') {
                        // get properties file
                        if (fileExists("mongodbycsb.properties")) {
                                println "mongodbycsb.properties... deleting it..."
                                sh "mongodbycsb.properties"
                        }
                        // get properties file - from test location
                        // in SCALE-CI there will be defined PGBENCH_SCALE_TEST_PROPERTY_FILE
                        // for now just keep it as is --

                        // sh "wget https://raw.githubusercontent.com/ekuric/openshift/master/postgresql/pgbench.properties"
                        sh "wget -O mongodbycsb.properties ${MONGOYCSB_PROPERTY_FILE}"
                        sh "cat mongodbycsb.properties"
			def mongodbycsb_scale_test_properties = readProperties file: "mongodbycsb.properties"
                        def MEMORY_LIMIT = mongodbycsb_scale_test_properties['MEMORY_LIMIT']
                        def YCSB_THREADS = mongodbycsb_scale_test_properties['YCSB_THREADS']
                        def JUMP_HOST = mongodbycsb_scale_test_properties['JUMP_HOST']
                        def WORKLOAD = mongodbycsb_scale_test_properties['WORKLOAD']
                        def ITERATIONS = mongodbycsb_scale_test_properties['ITERATIONS']
                        def RECORDCOUNT = mongodbycsb_scale_test_properties['RECORDCOUNT']
                        def OPERATIONCOUNT = mongodbycsb_scale_test_properties['OPERATIONCOUNT']
                        def STORAGECLASS = mongodbycsb_scale_test_properties['STORAGECLASS']
			def VOLUMECAPACITY = mongodbycsb_scale_test_properties['VOLUMECAPACITY']
                        // debug info
                        println "----------USER DEFINED OPTIONS-------------------"
                        println "-------------------------------------------------"
                        println "-------------------------------------------------"
                        println "MEMORY_LIMIT: '${MEMORY_LIMIT}'"
                        println "YCSB_THREADS: '${YCSB_THREADS}'"
                        println "JUMP_HOST: '${JUMP_HOST}'"
                        println "WORKLOAD: '${WORKLOAD}'"
                        println "ITERATIONS: '${ITERATIONS}'"
                        println "RECORDCOUNT: '${RECORDCOUNT}'"
                        println "OPERATIONCOUNT: '${OPERATIONCOUNT}'"
                        println "STORAGECLASS: '${STORAGECLASS}'"
			println "VOLUMECAPACITY:'${VOLUMECAPACITY}'"

                        println "-------------------------------------------------"
                        println "-------------------------------------------------"
                        try {
                           pgbench_build = build job: 'PGBENCH_SCALE_TEST',
                                parameters: [   [$class: 'StringParameterValue', name: 'NAMESPACE', value: NAMESPACE ],
                                                [$class: 'StringParameterValue', name: 'TRANSACTIONS', value: TRANSACTIONS ],
                                                [$class: 'StringParameterValue', name: 'TEMPLATE', value: TEMPLATE ],
                                                [$class: 'StringParameterValue', name: 'VOLUME_CAPACITY',value: VOLUME_CAPACITY ],
                                                [$class: 'StringParameterValue', name: 'MEMORY_LIMIT', value: MEMORY_LIMIT ],
                                                [$class: 'StringParameterValue', name: 'ITERATIONS', value: ITERATIONS ],
                                                [$class: 'StringParameterValue', name: 'MODE', value: MODE ],
                                                [$class: 'StringParameterValue', name: 'CLIENTS', value: CLIENTS ],
                                                [$class: 'StringParameterValue', name: 'THREADS', value: THREADS ],
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

stage ('mongoycsb_scale_test') {
          if ( mongodb_ycsb_test == "TRUE") {
                currentBuild.result = "SUCCESS"
		node('CCI && US') {
                        // get properties file
                        if (fileExists("mongodbycsbblock.properties")) {
                                println "mongodbycsbblock.properties... deleting it..."
                                sh "mongodbycsbblock.properties"
                        }
                        sh "wget -O mongodbycsbblock.properties ${MONGOYCSB_BLOCK_PROPERTY_FILE}"
                        sh "cat mongodbycsbblock.properties"
			def mongodbycsb_scale_test_properties = readProperties file: "mongodbycsbblock.properties"
                        def MEMORY_LIMIT = mongodbycsb_scale_test_properties['MEMORY_LIMIT']
                        def YCSB_THREADS = mongodbycsb_scale_test_properties['YCSB_THREADS']
                        def JUMP_HOST = mongodbycsb_scale_test_properties['JUMP_HOST']
                        def WORKLOAD = mongodbycsb_scale_test_properties['WORKLOAD']
                        def ITERATIONS = mongodbycsb_scale_test_properties['ITERATIONS']
                        def RECORDCOUNT = mongodbycsb_scale_test_properties['RECORDCOUNT']
                        def OPERATIONCOUNT = mongodbycsb_scale_test_properties['OPERATIONCOUNT']
                        def STORAGECLASS = mongodbycsb_scale_test_properties['STORAGECLASS']
			def VOLUMECAPACITY = mongodbycsb_scale_test_properties['VOLUMECAPACITY']
                        // debug info
                        println "----------USER DEFINED OPTIONS-------------------"
                        println "-------------------------------------------------"
                        println "-------------------------------------------------"
                        println "MEMORY_LIMIT: '${MEMORY_LIMIT}'"
                        println "YCSB_THREADS: '${YCSB_THREADS}'"
                        println "JUMP_HOST: '${JUMP_HOST}'"
                        println "WORKLOAD: '${WORKLOAD}'"
                        println "ITERATIONS: '${ITERATIONS}'"
                        println "RECORDCOUNT: '${RECORDCOUNT}'"
                        println "OPERATIONCOUNT: '${OPERATIONCOUNT}'"
                        println "STORAGECLASS: '${STORAGECLASS}'"
			println "VOLUMECAPACITY:'${VOLUMECAPACITY}'"

                        println "-------------------------------------------------"
                        println "-------------------------------------------------"
                        try {
                           pgbench_build = build job: 'PGBENCH_SCALE_TEST',
                                parameters: [   [$class: 'StringParameterValue', name: 'NAMESPACE', value: NAMESPACE ],
                                                [$class: 'StringParameterValue', name: 'TRANSACTIONS', value: TRANSACTIONS ],
                                                [$class: 'StringParameterValue', name: 'TEMPLATE', value: TEMPLATE ],
                                                [$class: 'StringParameterValue', name: 'VOLUME_CAPACITY',value: VOLUME_CAPACITY ],
                                                [$class: 'StringParameterValue', name: 'MEMORY_LIMIT', value: MEMORY_LIMIT ],
                                                [$class: 'StringParameterValue', name: 'ITERATIONS', value: ITERATIONS ],
                                                [$class: 'StringParameterValue', name: 'MODE', value: MODE ],
                                                [$class: 'StringParameterValue', name: 'CLIENTS', value: CLIENTS ],
                                                [$class: 'StringParameterValue', name: 'THREADS', value: THREADS ],
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

