def withDockerNetwork(Closure inner) {
  try {
    networkId = UUID.randomUUID().toString()
    sh "docker network create ${networkId}"
    inner.call(networkId)
  } finally {
    sh "docker network rm ${networkId}"
  }
}

pipeline {
  agent {label 'main'}
  options {
    timeout(time: 30, unit: 'MINUTES')
  }

  environment {
    REPO_NAME = sh(returnStdout: true, script: 'basename `git remote get-url origin` .git').trim()
    VERSION = sh(returnStdout: true, script: 'grep -Po "^version = \\"\\K([^\\"]+)" workers/pyproject.toml').trim()
    LATEST_AUTHOR = sh(returnStdout: true, script: 'git show -s --pretty=%an').trim()
    LATEST_COMMIT_ID = sh(returnStdout: true, script: 'git describe --tags --long  --always').trim()

    PYTEST_TEST_OPTIONS = ' '
    SNAPSHOT_BRANCH_REGEX = /(^main$)/
    RELEASE_REGEX = /^([0-9]+(\.[0-9]+)*)(-(RC|beta-|alpha-)[0-9]+)?$/
    RELEASE_DEPLOY = false
    SNAPSHOT_DEPLOY = false
    POETRY = 'python -m poetry'
    POETRY_OPTIONS = '--no-ansi --no-interaction'
    // wait for an answer to https://github.com/python-poetry/poetry/issues/1567#issuecomment-800542938
    // POETRY_RUN = 'python -m poetry run --no-ansi --no-interaction'
    POETRY_RUN = 'python -m poetry run'

    WORK_DIR = '/opt/oqt'
    MODULE_DIR = 'workers'
    DATABASE_DIR = 'database'
    POSTGRES_HOST = 'oqt-database'
    POSTGRES_PORT = 5432
  }

  stages {
    stage ('Build') {
      steps {
        script {
          echo REPO_NAME
          echo LATEST_AUTHOR
          echo LATEST_COMMIT_ID

          echo env.BRANCH_NAME
          echo env.BUILD_NUMBER
          echo env.TAG_NAME

          if (!(VERSION ==~ RELEASE_REGEX || VERSION ==~ /.*-SNAPSHOT$/)) {
            echo 'Version:'
            echo VERSION
            error 'The version declaration is invalid. It is neither a release nor a snapshot.'
          }
        }
        script {
          DATABASE = docker.build("oqt-database", "-f ${DATABASE_DIR}/Dockerfile.development ${DATABASE_DIR}")
          WORKERS = docker.build("oqt-workers", "${MODULE_DIR}")
          WORKERS_CI = docker.build("oqt-workers-ci", "-f ${MODULE_DIR}/Dockerfile.continuous-integration ${MODULE_DIR}")
        }
      }
      post {
        failure {
          rocketSend channel: 'jenkinsohsome', emoji: ':sob:' , message: "*${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}. Review the code!" , rawMessage: true
        }
      }
    }

    stage ('Test') {
      steps {
        script {
          withDockerNetwork{ n ->
            DATABASE.withRun("""--network ${n} \
                                --name ${POSTGRES_HOST} \
                                -p ${POSTGRES_PORT} \
                                -e POSTGRES_DB=oqt \
                                -e POSTGRES_USER=oqt \
                                -e POSTGRES_PASSWORD=oqt""") { c ->
              WORKERS_CI.inside("--network ${n} -e POSTGRES_HOST=${POSTGRES_HOST} -e POSTGRES_PORT=${POSTGRES_PORT} -e OQT_DATA_DIR=/data -v ${WORKSPACE}/data:/data") {
                // wait for database to be ready
                timeout(time: 30, unit: 'SECONDS') {
                  sh 'while ! pg_isready --host ${POSTGRES_HOST} --port ${POSTGRES_PORT}; do sleep 5; done'
                }
                // run pytest
                sh 'cd ${WORK_DIR} && VCR_RECORD_MODE=none ${POETRY_RUN} pytest --cov=ohsome_quality_analyst --cov-report=xml tests'
                // replace absolute dir in the coverage file with actually used dir for sonar-scanner
                sh "sed -i \"s#${WORK_DIR}#${WORKSPACE}/${MODULE_DIR}#g\" ${WORK_DIR}/coverage.xml"
                // run static analysis with sonar-scanner
                def scannerHome = tool 'SonarScanner 4';
                withSonarQubeEnv('sonarcloud GIScience/ohsome') {
                  SONAR_CLI_PARAMETER =
                    "-Dsonar.python.coverage.reportPaths=${WORK_DIR}/coverage.xml " +
                    "-Dsonar.projectVersion=${VERSION}"
                  if (env.CHANGE_ID) {
                    SONAR_CLI_PARAMETER += " " +
                      "-Dsonar.pullrequest.key=${env.CHANGE_ID} " +
                      "-Dsonar.pullrequest.branch=${env.CHANGE_BRANCH} " +
                      "-Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                  } else {
                    SONAR_CLI_PARAMETER += " " +
                      "-Dsonar.branch.name=${env.BRANCH_NAME}"
                  }
                  sh "${scannerHome}/bin/sonar-scanner " + SONAR_CLI_PARAMETER
                }
                // run other static code analysis
                sh 'cd ${WORK_DIR} && ${POETRY_RUN} black --check --diff --no-color .'
                sh 'cd ${WORK_DIR} && ${POETRY_RUN} flake8 --count --statistics --config setup.cfg .'
                sh 'cd ${WORK_DIR} && ${POETRY_RUN} isort --check --diff --settings-path setup.cfg .'
              }
            }
          }
        }
      }
      post {
        failure {
          rocketSend channel: 'jenkinsohsome', emoji: ':sob:' , message: "*${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}. Review the code!" , rawMessage: true
        }
      }
    }

    stage ('Check Dependencies') {
      when {
        expression {
          if (currentBuild.number > 1) {
            month_pre = new Date(currentBuild.previousBuild.rawBuild.getStartTimeInMillis())[Calendar.MONTH]
            echo month_pre.toString()
            month_now = new Date(currentBuild.rawBuild.getStartTimeInMillis())[Calendar.MONTH]
            echo month_now.toString()
            return month_pre != month_now
          }
          return false
        }
      }
      steps {
        script {
          WORKERS.inside {
            update_notify = sh(returnStdout: true, script: 'cd ${WORK_DIR} && ${POETRY} update ${POETRY_OPTIONS} --dry-run | tail -n +4 | grep -v ": Skipped " | sort -u').trim()
            echo update_notify
          }
        }
        rocketSend channel: 'jenkinsohsome', emoji: ':wave:' , message: "Check your dependencies in *${REPO_NAME}*. You might have updates: ${update_notify}" , rawMessage: true
      }
      post {
        failure {
          rocketSend channel: 'jenkinsohsome', emoji: ':disappointed:' , message: "Checking for updates in *${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}." , rawMessage: true
        }
      }
    }

    stage ('Encourage') {
      when {
        expression {
          if (currentBuild.number > 1) {
            date_pre = new Date(currentBuild.previousBuild.rawBuild.getStartTimeInMillis()).clearTime()
            echo date_pre.format( 'yyyyMMdd' )
            date_now = new Date(currentBuild.rawBuild.getStartTimeInMillis()).clearTime()
            echo date_now.format( 'yyyyMMdd' )
            return date_pre.numberAwareCompareTo(date_now)<0
          }
          return false
        }
      }
      steps {
        rocketSend channel: 'jenkinsohsome', emoji: ':wink:', message: "Hey, this is just your daily notice that Jenkins is still working for you on *${REPO_NAME}* Branch ${env.BRANCH_NAME}! Happy and for free! Keep it up!" , rawMessage: true
        echo 'pass'
      }
      post {
        failure {
          rocketSend channel: 'jenkinsohsome', emoji: ':disappointed:', message: "Reporting of *${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}." , rawMessage: true
        }
      }
    }

    stage ('Report Status Change') {
      when {
        expression {
          return ((currentBuild.number > 1) && (currentBuild.getPreviousBuild().result == 'FAILURE'))
        }
      }
      steps {
        rocketSend channel: 'jenkinsohsome', emoji: ':sunglasses:', message: "We had some problems, but we are BACK TO NORMAL! Nice debugging: *${REPO_NAME}*-build-nr. ${env.BUILD_NUMBER} *succeeded* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}." , rawMessage: true
        echo 'pass'
      }
      post {
        failure {
          rocketSend channel: 'jenkinsohsome', emoji: ':disappointed:', message: "Reporting of *${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}." , rawMessage: true
        }
      }
    }
  }
}
