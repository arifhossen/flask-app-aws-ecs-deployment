To use **Ubuntu** for your **EC2 instance** to install **Jenkins** and set up your **CI/CD pipeline** for deploying a **Python Flask app** on **AWS ECS** with **Docker** and **ECR**, you can follow this updated step-by-step guide.

### **Step-by-Step Guide: Install Jenkins on Ubuntu EC2 Instance and Deploy Flask App on ECS**

---

### **Step 1: Launch an EC2 Instance with Ubuntu**

1. **Log in to AWS Console**:
   - Go to the **AWS Management Console** and navigate to **EC2**.

2. **Create a New EC2 Instance**:
   - Click **Launch Instance**.
   - Choose **Ubuntu Server 20.04 LTS** (or later) from the list of available AMIs.
   - Select an **Instance Type** (e.g., t2.micro if eligible for the free tier).
   - Configure instance details (networking, VPC, subnet, etc.).
   - Add **Security Group** rules:
     - **SSH (port 22)** for SSH access.
     - **HTTP (port 80)** to access Jenkins.
     - **TCP (port 8080)** to access Jenkins Web UI.
     - **Ppython flask application to run on custom (port 7881)** 

   - Launch the instance and download the **private key** for SSH access.

3. **Access the EC2 Instance**:
   Once the EC2 instance is running, use **SSH** to connect to it:
   ```bash
   ssh -i your-key.pem ubuntu@<public-ip-of-ec2>
   ```

---

### **Step 2: Install Jenkins on Ubuntu**

1. **Update System Packages**:

   ```bash
   sudo apt update -y
   sudo apt upgrade -y
   ```

2. **Install Java Development Kit (JDK)**:
   
   Jenkins requires Java to run. Install **OpenJDK 11**:
   
   ```bash
   sudo apt install fontconfig openjdk-17-jre
   ```

   Verify the Java installation:
   
   ```bash
   java -version
   ```

3. **Add Jenkins Repository and Install Jenkins**:
   
    Add the Jenkins repository and install Jenkins.
    ```bash
    sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
    echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
    sudo apt-get update
    sudo apt-get install jenkins
    ```

4. **Start Jenkins Service**:
   
   Enable and start Jenkins:
   
   ```bash
   sudo systemctl enable jenkins
   sudo systemctl start jenkins
   ```

5. **Check Jenkins Status**:
   
   Verify that Jenkins is running:
   
   ```bash
   sudo systemctl status jenkins
   ```

6. **Access Jenkins Web Interface**:
   
   Open a browser and go to `http://<public-ip-of-ec2>:8080` to access the Jenkins UI.

7. **Unlock Jenkins**:
   
   - To unlock Jenkins, find the initial admin password:
   
     ```bash
     sudo cat /var/lib/jenkins/secrets/initialAdminPassword
     ```
   
   - Copy the password and paste it into the Jenkins unlock page in your browser.

8. **Install Suggested Plugins**:
   
   Once Jenkins is unlocked, select **Install Suggested Plugins** during the setup process.

---

### **Step 3: Install Docker on Jenkins EC2 Instance**

Jenkins will use **Docker** to build and push images to **Amazon ECR** and deploy to **ECS**.

1. **Install Docker**:
   
   Run the following commands to install Docker on your Ubuntu instance:
   
   ```bash
   sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install docker-ce -y
   ```

2. **Start Docker Service**:
   
   Start and enable Docker to run on boot:
   
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Add Jenkins User to Docker Group**:   

    Add the ubuntu and jenkins users to the Docker group and set permissions.
    
    ```bash
    sudo usermod -aG docker ubuntu
    sudo usermod -aG docker jenkins
    groups jenkins
    sudo chown root:docker /var/run/docker.sock
    sudo chmod 660 /var/run/docker.sock
    sudo systemctl restart jenkins
    sudo systemctl start docker
    sudo systemctl enable docker
    ```

---

### **Step 4: Configure AWS CLI on Jenkins EC2 Instance**

To interact with AWS services such as **ECR** and **ECS**, you need to configure the **AWS CLI**.

1. **Install AWS CLI**:
   
   Install AWS CLI on the EC2 instance:
   
   ```bash
   sudo apt install awscli -y
   ```

2. **Configure AWS CLI**:
   
   Configure AWS CLI with your AWS credentials:
   
   ```bash
   aws configure
   ```

   Enter your **AWS Access Key ID**, **Secret Access Key**, **Default region name** (e.g., `us-east-1`), and **Default output format** (e.g., `json`).

---

### **Step 5: Push the Docker Image to ECR (Elastic Container Registry)**

1. **Create an ECR Repository**:

   - Go to the **ECR** section of AWS Management Console.
   - Click **Create repository** and name it `flask-app`.
   - Leave the default settings and create the repository.

