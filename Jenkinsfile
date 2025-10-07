pipeline {
    agent any

    environment {
        CMD = 'C:\\Windows\\System32\\cmd.exe'
        PM2_CMD = 'C:\\Users\\Diana\\AppData\\Roaming\\npm\\pm2.cmd'
        PYTHON_EXE = 'C:\\Program Files\\Python313\\python.exe'
        TARGET_DIR = 'C:\\Users\\Diana\\OneDrive\\Desktop\\DevOps\\1LR-Server'
    }

    triggers { 
        githubPush() 
    }

    stages {
        stage('Stop Existing Servers') {
            steps {
                bat """
                    "${PM2_CMD}" delete django || echo No Django process to delete
                    "${PM2_CMD}" delete vue || echo No Vue process to delete
                    timeout /t 5 /nobreak > nul
                """
            }
        }

        stage('Update Code') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                    string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                ]) {
                    bat """
                        cd "${TARGET_DIR}"
                        
                        :: Настройка Git
                        git config --global --add safe.directory "${TARGET_DIR}"
                        git config user.name "%GIT_USER%"
                        git config user.email "%GIT_EMAIL%"
                        
                        :: Обновление кода
                        git fetch origin
                        git checkout main
                        git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main
                        
                        :: Обновление зависимостей
                        "${PYTHON_EXE}" -m pip install -r requirements.txt
                        
                        :: Миграции Django
                        "${PYTHON_EXE}" manage.py migrate
                        "${PYTHON_EXE}" manage.py collectstatic --noinput
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                    cd "${TARGET_DIR}"
                    "${PYTHON_EXE}" manage.py test dogs --verbosity=2
                """
            }
        }

        stage('Start Servers') {
            steps {
                script {
                    // Запуск Django с автоматической перезагрузкой
                    bat """
                        cd "${TARGET_DIR}"
                        :: Используем PM2 с watch для отслеживания изменений
                        "${PM2_CMD}" start "${PYTHON_EXE}" --name django --interpreter none --watch manage.py -- manage.py runserver 127.0.0.1:8000
                    """
                    
                    // Ждем запуска бэкенда
                    sleep(10)
                    
                    // Запуск Vue dev server
                    bat """
                        cd "${TARGET_DIR}\\client"
                        :: Устанавливаем зависимости если нужно
                        if not exist node_modules (
                            npm install
                        )
                        :: Запускаем Vue с hot reload
                        "${PM2_CMD}" start "npm" --name vue -- run dev
                    """
                    
                    // Ждем запуска фронтенда
                    sleep(15)
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    // Проверяем, что серверы работают
                    bat """
                        curl -f http://127.0.0.1:8000/api/dogs/ || echo "Backend not responding"
                        curl -f http://127.0.0.1:5173/ || echo "Frontend not responding"
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Сохраняем логи PM2
            bat """
                "${PM2_CMD}" logs --lines 100 > "${env.WORKSPACE}\\pm2_logs.txt"
            """
            archiveArtifacts artifacts: 'pm2_logs.txt', fingerprint: true
        }
        
        success {
            echo "Deployment successful! Servers are running with latest code."
            echo "Backend: http://127.0.0.1:8000/"
            echo "Frontend: http://127.0.0.1:5173/"
        }
        
        failure {
            echo "Deployment failed. Stopping servers..."
            bat """
                "${PM2_CMD}" delete django || echo No Django process
                "${PM2_CMD}" delete vue || echo No Vue process
            """
        }
    }
}