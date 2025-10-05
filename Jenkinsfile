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

        // --- МЕРЖ И РАЗВЕРТЫВАНИЕ ---
        stage('Merge fix into main and deploy') {
            steps {
                // Выполняем мерж и пуш только если тесты прошли
                withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    // Используем GitTool для слияния
                    gitPush(
                        credentialsId: 'github-credentials', 
                        // Слияние fix в main
                        url: "https://github.com/DianaParygina/1LR.git",
                        targetBranch: 'main',
                        sourceBranch: 'fix'
                    )
                }
                echo "Successfully merged 'fix' into 'main' and deployed."
            }
        }
    }
}