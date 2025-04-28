FROM openjdk:21-jdk-slim
ARG JAR_FILE=/build/libs/wowelang_Backend-0.0.1-SNAPSHOT.jar
ARG PROFILES
ARG ENV
COPY ${JAR_FILE} app.jar
ENTRYPOINT ["java", "-Dspring.profiles.active=${PROFILES}", "-Dserver.env=${ENV}", "-jar", "app.jar"]
