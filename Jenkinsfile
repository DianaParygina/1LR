pipeline {
    agent any

    environment {
        // Переменные окружения для путей и команд Windows
        CMD = 'C:\\Windows\\System32\\cmd.exe'
        PM2_CMD = 'C:\\Users\\Diana\\AppData\\Roaming\\npm\\pm2.cmd'
        PYTHON_EXE = 'C:\\Program Files\\Python313\\python.exe'
        // TARGET_DIR — это каталог, где лежат ваши Django/Vue проекты (рабочий сервер)
        TARGET_DIR = 'C:\\Users\\Diana\\OneDrive\\Desktop\\DevOps\\1LR-Server'
    }

    triggers { 
        githubPush() 
    }

    stages {
        stage('Start Backend Server') {
            steps {
                // Серверы запускаются из целевой папки, чтобы быть готовыми к тестам
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
                        // Тесты запускаются из целевой папки
                        bat """
                            cd "${TARGET_DIR}"
                            "${PYTHON_EXE}" manage.py test dogs
                        """
                        echo "Tests passed! Keeping servers running."
                    } catch (err) {
                        echo "Tests failed! Stopping servers..."
                        // Останавливаем серверы при падении тестов
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
                // Этот этап запускается только при пуше в ветку 'fix'
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
                                :: *** ПРЕДВАРИТЕЛЬНАЯ НАСТРОЙКА GIT ДЛЯ СЛУЖБЫ JENKINS ***
                                :: Разрешение проблемы прав доступа (dubious ownership) для целевой папки
                                git config --global --add safe.directory "C:/Users/Diana/OneDrive/Desktop/DevOps/1LR-Server"
                                
                                git config user.name "%GIT_USER%"
                                git config user.email "%GIT_EMAIL%"

                                :: *** 1. GIT-ОПЕРАЦИИ В JENKINS WORKSPACE (СЛИЯНИЕ И PUSH НА GITHUB) ***
                                
                                :: Переключаемся на main, обновляем его, сливаем fix и пушим на GitHub
                                git checkout main
                                git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main
                                git merge origin/fix --no-ff
                                git push https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main

                                :: Синхронизация fix с обновленным main (чтобы ветка fix всегда была чистой)
                                git checkout fix
                                git reset --hard main
                                git push --force https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git fix

                                :: *** 2. ОБНОВЛЕНИЕ КОДА В TARGET_DIR (РАЗВЕРТЫВАНИЕ) ***
                                
                                cd "${TARGET_DIR}"
                                
                                :: Инициализация Git в целевой папке, если она еще не репозиторий
                                if not exist .git (
                                    git init
                                    git remote add origin https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git
                                )

                                :: Скачиваем самый свежий код из обновленной main и принудительно обновляем локальный сервер
                                git fetch
                                git checkout main
                                git pull https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main 

                                :: *** 3. PM2-ОПЕРАЦИИ (ПЕРЕЗАПУСК) ***
                                
                                :: Перезапуск Django с новым кодом
                                call "${PM2_CMD}" delete django || echo No Django process
                                call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000

                                :: Перезапуск Vue с новым кодом
                                cd "${TARGET_DIR}\\client"
                                call "${PM2_CMD}" delete vue || echo No Vue process
                                call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"
                            """
                        }
                    } else {
                        echo "Tests failed. Skipping merge and deployment."
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful. Backend and Frontend are running via PM2 with the latest code!"
            echo "Backend: http://127.0.0.1:8000/"
            echo "Frontend: http://127.0.0.1:5173/"
        }
    }
}