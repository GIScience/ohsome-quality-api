pipeline {
    agent { label 'worker' }
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

        DOCKER_CREDENTIALS_ID = 'DockerHubHeiGITCredentials'
        DOCKER_REPOSITORY = 'heigit/ohsome-quality-api'
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
                    sh 'uv sync --locked --no-editable'
                }
            }
            post {
                failure {
                  rocket_buildfail()
                }
            }
        }

        stage('Test') {
            environment {
                VIRTUAL_ENV="${WORKSPACE}/.venv"
                PATH="${VIRTUAL_ENV}/bin:${PATH}"
            }
            steps {
                script {
                    // run pytest
                    sh 'VCR_RECORD_MODE=none pytest --cov=ohsome_quality_api --cov-report=xml tests'
                    // run static analysis with sonar-scanner
                    def scannerHome = tool 'SonarScanner 4'
                    withSonarQubeEnv('sonarcloud GIScience/ohsome') {
                        SONAR_CLI_PARAMETER =
                            "-Dsonar.python.coverage.reportPaths=${WORKSPACE}/coverage.xml " +
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
                    sh 'ruff format --check --diff .'
                    sh 'ruff check .'
                }
            }
            post {
                failure {
                  rocket_testfail()
                }
            }
        }

        stage('Build and Deploy Image') {
            steps {
                script {
                    docker.withRegistry('', DOCKER_CREDENTIALS_ID) {
                        if (env.BRANCH_NAME ==~ SNAPSHOT_BRANCH_REGEX) {
                            dockerImage = docker.build(DOCKER_REPOSITORY + ':' + env.BRANCH_NAME)
                            dockerImage.push()
                        }
                        if (VERSION ==~ RELEASE_REGEX && env.TAG_NAME ==~ RELEASE_REGEX) {
                            dockerImage = docker.build(DOCKER_REPOSITORY + ':' + VERSION)
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }

        stage('(Re)Deploy Test API') {
            when {
                expression {
                    return env.BRANCH_NAME ==~ SNAPSHOT_BRANCH_REGEX
                }
            }
            steps {
                script {
                    build job: 'oqapi Deployment/main', wait: false
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
