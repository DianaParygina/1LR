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
        stage('Start Backend Server') {
            steps {
                bat """
                    cd "${TARGET_DIR}"

                    call "${PM2_CMD}" delete django || echo No existing Django process

                    call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000
                """
            }
        }

        stage('Start Frontend Server') {
            steps {
                bat """
                    cd "${TARGET_DIR}\\client"

                    call "${PM2_CMD}" delete vue || echo No existing Vue process

                    call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"

                    echo Frontend started in background via PM2
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    try {
                        bat """
                            cd "${TARGET_DIR}"
                            "${PYTHON_EXE}" manage.py test dogs
                        """
                        echo "Tests passed! Keeping servers running."
                    } catch (err) {
                        echo "Tests failed! Stopping servers..."

                        bat """
                            "${PM2_CMD}" delete django || echo No Django process to delete
                            "${PM2_CMD}" delete vue || echo No Vue process to delete
                        """
                        error("Integration tests failed. Servers stopped.")
                    }
                }
            }
        }
        
        stage('Merge fix into main and sync fix') {
            when {
                // Запускается, только если коммит был в ветке 'fix'
                branch 'fix' 
            }
            steps {
                script {
                    // Продолжаем, только если предыдущие этапы прошли успешно
                    if (currentBuild.result == null || currentBuild.result == 'SUCCESS') {
                        withCredentials([
                            usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                            string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                        ]) {
                            bat """
                                cd "${TARGET_DIR}"
                                
                                :: 1. Настройка пользователя Git для коммита слияния
                                git config user.name "%GIT_USER%"
                                git config user.email "%GIT_EMAIL%"

                                :: 2. Переключаемся на main, обновляем его
                                git checkout main
                                git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main

                                :: 3. Слияние fix в main с помощью --no-ff
                                :: Если возникнет конфликт, команда завершится ошибкой.
                                git merge fix --no-ff

                                :: 4. Отправляем слитую ветку main на GitHub
                                git push https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main

                                :: 5. Синхронизируем ветку fix с main
                                git checkout fix
                                git reset --hard main
                                git push --force https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git fix

                                :: 6. Перезапуск серверов с новыми изменениями
                                call "${PM2_CMD}" delete django || echo No Django process
                                call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000

                                call "${PM2_CMD}" delete vue || echo No Vue process
                                call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"
                            """
                        }
                    } else {
                        echo "Tests failed. Skipping merge."
                    }
                }
            }
        } 
    }
    
    post {
        success {
            echo "Backend and Frontend are running via PM2!"
            echo "Backend: http://127.0.0.1:8000/"
            echo "Frontend: http://127.0.0.1:5173/"
        }
    }
}