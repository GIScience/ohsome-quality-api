pipeline {
    agent { label 'main' }
    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        REPO_NAME = sh(returnStdout: true, script: 'basename `git remote get-url origin` .git').trim()
        VERSION = sh(returnStdout: true, script: 'grep -Po "^version = \\"\\K([^\\"]+)" pyproject.toml').trim()
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

        WORK_DIR = '/opt/oqapi'
        MODULE_DIR = '.'
    }

    stages {
        stage('Build') {
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
                    DOCKER_API = docker.build('oqapi-api', "${MODULE_DIR}")
                    DOCKER_API_CI = docker.build('oqapi-api-ci', "-f ${MODULE_DIR}/Dockerfile.continuous-integration ${MODULE_DIR}")
                }
            }
            post {
                failure {
                  rocket_buildfail()
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    DOCKER_API_CI.inside("""--add-host 'api.ohsome.org:127.0.3.4'""") { // blacklist api.ohsome.org
                        // run pytest
                        sh 'cd ${WORK_DIR} && VCR_RECORD_MODE=none ${POETRY_RUN} pytest --cov=ohsome_quality_api --cov-report=xml tests'
                        // replace absolute dir in the coverage file with actually used dir for sonar-scanner
                        sh "sed -i \"s#${WORK_DIR}#${WORKSPACE}/${MODULE_DIR}#g\" ${WORK_DIR}/coverage.xml"
                        // run static analysis with sonar-scanner
                        def scannerHome = tool 'SonarScanner 4'
                        withSonarQubeEnv('sonarcloud GIScience/ohsome') {
                            SONAR_CLI_PARAMETER =
                "-Dsonar.python.coverage.reportPaths=${WORK_DIR}/coverage.xml " +
                "-Dsonar.projectVersion=${VERSION}"
                            if (env.CHANGE_ID) {
                                SONAR_CLI_PARAMETER += ' ' +
                  "-Dsonar.pullrequest.key=${env.CHANGE_ID} " +
                  "-Dsonar.pullrequest.branch=${env.CHANGE_BRANCH} " +
                  "-Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
              } else {
                                SONAR_CLI_PARAMETER += ' ' +
                  "-Dsonar.branch.name=${env.BRANCH_NAME}"
                            }
                            sh "${scannerHome}/bin/sonar-scanner " + SONAR_CLI_PARAMETER
                        }
                        // run other static code analysis
                        sh 'cd ${WORK_DIR} && ${POETRY_RUN} black --check --diff --no-color .'
                        sh 'cd ${WORK_DIR} && ${POETRY_RUN} ruff .'
                    }
                }
            }
            post {
                failure {
                  rocket_testfail()
                }
            }
        }

        stage('Check Dependencies') {
            when {
                // expression {
                //     if (currentBuild.number > 1) {
                //         month_pre = new Date(currentBuild.previousBuild.rawBuild.getStartTimeInMillis())[Calendar.MONTH]
                //         echo month_pre.toString()
                //         month_now = new Date(currentBuild.rawBuild.getStartTimeInMillis())[Calendar.MONTH]
                //         echo month_now.toString()
                //         return month_pre != month_now
                //     }
                //     return false
                // }
                expression {
                    if (currentBuild.number > 1) {
                        return (((currentBuild.getStartTimeInMillis() - currentBuild.previousBuild.getStartTimeInMillis()) > 2592000000) && (env.BRANCH_NAME ==~ SNAPSHOT_BRANCH_REGEX)) //2592000000 30 days in milliseconds
                    }
                    return false
                    }
            }
            steps {
                script {
                    DOCKER_API.inside {
                        update_notify = sh(returnStdout: true, script: 'cd ${WORK_DIR} && ${POETRY} update ${POETRY_OPTIONS} --dry-run | tail -n +4 | grep -v ": Skipped " | sort -u').trim()
                        echo update_notify
                    }
                }
                rocket_basicsend("Check your dependencies in *${REPO_NAME}*. You might have updates: ${update_notify}")
            }
            post {
                failure {
                    rocket_basicsend("Checking for updates in *${REPO_NAME}*-build nr. ${env.BUILD_NUMBER} *failed* on Branch - ${env.BRANCH_NAME}  (<${env.BUILD_URL}|Open Build in Jenkins>). Latest commit from  ${LATEST_AUTHOR}.")
                }
            }
        }

        stage('Wrapping Up') {
            steps {
                encourage()
                status_change()
            }
        }
    }
}
