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
                    
                    :: Передаем команду 'npm run dev' в PM2 через cmd.exe, чтобы обеспечить корректный запуск
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
        
        stage('Merge fix into main and deploy') {
            when { 
                expression { env.BRANCH_NAME?.contains('fix') || env.GIT_BRANCH?.contains('fix') } 
            }
            steps {
                script {
                    if (currentBuild.result == null || currentBuild.result == 'SUCCESS') {
                        withCredentials([
                            usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                            string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                        ]) {
                            bat """
                                :: *** 1. GIT-ОПЕРАЦИИ (ВЫПОЛНЯЮТСЯ В $WORKSPACE - СЛИЯНИЕ И ПУШ) ***
                                
                                :: Настройка пользователя Git
                                git config user.name "%GIT_USER%"
                                git config user.email "%GIT_EMAIL%"

                                :: Переключаемся на main, обновляем его, сливаем fix и пушим
                                git checkout main
                                git pull https://%GIT_USER%:%GIT_TOKEN%@[github.com/DianaParygina/1LR.git](https://github.com/DianaParygina/1LR.git) main
                                git merge origin/fix --no-ff
                                git push https://%GIT_USER%:%GIT_TOKEN%@[github.com/DianaParygina/1LR.git](https://github.com/DianaParygina/1LR.git) main

                                :: Синхронизация fix с обновленным main
                                git checkout fix
                                git reset --hard main
                                git push --force https://%GIT_USER%:%GIT_TOKEN%@[github.com/DianaParygina/1LR.git](https://github.com/DianaParygina/1LR.git) fix
                                
                                :: *** 2. PM2-ОПЕРАЦИИ (ПЕРЕХОД В TARGET_DIR И ОБНОВЛЕНИЕ КОДА) ***
                                
                                :: **КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновление кода в целевой папке**
                                cd "${TARGET_DIR}"
                                git checkout main
                                git pull https://%GIT_USER%:%GIT_TOKEN%@[github.com/DianaParygina/1LR.git](https://github.com/DianaParygina/1LR.git) main

                                :: Перезапуск Django
                                call "${PM2_CMD}" delete django || echo No Django process
                                call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000

                                :: Переход в каталог Vue/Frontend и перезапуск
                                cd "${TARGET_DIR}\\client"
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
            echo "Backend and Frontend are running via PM2 with the latest code!"
            echo "Backend: http://127.0.0.1:8000/"
            echo "Frontend: http://127.0.0.1:5173/"
        }
    }
}