2. **Authenticate Docker to ECR**:

   Use the AWS CLI to authenticate Docker with ECR:

   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
   ```

   Replace `<aws_account_id>` with your AWS account ID.

3. **Tag the Docker Image**:

   Tag your Docker image for ECR:

   ```bash
   docker tag flask-app:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/flask-app:latest
   ```

4. **Push the Image to ECR**:

   Push your Docker image to your ECR repository:

   ```bash
   docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/flask-app:latest
   ```

---

### **Step 6: Set Up ECS Cluster and Task Definition**

1. **Create an ECS Cluster**:
   
   - Go to **ECS** in AWS Console.
   - Click **Create Cluster**.
   - Select **EC2 Linux + Networking** (or **Fargate** if you don’t want to manage EC2 instances) and click **Next Step**.
   - Enter the cluster name (e.g., `flask-cluster`) and create the cluster.

2. **Create a Task Definition**:
   
   - Go to the **Task Definitions** section in ECS.
   - Click **Create new Task Definition**.
   - Select the launch type (e.g., **EC2** or **Fargate**).
   - Define the container using the ECR image URL you pushed earlier.
     - Container name: `flask-app`
     - Image: `<aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/flask-app:latest`
     - Port mappings: `5000:5000`
     - CPU and memory settings: Choose based on your application needs.
   - Save the task definition.

---


### **Step 7: Set Up Jenkins Pipeline for Flask App Deployment**

Now, let’s set up a Jenkins **Pipeline** to automate the process of building and deploying your Flask app.

1. **Create a New Jenkins Pipeline Job**:
   
   - In Jenkins Dashboard, click **New Item**.
   - Select **Pipeline** and name it (e.g., `Flask-App-ECS-Deploy`).
   - Click **OK** to create the job.

2. **Configure GitHub Repository**:
   
   Under **Pipeline**, in the **Definition** section, select **Pipeline script from SCM**.
   - Set **SCM** to **Git**.
   - Enter the **GitHub repository URL** for your Flask app (e.g., `https://github.com/arifhossen/flask-app-aws-ecs-deployment.git`).
   - If your repository is private, add **Credentials** for GitHub access.

3. **Pipeline Script for Jenkins**:
   
   Below is the **Jenkins Pipeline Script** to automate the process:
   
   ```groovy
   pipeline {
       agent any
       
       environment {
           AWS_REGION = 'us-east-1'
           ECR_REPO_URI = '<aws_account_id>.dkr.ecr.${AWS_REGION}.amazonaws.com/flask-app'
           IMAGE_TAG = 'latest'
       }

       stages {
           stage('Checkout') {
               steps {
                   git branch: 'main', url: 'https://github.com/arifhossen/flask-app-aws-ecs-deployment.git'
               }
           }
           
           stage('Build Docker Image') {
               steps {
                   script {
                       sh 'docker build -t ${ECR_REPO_URI}:${IMAGE_TAG} .'
                   }
               }
           }

           stage('Login to ECR') {
               steps {
                   script {
                       sh 'aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}'
                   }
               }
           }

           stage('Push Docker Image to ECR') {
               steps {
                   script {
                       sh 'docker push ${ECR_REPO_URI}:${IMAGE_TAG}'
                   }
               }
           }

           stage('Deploy to ECS') {
               steps {
                   script {
                       sh 'aws ecs update-service --cluster flask-cluster --service flask-service --force-new-deployment --region ${AWS_REGION}'
                   }
               }
           }
       }
   }
   ```

4. **Save and Build the Pipeline**:
   
   - Save the job and click **Build Now** to trigger the pipeline.
   - Jenkins will:
     1. Check out the code from your GitHub repository.
     2. Build the Docker image for your Flask app.
     3. Push the Docker image to ECR.
     4. Trigger a deployment to ECS.

---

### **Step 6: Monitor ECS Deployment and Access Flask App**

1. **Monitor ECS Deployment**:
   
   Go to **Amazon ECS** and check the status of your service (e.g., `flask-service`). Make sure the new Docker image is deployed successfully.

2. **Access Your Flask App**:
   
   - If you're using an **Application Load Balancer (ALB)**, navigate to the ALB DNS name in your browser.
   - If not using an ALB, you can use the **public IP** of the ECS task (Fargate) or the EC2 instance to access your app.

---

### **Conclusion**

This guide walked you through the steps to:
- Install Jenkins on an **Ubuntu EC2 instance**.
- Configure **Docker** and **AWS CLI** for Jenkins.
- Set up a **Jenkins Pipeline** to automate the deployment of your **Flask app** to **Amazon ECS** using **Docker** and **Amazon ECR**.

With this setup, your Flask app is deployed automatically to ECS every time changes are made to the GitHub repository.