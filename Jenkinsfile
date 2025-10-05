pipeline {
    agent any
    
    // Переменные окружения для путей и команд
    environment {
        // Установите правильный путь к pm2.cmd на вашем сервере Jenkins
        PM2_CMD = 'C:\\Users\\Diana\\AppData\\Roaming\\npm\\pm2.cmd'
        // Установите правильный путь к python.exe на вашем сервере Jenkins
        PYTHON_CMD = 'C:\\Program Files\\Python313\\python.exe'
        // Папка, куда склонирован репозиторий (рабочая область Jenkins)
        WORKSPACE = "${env.WORKSPACE}"
        // Ветка для слияния
        TARGET_BRANCH = 'main'
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }
        
        // --- ЗАПУСК BACKEND СЕРВЕРА (Django) ---
        // Теперь Django запускается из корневой папки Workspace
        stage('Start Backend Server') {
            steps {
                bat """
                    call "${PM2_CMD}" delete django   || echo No existing Django process 
                    call "${PM2_CMD}" start "${PYTHON_CMD}" --name "django" -- "manage.py" "runserver" "0.0.0.0:8000" -- --time
                """
            }
        }

        // --- ЗАПУСК FRONTEND СЕРВЕРА (Vue) ---
        stage('Start Frontend Server') {
            steps {
                bat """
                    cd client
                    call "${PM2_CMD}" delete vue   || echo No existing Vue process 
                    call "${PM2_CMD}" start cmd.exe --name "vue" -- "/c" "npm run dev"
                """
                echo "Frontend started in background via PM2"
            }
        }

        // --- ЗАПУСК ТЕСТОВ ---
        // Тесты запускаются из корневой папки Workspace
        stage('Run Tests') {
            steps {
                script {
                    try {
                        bat """
                            "${PYTHON_CMD}" manage.py test dogs 
                        """
                        echo "Tests passed! Proceeding to merge and deploy."
                    } catch (err) {
                        echo "Tests failed! Stopping servers..."
                        
                        // Если тесты упали, останавливаем оба процесса PM2
                        bat """
                            "${PM2_CMD}" delete django   || echo No Django process to delete 
                            "${PM2_CMD}" delete vue      || echo No Vue process to delete
                        """
                        error("Integration tests failed. Servers stopped.")
                    }
                }
            }
        }

       stage('Merge fix into main and sync fix') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN'),
                    string(credentialsId: 'github-email', variable: 'GIT_EMAIL')
                ]) {
                    bat """
                        cd "${TARGET_DIR}"
                        git config user.name "%GIT_USER%"
                        git config user.email "%GIT_EMAIL%"

                        git checkout main
                        git pull --rebase https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main

                        :: Сливаем fix
                        git merge fix

                        git push https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git main

                        :: Теперь синхронизируем fix с main (чтобы обе ветки идентичны)
                        git checkout fix
                        git reset --hard main
                        git push --force https://%GIT_USER%:%GIT_TOKEN%@github.com/DianaParygina/1LR.git fix

                        :: Перезапуск серверов
                        call "${PM2_CMD}" delete django  echo No Django process
                        call "${PM2_CMD}" start "${PYTHON_EXE}" --name django -- manage.py runserver 127.0.0.1:8000

                        call "${PM2_CMD}" delete vue || echo No Vue process
                        call "${PM2_CMD}" start "${CMD}" --name vue -- /c "cd ${TARGET_DIR}\\client && npm run dev"
                    """
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